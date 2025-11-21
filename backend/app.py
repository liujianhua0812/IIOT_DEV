import os
import mimetypes
import uuid
import requests
import secrets
from datetime import datetime, timezone, date
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from sqlalchemy import func, or_
from sqlalchemy.exc import OperationalError, DatabaseError
from database import (
    get_db,
    Device,
    User,
    DeviceType,
    DeviceTypeParameter,
    DeviceParameterValue,
    Application,
    DeviceTopology,
    VideoStream,
    LaptopLabelType,
    ProductType,
    ProductionOrder,
    ProductionProduct,
    TK_Positions,
)
from sqlalchemy.orm import joinedload
from config import MODE
from simulation import create_simulator

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}

# 简单的 token 存储（生产环境应使用 Redis 或数据库）
token_store = {}


def normalize_order_products(db):
    """确保每个订单的产品数量与计划量一致，并全部回到 scheduled 状态"""
    created = deleted = updated = 0
    orders = db.query(ProductionOrder).all()
    for order in orders:
        quantity = max(0, order.quantity or 0)
        products = (
            db.query(ProductionProduct)
            .filter(ProductionProduct.order_id == order.id)
            .order_by(ProductionProduct.id.asc())
            .all()
        )
        kept = products[:quantity]
        extras = products[quantity:]
        
        for product in kept:
            if (
                product.status != "scheduled"
                or product.produced_at is not None
                or product.produced_end is not None
            ):
                product.status = "scheduled"
                product.product_type_id = product.product_type_id or order.product_type_id
                product.produced_at = None
                product.produced_end = None
                product.updated_at = datetime.now(timezone.utc)
                updated += 1
        
        for product in extras:
            db.delete(product)
            deleted += 1
        
        existing_count = len(kept)
        for idx in range(existing_count, quantity):
            serial = f"{order.product_code or 'PRD'}-{order.order_code or order.id}-{idx + 1:04d}-{uuid.uuid4().hex[:6].upper()}"
            new_product = ProductionProduct(
                serial_number=serial,
                order_id=order.id,
                product_type_id=order.product_type_id,
                status="scheduled",
                produced_at=None,
                produced_end=None,
                description=f"初始化产品 {serial}",
            )
            db.add(new_product)
            created += 1
    
    return {"created": created, "deleted": deleted, "updated": updated}


def reset_orders_and_products(db, *, log_prefix="重置"):
    """统一清空历史模拟数据，确保所有订单/产品回到初始状态"""
    from datetime import datetime, timezone

    orders_reset = (
        db.query(ProductionOrder)
        .filter(ProductionOrder.status.in_(["in_progress", "completed"]))
        .update(
            {
                ProductionOrder.status: "scheduled",
                ProductionOrder.updated_at: datetime.now(timezone.utc),
            },
            synchronize_session=False,
        )
    )

    # 将所有产品都重置为 scheduled，清空历史时间戳
    products_reset = (
        db.query(ProductionProduct)
        .update(
            {
                ProductionProduct.status: "scheduled",
                ProductionProduct.product_type_id: ProductionProduct.product_type_id,
                ProductionProduct.produced_at: None,
                ProductionProduct.produced_end: None,
                ProductionProduct.updated_at: datetime.now(timezone.utc),
            },
            synchronize_session=False,
        )
    )

    normalize_stats = normalize_order_products(db)
    db.commit()

    remaining_non_scheduled = (
        db.query(ProductionProduct)
        .filter(
            or_(
                ProductionProduct.status != "scheduled",
                ProductionProduct.status.is_(None),
            )
        )
        .count()
    )

    if orders_reset > 0 or products_reset > 0:
        print(
            f"{log_prefix}：重置订单 {orders_reset} 个，产品 {products_reset} 条为 scheduled"
        )
    if normalize_stats:
        print(
            f"{log_prefix}：规范化产品 -> 新增 {normalize_stats['created']} 条，"
            f"删除 {normalize_stats['deleted']} 条，重置 {normalize_stats['updated']} 条"
        )
    if remaining_non_scheduled > 0:
        print(
            f"警告：{log_prefix} 后仍有 {remaining_non_scheduled} 条产品不是 scheduled 状态"
        )

    return {
        "orders_reset": orders_reset,
        "products_reset": products_reset,
        "normalize_stats": normalize_stats,
        "remaining": remaining_non_scheduled,
    }


def ensure_tk_positions_table():
    """确保 tk_positions 表存在，如果不存在则创建"""
    try:
        from sqlalchemy import inspect
        db = next(get_db())
        inspector = inspect(db.bind)
        if "tk_positions" not in inspector.get_table_names():
            TK_Positions.__table__.create(db.bind, checkfirst=True)
            print("✓ tk_positions 表已自动创建")
        db.close()
    except Exception as e:
        print(f"⚠ 检查/创建 tk_positions 表时出错: {e}")


def create_app() -> Flask:
    app = Flask(__name__)
    
    # Initialize SocketIO
    if MODE != "production":
        allowed_origins_for_socketio = "*"
    else:
        default_origins_socketio = "http://166.111.80.127:10061,http://166.111.80.127:10062,http://166.111.80.127:10063,http://166.111.80.127:10064,http://166.111.80.127:10065,http://166.111.80.127:10066,http://localhost:10061,http://localhost:10062,http://localhost:10063,http://localhost:10064,http://localhost:10065,http://localhost:10066"
        cors_origins_env = os.getenv("CORS_ORIGINS", default_origins_socketio)
        allowed_origins_for_socketio = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    socketio = SocketIO(app, cors_allowed_origins=allowed_origins_for_socketio, async_mode='threading')
    app.socketio = socketio
    
    try:
        app.production_simulator = create_simulator()
        # Set WebSocket callback for simulator
        if app.production_simulator:
            def websocket_push(event):
                # Broadcast to all connected clients immediately
                # In Flask-SocketIO, emit without room parameter broadcasts to all clients in the namespace
                try:
                    socketio.emit('simulation_event', event, namespace='/simulation')
                    print(f"WebSocket event sent: {event.get('stage', 'unknown')} - {event.get('message', '')[:50]}")
                except Exception as e:
                    print(f"Error sending WebSocket event: {e}")
            app.production_simulator.set_websocket_callback(websocket_push)
    except Exception as e:
        print(f"生产模拟器启动失败: {e}")
        app.production_simulator = None
    
    # 根据运行模式配置 CORS
    if MODE == "production":
        # 部署模式：限制跨域来源
        default_origins = "http://166.111.80.127:10061,http://166.111.80.127:10062,http://166.111.80.127:10063,http://166.111.80.127:10064,http://166.111.80.127:10065,http://166.111.80.127:10066,http://localhost:10061,http://localhost:10062,http://localhost:10063,http://localhost:10064,http://localhost:10065,http://localhost:10066"
        allowed_origins = os.getenv("CORS_ORIGINS", default_origins).split(",")
        # 清理空白字符
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        CORS(app, 
             resources={
                 r"/api/*": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/map/*": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/intersections": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/intersections/*": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/video-streams/*": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/health": {"origins": "*"}
             },
             supports_credentials=True,
             automatic_options=True)
        print(f"CORS 允许的来源: {allowed_origins}")
    else:
        # 开发模式：允许所有来源，包括所有前端项目的端口
        CORS(app, 
             resources={
                 r"/api/*": {
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/map/*": {
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/intersections": {
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/intersections/*": {
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/video-streams/*": {
                     "origins": "*",
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                     "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                     "expose_headers": ["Content-Type"],
                     "supports_credentials": True,
                     "max_age": 3600
                 },
                 r"/health": {"origins": "*"}
             },
             supports_credentials=True,
             automatic_options=True)

    register_routes(app)
    
    # 确保 tk_positions 表存在
    ensure_tk_positions_table()

    return app


def register_routes(app: Flask) -> None:
    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/api/home/overview")
    def home_overview():
        db = next(get_db())
        try:
            application = (
                db.query(Application)
                .filter(
                    (Application.english_name == 'LenovoFMS') |
                    (Application.name == 'LenovoFMS') |
                    (Application.name.like('%LenovoFMS%'))
                )
                .order_by(Application.id.asc())
                .first()
            )

            device_count = 0
            if application:
                device_count = (
                    db.query(Device)
                    .filter(Device.application_id == application.id)
                    .count()
                )

            # 1. 支持标签类型：统计表的总记录数
            label_type_query = db.query(LaptopLabelType)
            if application:
                label_type_query = label_type_query.filter(
                    (LaptopLabelType.application_id == application.id) |
                    (LaptopLabelType.application_id.is_(None))
                )
            label_type_count = label_type_query.count()

            # 2. 支持笔记本型号：固定值 5866
            supported_laptops = 5866

            # 3. 稳定运行天数：从 2025.07.01 到当前时间计算天数
            start_date = date(2025, 7, 1)
            current_date = date.today()
            stable_days = (current_date - start_date).days

            # 4. 已完成订单数：稳定运行天数 * 200 + 当前完成的订单数
            completed_orders_count = (
                db.query(ProductionOrder)
                .filter(ProductionOrder.status == "completed")
                .count()
            )
            completed_orders_total = stable_days * 200 + completed_orders_count

            # 5. 已完成产品数：稳定运行天数 * 200 * 4 + 当前已完成的产品数
            completed_products_count = (
                db.query(ProductionProduct)
                .filter(ProductionProduct.status == "completed")
                .count()
            )
            completed_products_total = stable_days * 200 * 4 + completed_products_count

            # 6. 贴标质检告警数：已完成产品数 * 0.035
            label_qc_alarms = int(completed_products_total * 0.035)

            # 7. 平均节拍：计算已完成产品的平均耗时（秒）
            # 只计算有 produced_at 和 produced_end 的产品
            avg_cycle_time = None
            completed_products_with_times = (
                db.query(ProductionProduct)
                .filter(
                    ProductionProduct.status == "completed",
                    ProductionProduct.produced_at.isnot(None),
                    ProductionProduct.produced_end.isnot(None)
                )
                .all()
            )
            
            if completed_products_with_times:
                total_seconds = 0
                valid_count = 0
                for product in completed_products_with_times:
                    if product.produced_at and product.produced_end:
                        # 计算时间差（秒）
                        time_diff = (product.produced_end - product.produced_at).total_seconds()
                        if time_diff > 0:  # 确保时间差有效
                            total_seconds += time_diff
                            valid_count += 1
                
                if valid_count > 0:
                    avg_cycle_time = round(total_seconds / valid_count, 1)

            overview = {
                "labelTypes": label_type_count,
                "supportedLaptops": supported_laptops,
                "stableDays": stable_days,
                "completedOrders": completed_orders_total,
                "completedProducts": completed_products_total,
                "labelQcAlarms": label_qc_alarms,
                "dailyCycleTime": avg_cycle_time,
                "deviceCount": device_count,
                "modalTypes": 12,
                "securityEvents": 327,
                "dispatchTasks": 95,
            }
            return jsonify(overview)
        except (OperationalError, DatabaseError) as e:
            print(f"数据库连接错误: {e}")
            return jsonify({
                "error": "数据库连接失败",
                "message": "无法连接到数据库服务器，请检查数据库配置和网络连接"
            }), 503
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.get("/api/home/deployments")
    def home_deployments():
        deployments = [
            {
                "name": "华北核心节点",
                "value": [116.4074, 39.9042],
                "devices": 520,
                "status": "运行稳定",
            },
            {
                "name": "华东边缘节点",
                "value": [121.4737, 31.2304],
                "devices": 410,
                "status": "安全巡检中",
            },
            {
                "name": "华南协同中心",
                "value": [113.2644, 23.1291],
                "devices": 360,
                "status": "调度优化中",
            },
            {
                "name": "西南创新节点",
                "value": [104.0665, 30.5728],
                "devices": 290,
                "status": "模型升级",
            },
            {
                "name": "东北安全枢纽",
                "value": [123.4315, 41.8057],
                "devices": 284,
                "status": "防护增强",
            },
        ]
        return jsonify({"deployments": deployments})

    @app.get("/api/devices")
    def get_devices():
        """获取设备列表"""
        try:
            db = next(get_db())
            # 获取查询参数
            page = request.args.get("page", 1, type=int)
            page_size = request.args.get("page_size", 20, type=int)
            status = request.args.get("status", None, type=str)
            search = request.args.get("search", None, type=str)

            # 构建查询，预加载关联数据
            query = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type),
                joinedload(Device.application)
            )

            # 状态筛选
            if status:
                query = query.filter(Device.status == status)

            # 搜索筛选（设备名称或编码）
            if search:
                query = query.filter(
                    (Device.name.ilike(f"%{search}%")) | (Device.code.ilike(f"%{search}%"))
                )

            # 获取总数（需要先克隆查询以避免影响分页）
            total = query.count()

            # 分页
            offset = (page - 1) * page_size
            devices = query.order_by(Device.created_at.desc()).offset(offset).limit(page_size).all()

            # 转换为字典
            devices_data = [device.to_dict() for device in devices]

            return jsonify({
                "devices": devices_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

    @app.get("/api/lenovofms/devices")
    def get_lenovofms_devices():
        """获取 LenovoFMS 系统的设备数据（按工位分组）和拓扑连接"""
        db = next(get_db())
        try:
            
            # 查找 LenovoFMS 应用
            # 优先通过英文名查找，如果没有则通过名称查找
            lenovofms_app = db.query(Application).filter(
                (Application.english_name == 'LenovoFMS') | 
                (Application.name == 'LenovoFMS') |
                (Application.name.like('%LenovoFMS%')) |
                (Application.name.like('%FMS%'))
            ).first()
            
            if not lenovofms_app:
                return jsonify({
                    "error": "未找到 LenovoFMS 应用",
                    "devices": {},
                    "connections": []
                }), 404
            
            # 只查询属于 LenovoFMS 应用的设备
            devices = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters)
            ).filter(Device.application_id == lenovofms_app.id).all()
            
            # 按工位分组
            devices_by_station = {}
            for device in devices:
                # 从 description 中提取工位名称
                station = 'unknown'
                if device.description:
                    if device.description.startswith('工位:'):
                        station = device.description.replace('工位:', '').strip()
                    elif device.description.startswith('工位：'):
                        station = device.description.replace('工位：', '').strip()
                
                # 如果 description 中没有工位信息，尝试从 code 中提取
                if station == 'unknown' and device.code:
                    # 设备 code 格式：type-station-number，如 camera-read-1 -> read
                    parts = device.code.split('-')
                    if len(parts) >= 2:
                        # 检查第二部分是否是已知的工位
                        potential_station = parts[1]
                        if potential_station in ['read', 'label', 'pick', 'qc', 'network']:
                            station = potential_station
                
                if station not in devices_by_station:
                    devices_by_station[station] = []
                
                # 转换为前端格式
                device_dict = {
                    'id': device.code,
                    'name': device.name,
                    'type': device.device_type.code if device.device_type else 'unknown',
                    'station': station,
                    'status': device.status or 'online',
                    'position': {
                        'x': device.position_x or 0,
                        'y': device.position_y or 0
                    },
                    'details': {}
                }
                
                # 添加参数值到 details
                if device.parameter_values:
                    for pv in device.parameter_values:
                        # 将 ip_address 映射回 ip（前端使用）
                        key = 'ip' if pv.param_key == 'ip_address' else pv.param_key
                        device_dict['details'][key] = pv.param_value
                
                devices_by_station[station].append(device_dict)
            
            # 查询设备拓扑连接（只返回属于 LenovoFMS 应用的设备之间的连接）
            from database import DeviceTopology
            # 获取所有 LenovoFMS 设备的 code
            lenovofms_device_codes = {device.code for device in devices}
            
            topologies = db.query(DeviceTopology).all()
            connections = []
            for topology in topologies:
                # 只包含源设备和目标设备都属于 LenovoFMS 应用的连接
                if topology.source_device_code in lenovofms_device_codes and \
                   topology.target_device_code in lenovofms_device_codes:
                    connections.append({
                        'source': topology.source_device_code,
                        'target': topology.target_device_code,
                        'type': topology.connection_type,
                        'description': topology.description
                    })
            
            return jsonify({
                "devices": devices_by_station,
                "connections": connections
            }), 200
        except (OperationalError, DatabaseError) as e:
            print(f"数据库连接错误: {e}")
            return jsonify({
                "error": "数据库连接失败",
                "message": "无法连接到数据库服务器，请检查数据库配置和网络连接",
                "devices": {},
                "connections": []
            }), 503
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取 LenovoFMS 设备失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/api/devices/<int:device_id>")
    def get_device(device_id):
        """获取单个设备详情"""
        try:
            db = next(get_db())
            device = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters),
                joinedload(Device.application)
            ).filter(Device.id == device_id).first()
            
            if not device:
                return jsonify({"error": "设备不存在"}), 404
            
            return jsonify({"device": device.to_dict(include_parameters=True)}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.post("/api/devices")
    def create_device():
        """创建设备"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            # 验证必填字段
            if not data.get("name") or not data.get("code"):
                return jsonify({"error": "设备名称和编码为必填项"}), 400
            
            # 检查设备编码是否已存在
            existing = db.query(Device).filter(Device.code == data["code"]).first()
            if existing:
                return jsonify({"error": f"设备编码 '{data['code']}' 已存在"}), 400
            
            # 如果指定了设备类型，验证设备类型是否存在
            device_type = None
            if data.get("device_type_id"):
                device_type = db.query(DeviceType).filter(DeviceType.id == data["device_type_id"]).first()
                if not device_type:
                    return jsonify({"error": "指定的设备类型不存在"}), 400
            
            # 创建设备
            from datetime import datetime
            device = Device(
                name=data["name"],
                code=data["code"],
                device_type_id=data.get("device_type_id"),
                application_id=data.get("application_id"),
                position_x=data.get("position_x"),
                position_y=data.get("position_y"),
                serial_number=data.get("serial_number", ""),
                longitude=data.get("longitude"),
                latitude=data.get("latitude"),
                status=data.get("status", "在线"),
                health_status=data.get("health_status", "良好"),
                description=data.get("description", ""),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(device)
            db.flush()  # 获取 device.id
            
            # 创建参数值
            if data.get("parameters") and device_type:
                # 重新加载设备以获取设备类型和参数定义
                db.refresh(device)
                device = db.query(Device).options(
                    joinedload(Device.device_type).joinedload(DeviceType.parameters)
                ).filter(Device.id == device.id).first()
                
                if device and device.device_type and device.device_type.parameters:
                    param_definitions = {p.param_key: p for p in device.device_type.parameters}
                    
                    for param_key, param_value in data["parameters"].items():
                        if param_key not in param_definitions:
                            continue
                        
                        param_def = param_definitions[param_key]
                        
                        # 转换参数值
                        try:
                            if param_value is None:
                                str_value = None
                            elif param_def.param_type == 'boolean':
                                str_value = 'true' if param_value else 'false'
                            elif param_def.param_type == 'date':
                                str_value = param_value if isinstance(param_value, str) else str(param_value) if param_value is not None else None
                            elif param_def.param_type == 'number':
                                str_value = None if (param_value is None or param_value == '') else str(param_value)
                            else:
                                str_value = str(param_value) if param_value is not None else None
                        except Exception as e:
                            return jsonify({"error": f"参数 {param_key} 值转换失败: {str(e)}"}), 400
                        
                        # 创建参数值
                        param_value_obj = DeviceParameterValue(
                            device_id=device.id,
                            parameter_id=param_def.id,
                            param_key=param_key,
                            param_value=str_value
                        )
                        db.add(param_value_obj)
            
            db.commit()
            
            # 重新查询设备以获取完整的数据
            device = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters),
                joinedload(Device.application)
            ).filter(Device.id == device.id).first()
            
            return jsonify({
                "message": "设备创建成功",
                "device": device.to_dict(include_parameters=True)
            }), 201
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.put("/api/devices/<int:device_id>")
    def update_device(device_id):
        """更新设备信息"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            device = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters)
            ).filter(Device.id == device_id).first()
            
            if not device:
                return jsonify({"error": "设备不存在"}), 404
            
            # 更新设备基本信息
            from datetime import datetime
            
            # 保存需要更新的字段值（在重新查询前）
            saved_fields = {}
            if "status" in data:
                saved_fields["status"] = data.get("status")
            if "health_status" in data:
                saved_fields["health_status"] = data.get("health_status")
            if "name" in data:
                saved_fields["name"] = data["name"]
            if "code" in data:
                saved_fields["code"] = data["code"]
            if "description" in data:
                saved_fields["description"] = data.get("description")
            
            # 更新基本字段
            if "name" in data:
                device.name = data["name"]
            if "code" in data:
                device.code = data["code"]
            if "device_type_id" in data:
                device.device_type_id = data["device_type_id"]
            if "application_id" in data:
                device.application_id = data.get("application_id")
            if "position_x" in data:
                device.position_x = data.get("position_x")
            if "position_y" in data:
                device.position_y = data.get("position_y")
            if "serial_number" in data:
                device.serial_number = data.get("serial_number")
            if "longitude" in data:
                device.longitude = data.get("longitude")
            if "latitude" in data:
                device.latitude = data.get("latitude")
            if "status" in data:
                device.status = data.get("status")
            if "health_status" in data:
                device.health_status = data.get("health_status")
            if "description" in data:
                device.description = data.get("description")
            
            # 更新 updated_at
            device.updated_at = datetime.utcnow()
            
            # 更新参数值
            existing_params = {}
            if "parameters" in data:
                # 如果设备类型被更新了，需要重新加载设备类型和参数定义
                if "device_type_id" in data:
                    db.flush()  # 刷新当前修改到数据库（不提交）
                    device = db.query(Device).options(
                        joinedload(Device.parameter_values),
                        joinedload(Device.device_type).joinedload(DeviceType.parameters)
                    ).filter(Device.id == device_id).first()
                    
                    # 恢复之前保存的字段值（因为重新查询会覆盖）
                    for field, value in saved_fields.items():
                        setattr(device, field, value)
                    device.updated_at = datetime.utcnow()
                
                if not device.device_type:
                    return jsonify({"error": "设备没有关联设备类型，无法更新参数值"}), 400
                
                if not device.device_type.parameters:
                    return jsonify({"error": "设备类型没有定义参数"}), 400
                
                param_definitions = {p.param_key: p for p in device.device_type.parameters}
                
                # 查询现有的参数值
                existing_params_query = db.query(DeviceParameterValue).filter(
                    DeviceParameterValue.device_id == device.id
                ).all()
                existing_params = {pv.param_key: pv for pv in existing_params_query}
                
                for param_key, param_value in data["parameters"].items():
                    if param_key not in param_definitions:
                        continue
                    
                    param_def = param_definitions[param_key]
                    
                    # 转换参数值
                    try:
                        if param_value is None:
                            str_value = None
                        elif param_def.param_type == 'boolean':
                            str_value = 'true' if param_value else 'false'
                        elif param_def.param_type == 'date':
                            str_value = param_value if isinstance(param_value, str) else str(param_value) if param_value is not None else None
                        elif param_def.param_type == 'number':
                            str_value = None if (param_value is None or param_value == '') else str(param_value)
                        else:
                            str_value = str(param_value) if param_value is not None else None
                    except Exception as e:
                        return jsonify({"error": f"参数 {param_key} 值转换失败: {str(e)}"}), 400
                    
                    # 更新或创建参数值
                    if param_key in existing_params:
                        existing_params[param_key].param_value = str_value
                        existing_params[param_key].updated_at = datetime.utcnow()
                    else:
                        param_value_obj = DeviceParameterValue(
                            device_id=device.id,
                            parameter_id=param_def.id,
                            param_key=param_key,
                            param_value=str_value
                        )
                        db.add(param_value_obj)
                        existing_params[param_key] = param_value_obj
            
            # 提交事务
            db.commit()
            
            # 重新查询设备以获取完整的最新数据
            device = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters),
                joinedload(Device.application)
            ).filter(Device.id == device_id).first()
            
            return jsonify({
                "message": "设备更新成功",
                "device": device.to_dict(include_parameters=True)
            }), 200
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/map/devices")
    def get_tellhow_traffic_devices():
        """获取 TellhowTraffic 应用的设备数据（用于地图可视化）"""
        try:
            db = next(get_db())
            
            # 查找 TellhowTraffic 应用（多种可能的名称）
            tellhowtraffic_app = db.query(Application).filter(
                (Application.english_name.ilike('%TellhowTraffic%')) | 
                (Application.name.ilike('%TellhowTraffic%')) |
                (Application.english_name.ilike('%Tellhow%Traffic%')) |
                (Application.name.ilike('%Tellhow%Traffic%')) |
                (Application.english_name.ilike('%Traffic%')) |
                (Application.name.ilike('%Traffic%'))
            ).first()
            
            if not tellhowtraffic_app:
                # 如果找不到，尝试列出所有应用以便调试
                all_apps = db.query(Application).all()
                app_names = [f"{app.name}({app.english_name})" for app in all_apps]
                return jsonify({
                    "error": "未找到 TellhowTraffic 应用",
                    "devices": [],
                    "intersections": [],
                    "available_apps": app_names,
                    "hint": "请检查数据库中是否存在 TellhowTraffic 应用，或使用 GET /api/applications 查看所有应用"
                }), 404
            
            # 获取查询参数
            intersection_id = request.args.get("intersection_id", None, type=int)
            
            # 查询属于 TellhowTraffic 应用的设备
            devices_query = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type)
            ).filter(Device.application_id == tellhowtraffic_app.id)
            
            # 如果指定了路口ID，可以进一步过滤（这里假设设备有路口关联字段，如果没有则忽略）
            # 注意：如果设备表中没有路口关联字段，这个过滤不会生效
            # 可以根据实际数据库结构调整
            
            devices = devices_query.all()
            
            # 转换设备数据格式
            devices_data = []
            cameras = []
            signal_controllers = []
            switches = []
            guidance_screens = []
            traffic_lights = []
            
            for device in devices:
                # 从参数值中获取 ip_address 和 traffic_light_status
                ip_address = None
                traffic_light_status = None
                if device.parameter_values:
                    for pv in device.parameter_values:
                        if pv.param_key == "ip_address":
                            ip_address = pv.param_value
                        elif pv.param_key == "traffic_light_status":
                            traffic_light_status = pv.param_value
                
                device_dict = {
                    "id": device.id,
                    "code": device.code,
                    "name": device.name,
                    "type": device.device_type.code if device.device_type else None,
                    "device_type": device.device_type.code if device.device_type else None,
                    "status": device.status or "online",
                    "longitude": device.longitude,
                    "latitude": device.latitude,
                    "ip_address": ip_address
                }
                
                # 如果是红绿灯，添加状态信息
                if device.device_type and device.device_type.code == 'traffic_light':
                    device_dict["traffic_light_status"] = traffic_light_status
                
                devices_data.append(device_dict)
                
                # 按设备类型分类
                device_type = device.device_type.code if device.device_type else None
                if device_type == 'camera':
                    cameras.append(device_dict)
                elif device_type == 'traffic_signal_controller':
                    signal_controllers.append(device_dict)
                elif device_type == 'switch':
                    switches.append(device_dict)
                elif device_type == 'traffic_guidance_screen':
                    guidance_screens.append(device_dict)
                elif device_type == 'traffic_light':
                    traffic_lights.append(device_dict)
            
            # 构建返回数据
            # 查询拓扑关系（仅包含返回的设备之间的连接）
            device_codes = [device["code"] for device in devices_data if device.get("code")]
            topologies_data = []
            if device_codes:
                topologies = db.query(DeviceTopology).filter(
                    DeviceTopology.source_device_code.in_(device_codes),
                    DeviceTopology.target_device_code.in_(device_codes)
                ).all()
                topologies_data = [
                    {
                        "id": topology.id,
                        "source_device_code": topology.source_device_code,
                        "target_device_code": topology.target_device_code,
                        "connection_type": topology.connection_type,
                        "description": topology.description
                    }
                    for topology in topologies
                ]
            
            result = {
                "devices": devices_data,
                "cameras": cameras,
                "signal_controllers": signal_controllers,
                "switches": switches,
                "guidance_screens": guidance_screens,
                "traffic_lights": traffic_lights,
                "topologies": topologies_data
            }
            
            # 如果指定了路口ID，返回该路口的详细信息
            if intersection_id:
                # 这里假设有路口表，如果没有则返回空
                # 可以根据实际数据库结构调整
                # 暂时返回一个模拟的路口数据
                result["intersection"] = {
                    "id": intersection_id,
                    "name": f"路口 {intersection_id}",
                    "longitude": 112.927176,
                    "latitude": 27.87076,
                    "status": "normal"
                }
            else:
                # 返回所有路口（如果有路口表的话）
                # 暂时返回空数组，可以根据实际需求添加
                result["intersections"] = []
            
            return jsonify(result), 200
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取 TellhowTraffic 设备失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/video-streams/device/<int:device_id>")
    def get_device_video_stream(device_id):
        """获取设备的视频流"""
        try:
            db = next(get_db())
            stream = db.query(VideoStream).filter(
                VideoStream.device_id == device_id,
                VideoStream.status == 'active'
            ).first()
            
            if not stream:
                return jsonify({
                    "error": "该设备暂无视频流"
                }), 404
            
            return jsonify(stream.to_dict()), 200
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取设备视频流失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/video-streams/stream/<int:stream_id>")
    def stream_video(stream_id):
        """流式传输视频文件"""
        try:
            db = next(get_db())
            stream = db.query(VideoStream).filter(VideoStream.id == stream_id).first()
            
            if not stream:
                return jsonify({"error": "视频流不存在"}), 404
            
            # 处理文件路径（支持相对路径和绝对路径）
            file_path = stream.file_path
            if not file_path:
                return jsonify({"error": "视频文件路径未设置"}), 400
            
            # 获取项目根目录（backend的父目录）
            PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            if not os.path.isabs(file_path):
                # 如果是相对路径，转换为绝对路径
                if file_path.startswith('./'):
                    file_path = os.path.join(PROJECT_ROOT, file_path[2:])
                else:
                    file_path = os.path.join(PROJECT_ROOT, file_path)
            
            if not os.path.exists(file_path):
                return jsonify({"error": f"视频文件不存在: {file_path}"}), 404
            
            # 根据文件扩展名确定MIME类型
            file_ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.ts': 'video/mp2t',
                '.mp4': 'video/mp4',
                '.m3u8': 'application/vnd.apple.mpegurl',
                '.m4s': 'video/iso.segment'
            }
            content_type = mime_types.get(file_ext, 'video/mp4')
            
            # 如果是.m3u8文件，返回HLS播放列表
            if file_ext == '.m3u8':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return Response(
                    content,
                    mimetype=content_type,
                    headers={
                        'Cache-Control': 'no-cache',
                        'Access-Control-Allow-Origin': '*'
                    }
                )
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            
            # 获取Range请求头（支持视频流式播放）
            range_header = request.headers.get('Range', None)
            
            if range_header:
                # 解析Range头
                byte_start = 0
                byte_end = file_size - 1
                
                # Range格式: bytes=start-end
                if '=' in range_header:
                    ranges = range_header.split('=')[1]
                    if '-' in ranges:
                        start_str, end_str = ranges.split('-', 1)
                        if start_str:
                            byte_start = int(start_str)
                        if end_str:
                            byte_end = int(end_str)
                
                # 确保范围有效
                byte_start = max(0, byte_start)
                byte_end = min(file_size - 1, byte_end)
                
                if byte_start > byte_end:
                    return Response('Range Not Satisfiable', status=416)
                
                content_length = byte_end - byte_start + 1
                
                def generate():
                    with open(file_path, 'rb') as f:
                        f.seek(byte_start)
                        remaining = content_length
                        while remaining:
                            chunk_size = min(8192, remaining)
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk
                
                return Response(
                    generate(),
                    status=206,  # Partial Content
                    headers={
                        'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(content_length),
                        'Content-Type': content_type,
                        'Cache-Control': 'no-cache',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
                        'Access-Control-Allow-Headers': 'Range, Content-Type'
                    },
                    mimetype=content_type
                )
            else:
                # 没有Range头，返回整个文件（但视频播放通常需要Range支持）
                # 为了更好的兼容性，我们仍然返回支持Range的响应
                def generate_full():
                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            yield chunk
                
                return Response(
                    generate_full(),
                    status=200,
                    headers={
                        'Content-Type': content_type,
                        'Content-Length': str(file_size),
                        'Accept-Ranges': 'bytes',
                        'Cache-Control': 'no-cache',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
                        'Access-Control-Allow-Headers': 'Range, Content-Type'
                    },
                    mimetype=content_type
                )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"流式传输视频失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/api/map/china-geojson")
    def get_china_geojson():
        """代理获取中国地图 GeoJSON 数据"""
        try:
            # 尝试从阿里云获取地图数据
            url = "https://geo.datav.aliyun.com/areas/bound/geojson?code=100000_full"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://datav.aliyun.com/"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 验证响应内容
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                raise ValueError(f"响应不是 JSON 格式: {content_type}")
            
            geo_json = response.json()
            
            # 验证是否是有效的 GeoJSON
            if not geo_json or not isinstance(geo_json, dict) or "type" not in geo_json:
                raise ValueError("无效的 GeoJSON 数据")
            
            return jsonify(geo_json)
        except requests.exceptions.RequestException as e:
            # 如果请求失败，返回错误信息
            return jsonify({
                "error": "无法加载地图数据",
                "message": str(e),
                "fallback": True
            }), 503
        except (ValueError, KeyError) as e:
            # 如果数据格式错误
            return jsonify({
                "error": "地图数据格式错误",
                "message": str(e),
                "fallback": True
            }), 500

    @app.post("/api/auth/register")
    def register_user():
        """用户注册"""
        try:
            data = request.get_json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not username or not email or not password:
                return jsonify({"message": "请填写所有必填项"}), 400

            if len(password) < 6:
                return jsonify({"message": "密码长度至少为6位"}), 400

            db = next(get_db())

            # 检查用户名是否已存在
            if db.query(User).filter(User.username == username).first():
                return jsonify({"message": "用户名已存在"}), 400

            # 检查邮箱是否已存在
            if db.query(User).filter(User.email == email).first():
                return jsonify({"message": "邮箱已被注册"}), 400

            # 创建新用户
            user = User(username=username, email=email)
            user.set_password(password)
            db.add(user)
            db.commit()
            db.refresh(user)

            return jsonify({
                "message": "注册成功",
                "user": user.to_dict()
            }), 201
        except Exception as e:
            db.rollback()
            return jsonify({"message": f"注册失败: {str(e)}"}), 500
        finally:
            db.close()

    @app.post("/api/auth/login")
    def login_user():
        """用户登录"""
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return jsonify({"message": "请输入用户名和密码"}), 400

            db = next(get_db())

            # 查找用户（支持用户名或邮箱登录）
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()

            if not user or not user.check_password(password):
                return jsonify({"message": "用户名或密码错误"}), 401

            if not user.is_active:
                return jsonify({"message": "账户已被禁用"}), 403

            # 生成简单的 token（实际生产环境应使用 JWT）
            token = secrets.token_urlsafe(32)
            # 存储 token 到用户ID的映射
            token_store[token] = user.id

            return jsonify({
                "message": "登录成功",
                "token": token,
                "user": user.to_dict()
            }), 200
        except Exception as e:
            return jsonify({"message": f"登录失败: {str(e)}"}), 500
        finally:
            db.close()

    @app.get("/api/auth/profile")
    def get_user_profile():
        """获取当前用户信息"""
        try:
            # 从请求头获取 token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "未授权"}), 401

            token = auth_header.split(" ")[1]
            user_id = token_store.get(token)

            if not user_id:
                return jsonify({"message": "无效的 token"}), 401

            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return jsonify({"message": "用户不存在"}), 404

            return jsonify(user.to_dict()), 200
        except Exception as e:
            return jsonify({"message": f"获取用户信息失败: {str(e)}"}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.put("/api/auth/profile")
    def update_user_profile():
        """更新用户信息"""
        try:
            # 从请求头获取 token
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "未授权"}), 401

            token = auth_header.split(" ")[1]
            user_id = token_store.get(token)

            if not user_id:
                return jsonify({"message": "无效的 token"}), 401

            data = request.get_json()
            username = data.get("username")
            email = data.get("email")

            if not username or not email:
                return jsonify({"message": "请填写所有必填项"}), 400

            # 简单的邮箱格式验证
            import re
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({"message": "请输入有效的邮箱地址"}), 400

            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return jsonify({"message": "用户不存在"}), 404

            # 检查用户名是否已被其他用户使用
            existing_user = db.query(User).filter(
                User.username == username,
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({"message": "用户名已被使用"}), 400

            # 检查邮箱是否已被其他用户使用
            existing_email = db.query(User).filter(
                User.email == email,
                User.id != user_id
            ).first()
            if existing_email:
                return jsonify({"message": "邮箱已被使用"}), 400

            # 更新用户信息
            user.username = username
            user.email = email
            db.commit()
            db.refresh(user)

            return jsonify(user.to_dict()), 200
        except Exception as e:
            db.rollback()
            return jsonify({"message": f"更新用户信息失败: {str(e)}"}), 500
        finally:
            db.close()

    # ========== 设备类型管理 API ==========
    @app.get("/api/device-types")
    def get_device_types():
        """获取设备类型列表"""
        try:
            db = next(get_db())
            device_types = db.query(DeviceType).all()
            result = [dt.to_dict() for dt in device_types]
            return jsonify({"device_types": result}), 200
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取设备类型失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.post("/api/device-types")
    def create_device_type():
        """创建设备类型"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            # 验证必填字段
            if not data.get("name") or not data.get("code"):
                return jsonify({"error": "设备类型名称和代码为必填项"}), 400
            
            # 检查代码是否已存在
            existing = db.query(DeviceType).filter(DeviceType.code == data["code"]).first()
            if existing:
                return jsonify({"error": f"设备类型代码 '{data['code']}' 已存在"}), 400
            
            # 创建设备类型
            device_type = DeviceType(
                code=data["code"],
                name=data["name"],
                description=data.get("description", "")
            )
            db.add(device_type)
            db.flush()  # 获取 device_type.id
            
            # 创建参数
            if data.get("parameters"):
                for index, param_data in enumerate(data["parameters"]):
                    if param_data.get("name") and param_data.get("key"):
                        param = DeviceTypeParameter(
                            device_type_id=device_type.id,
                            param_key=param_data["key"],
                            param_name=param_data["name"],
                            param_type=param_data.get("type", "string"),
                            required=param_data.get("required", False),
                            default_value=param_data.get("default_value"),
                            sort_order=param_data.get("sort_order", index)
                        )
                        db.add(param)
            
            db.commit()
            db.refresh(device_type)
            
            return jsonify({
                "message": "设备类型创建成功",
                "device_type": device_type.to_dict()
            }), 201
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.put("/api/device-types/<int:device_type_id>")
    def update_device_type(device_type_id):
        """更新设备类型"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            device_type = db.query(DeviceType).filter(DeviceType.id == device_type_id).first()
            if not device_type:
                return jsonify({"error": "设备类型不存在"}), 404
            
            # 更新基本信息
            if "name" in data:
                device_type.name = data["name"]
            if "description" in data:
                device_type.description = data.get("description", "")
            
            # 更新参数（删除旧参数，添加新参数）
            if "parameters" in data:
                # 删除旧参数
                db.query(DeviceTypeParameter).filter(
                    DeviceTypeParameter.device_type_id == device_type_id
                ).delete()
                
                # 添加新参数
                for index, param_data in enumerate(data["parameters"]):
                    if param_data.get("name") and param_data.get("key"):
                        param = DeviceTypeParameter(
                            device_type_id=device_type_id,
                            param_key=param_data["key"],
                            param_name=param_data["name"],
                            param_type=param_data.get("type", "string"),
                            required=param_data.get("required", False),
                            default_value=param_data.get("default_value"),
                            sort_order=param_data.get("sort_order", index)
                        )
                        db.add(param)
            
            db.commit()
            db.refresh(device_type)
            
            return jsonify({
                "message": "设备类型更新成功",
                "device_type": device_type.to_dict()
            }), 200
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.delete("/api/device-types/<int:device_type_id>")
    def delete_device_type(device_type_id):
        """删除设备类型"""
        try:
            db = next(get_db())
            
            device_type = db.query(DeviceType).filter(DeviceType.id == device_type_id).first()
            if not device_type:
                return jsonify({"error": "设备类型不存在"}), 404
            
            # 检查是否有设备使用该类型
            device_count = db.query(Device).filter(Device.device_type_id == device_type_id).count()
            if device_count > 0:
                return jsonify({
                    "error": f"无法删除：有 {device_count} 个设备正在使用此类型"
                }), 400
            
            # 删除设备类型（级联删除参数）
            db.delete(device_type)
            db.commit()
            
            return jsonify({
                "message": "设备类型删除成功"
            }), 200
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    # ========== 标签类型管理 API ==========
    @app.get("/api/laptop-label-types")
    def get_laptop_label_types():
        """获取标签类型列表"""
        db = next(get_db())
        try:
            application_id = request.args.get("application_id", type=int)
            query = db.query(LaptopLabelType)
            if application_id:
                query = query.filter(
                    (LaptopLabelType.application_id == application_id)
                    | (LaptopLabelType.application_id.is_(None))
                )
            label_types = query.order_by(LaptopLabelType.id.asc()).all()
            return jsonify({
                "label_types": [lt.to_dict() for lt in label_types]
            }), 200
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.post("/api/laptop-label-types")
    def create_laptop_label_type():
        """新增标签类型"""
        db = next(get_db())
        try:
            data = request.get_json() or {}
            name = data.get("name")
            label_type = data.get("label_type")

            if not name or not label_type:
                return jsonify({"error": "标签名称和标签类型为必填项"}), 400

            def parse_float(value):
                if value in (None, "", []):
                    return None
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            label = LaptopLabelType(
                name=name,
                label_type=label_type,
                length_mm=parse_float(data.get("length_mm")),
                width_mm=parse_float(data.get("width_mm")),
                image_path=data.get("image_path") or "./data/labels/label.png",
                application_id=data.get("application_id"),
                description=data.get("description", ""),
            )
            db.add(label)
            db.commit()
            db.refresh(label)
            return jsonify({
                "message": "标签类型创建成功",
                "label_type": label.to_dict()
            }), 201
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.put("/api/laptop-label-types/<int:label_type_id>")
    def update_laptop_label_type(label_type_id):
        """更新标签类型"""
        db = next(get_db())
        try:
            data = request.get_json() or {}
            label = db.query(LaptopLabelType).filter(LaptopLabelType.id == label_type_id).first()
            if not label:
                return jsonify({"error": "标签类型不存在"}), 404

            def parse_float(value):
                if value in (None, "", []):
                    return None
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            if "name" in data:
                label.name = data["name"]
            if "label_type" in data:
                label.label_type = data["label_type"]
            if "length_mm" in data:
                label.length_mm = parse_float(data.get("length_mm"))
            if "width_mm" in data:
                label.width_mm = parse_float(data.get("width_mm"))
            if "image_path" in data:
                label.image_path = data.get("image_path") or "./data/labels/label.png"
            if "application_id" in data:
                label.application_id = data.get("application_id")
            if "description" in data:
                label.description = data.get("description", "")

            db.commit()
            db.refresh(label)
            return jsonify({
                "message": "标签类型更新成功",
                "label_type": label.to_dict()
            }), 200
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.delete("/api/laptop-label-types/<int:label_type_id>")
    def delete_laptop_label_type(label_type_id):
        """删除标签类型"""
        db = next(get_db())
        try:
            label = db.query(LaptopLabelType).filter(LaptopLabelType.id == label_type_id).first()
            if not label:
                return jsonify({"error": "标签类型不存在"}), 404

            db.delete(label)
            db.commit()
            return jsonify({"message": "标签类型删除成功"}), 200
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.get("/api/laptop-label-types/<int:label_type_id>/image")
    def get_laptop_label_type_image(label_type_id):
        """获取标签类型图片"""
        db = next(get_db())
        try:
            label = db.query(LaptopLabelType).filter(LaptopLabelType.id == label_type_id).first()
            if not label:
                return jsonify({"error": "标签类型不存在"}), 404

            image_path = label.image_path or "./data/labels/label.png"
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            if not os.path.isabs(image_path):
                normalized = image_path.lstrip("./").lstrip("/")
                image_path = os.path.join(base_dir, normalized)
            image_path = os.path.abspath(image_path)

            if not image_path.startswith(base_dir):
                return jsonify({"error": "非法的文件路径"}), 400

            if not os.path.exists(image_path):
                return jsonify({"error": "图片文件不存在"}), 404

            mime_type, _ = mimetypes.guess_type(image_path)
            return send_file(image_path, mimetype=mime_type or "application/octet-stream")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.post("/api/laptop-label-types/upload")
    def upload_laptop_label_type_image():
        """上传标签类型图片"""
        if "file" not in request.files:
            return jsonify({"error": "未找到上传文件"}), 400

        upload_file = request.files["file"]
        if upload_file.filename == "":
            return jsonify({"error": "请选择文件"}), 400

        filename = secure_filename(upload_file.filename)
        if "." not in filename:
            return jsonify({"error": "文件缺少扩展名"}), 400
        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({"error": "不支持的文件类型"}), 400

        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "labels", "uploads"))
        os.makedirs(upload_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(upload_dir, unique_name)
        upload_file.save(file_path)

        relative_path = f"./data/labels/uploads/{unique_name}"
        return jsonify({"message": "上传成功", "path": relative_path}), 201

    @app.get("/api/orders/in-progress")
    def get_in_progress_orders():
        """获取所有生产任务订单列表（scheduled + in_progress），将当前正在生产的订单置顶"""
        db = next(get_db())
        try:
            # 获取所有 scheduled 和 in_progress 状态的订单
            # 使用 CASE 语句确保 in_progress 状态的订单排在前面
            from sqlalchemy import case
            status_order = case(
                (ProductionOrder.status == "in_progress", 0),
                (ProductionOrder.status == "scheduled", 1),
                else_=2
            )
            all_orders = (
                db.query(ProductionOrder)
                .options(joinedload(ProductionOrder.product_type))
                .filter(ProductionOrder.status.in_(["scheduled", "in_progress"]))
                .order_by(
                    # 先按状态排序：in_progress (0) 在前，scheduled (1) 在后
                    status_order.asc(),
                    # 然后按排产日期排序
                    ProductionOrder.scheduled_date.is_(None),
                    ProductionOrder.scheduled_date.asc(),
                    # 最后按 ID 排序
                    ProductionOrder.id.asc(),
                )
                .all()
            )

            order_ids = [order.id for order in all_orders]
            completed_counts = {}
            if order_ids:
                completed_rows = (
                    db.query(ProductionProduct.order_id, func.count(ProductionProduct.id))
                    .filter(ProductionProduct.order_id.in_(order_ids))
                    .filter(ProductionProduct.status.in_(["completed", "packaged", "shipped"]))
                    .group_by(ProductionProduct.order_id)
                    .all()
                )
                completed_counts = {order_id: count for order_id, count in completed_rows}

            order_data = []
            for order in all_orders:
                quantity = order.quantity or 0
                # 只有当前正在执行的订单才展示实时完成进度
                if order.status == "in_progress":
                    completed = completed_counts.get(order.id, 0)
                else:
                    completed = 0
                pending = max(quantity - completed, 0)
                order_data.append({
                    "order_id": order.id,
                    "order_code": order.order_code,
                    "product_code": order.product_code,
                    "product_name": order.product_type.product_name if order.product_type else order.product_code,
                    "quantity": quantity,
                    "completed": completed,
                    "pending": pending,
                    "status": order.status,  # 添加状态字段，用于前端判断是否高亮
                    "scheduled_date": order.scheduled_date.isoformat() if order.scheduled_date else None,
                    "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
                })

            return jsonify({"orders": order_data}), 200
        except (OperationalError, DatabaseError) as e:
            print(f"数据库连接错误: {e}")
            return jsonify({
                "error": "数据库连接失败",
                "message": "无法连接到数据库服务器，请检查数据库配置和网络连接",
                "orders": []
            }), 503
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    @app.get("/api/simulation/events")
    def get_simulation_events():
        simulator = getattr(app, "production_simulator", None)
        if not simulator:
            return jsonify({"events": []}), 200
        limit = request.args.get("limit", 100, type=int)
        return jsonify({"events": simulator.get_events(limit)}), 200

    @app.get("/api/simulation/status")
    def get_simulation_status():
        simulator = getattr(app, "production_simulator", None)
        if not simulator:
            return jsonify({"running": False, "events": 0}), 200
        return jsonify({
            "running": simulator.running,
            "events": len(simulator.events)
        }), 200

    @app.post("/api/simulation/start")
    def start_simulation():
        """启动生产模拟"""
        simulator = getattr(app, "production_simulator", None)
        if not simulator:
            return jsonify({"error": "模拟器未初始化"}), 500
        if simulator.running:
            return jsonify({"message": "模拟器已在运行", "running": True}), 200
        simulator.start()
        return jsonify({"message": "模拟器已启动", "running": True}), 200

    @app.post("/api/simulation/stop")
    def stop_simulation():
        """停止生产模拟"""
        simulator = getattr(app, "production_simulator", None)
        if not simulator:
            return jsonify({"error": "模拟器未初始化"}), 500
        if not simulator.running:
            return jsonify({"message": "模拟器未运行", "running": False}), 200
        simulator.stop()
        
        db = next(get_db())
        try:
            reset_orders_and_products(db, log_prefix="停止生产")
        except Exception as e:
            db.rollback()
            print(f"停止生产时重置订单和产品状态失败: {e}")
        finally:
            db.close()
        
        # 3. 清空所有生产日志
        try:
            simulator.clear_events()
            # Broadcast clear event to all connected clients
            try:
                app.socketio.emit('simulation_cleared', {}, namespace='/simulation')
            except Exception as e:
                print(f"Error broadcasting clear event: {e}")
        except Exception as e:
            print(f"停止生产时清空日志失败: {e}")
        
        return jsonify({"message": "模拟器已停止，所有数据已重置", "running": False}), 200

    @app.post("/api/simulation/clear")
    def clear_simulation_events():
        """清空生产日志事件"""
        simulator = getattr(app, "production_simulator", None)
        if not simulator:
            return jsonify({"error": "模拟器未初始化"}), 500
        simulator.clear_events()
        # Broadcast clear event to all connected clients
        try:
            app.socketio.emit('simulation_cleared', {}, namespace='/simulation')
        except Exception as e:
            print(f"Error broadcasting clear event: {e}")
        return jsonify({"message": "日志已清空", "events": 0}), 200

    @app.post("/api/simulation/reset-orders")
    def reset_orders_to_initial_state():
        """重置所有订单和产品状态为初始状态（scheduled）"""
        db = next(get_db())
        try:
            stats = reset_orders_and_products(db, log_prefix="开始生产前重置")
            return jsonify({
                "message": "订单状态已重置",
                "orders_reset": stats["orders_reset"],
                "products_reset": stats["products_reset"],
                "normalize": stats["normalize_stats"],
                "remaining_abnormal": stats["remaining"],
            }), 200
        except (OperationalError, DatabaseError) as e:
            db.rollback()
            print(f"数据库连接错误: {e}")
            return jsonify({
                "error": "数据库连接失败",
                "message": "无法连接到数据库服务器，请检查数据库配置和网络连接"
            }), 503
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(f"重置订单状态失败: {error_trace}")
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            db.close()

    # WebSocket event handlers
    @app.socketio.on('connect', namespace='/simulation')
    def handle_simulation_connect():
        """Handle WebSocket connection for simulation events."""
        print('Client connected to simulation namespace')
        # Send initial events if available (limit to 20)
        simulator = getattr(app, "production_simulator", None)
        if simulator:
            events = simulator.get_events(20)
            if events:
                emit('initial_events', {'events': events})

    @app.socketio.on('disconnect', namespace='/simulation')
    def handle_simulation_disconnect():
        """Handle WebSocket disconnection."""
        print('Client disconnected from simulation namespace')

    @app.get("/api/applications")
    def get_applications():
        """获取应用列表"""
        try:
            db = next(get_db())
            applications = db.query(Application).all()
            return jsonify({
                "applications": [{
                    "id": app.id,
                    "name": app.name,
                    "english_name": app.english_name,
                    "description": app.description
                } for app in applications]
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/api/applications/<int:application_id>/topology")
    def get_application_topology(application_id):
        """获取指定应用的网络拓扑"""
        try:
            db = next(get_db())
            
            # 验证应用是否存在
            application = db.query(Application).filter(Application.id == application_id).first()
            if not application:
                return jsonify({"error": "应用不存在"}), 404
            
            # 获取该应用的所有设备
            devices = db.query(Device).filter(Device.application_id == application_id).all()
            device_codes = {device.code for device in devices}
            
            # 获取该应用的设备拓扑连接
            topologies = db.query(DeviceTopology).filter(
                DeviceTopology.source_device_code.in_(device_codes),
                DeviceTopology.target_device_code.in_(device_codes)
            ).all()
            
            # 获取设备详细信息
            devices_data = []
            for device in devices:
                devices_data.append({
                    "id": device.id,
                    "code": device.code,
                    "name": device.name,
                    "type": device.device_type.code if device.device_type else None,
                    "status": device.status,
                    "position_x": device.position_x,
                    "position_y": device.position_y
                })
            
            return jsonify({
                "application": {
                    "id": application.id,
                    "name": application.name,
                    "english_name": application.english_name
                },
                "devices": devices_data,
                "topology": [topology.to_dict() for topology in topologies]
            }), 200
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.post("/api/applications/<int:application_id>/topology")
    def create_topology_connection(application_id):
        """为指定应用创建网络拓扑连接"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            # 验证应用是否存在
            application = db.query(Application).filter(Application.id == application_id).first()
            if not application:
                return jsonify({"error": "应用不存在"}), 404
            
            # 验证必填字段
            if not data.get("source_device_code") or not data.get("target_device_code"):
                return jsonify({"error": "源设备编码和目标设备编码为必填项"}), 400
            
            # 验证设备是否属于该应用
            source_device = db.query(Device).filter(
                Device.code == data["source_device_code"],
                Device.application_id == application_id
            ).first()
            target_device = db.query(Device).filter(
                Device.code == data["target_device_code"],
                Device.application_id == application_id
            ).first()
            
            if not source_device:
                return jsonify({"error": f"源设备 '{data['source_device_code']}' 不存在或不属于该应用"}), 400
            if not target_device:
                return jsonify({"error": f"目标设备 '{data['target_device_code']}' 不存在或不属于该应用"}), 400
            
            # 检查连接是否已存在
            existing = db.query(DeviceTopology).filter(
                DeviceTopology.source_device_code == data["source_device_code"],
                DeviceTopology.target_device_code == data["target_device_code"]
            ).first()
            
            if existing:
                return jsonify({"error": "该连接已存在"}), 400
            
            # 创建拓扑连接
            topology = DeviceTopology(
                source_device_code=data["source_device_code"],
                target_device_code=data["target_device_code"],
                connection_type=data.get("connection_type", "network"),
                description=data.get("description", "")
            )
            db.add(topology)
            db.commit()
            
            return jsonify({
                "message": "拓扑连接创建成功",
                "topology": topology.to_dict()
            }), 201
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": error_trace}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.put("/api/topology/<int:topology_id>")
    def update_topology_connection(topology_id):
        """更新网络拓扑连接"""
        try:
            data = request.get_json()
            db = next(get_db())
            
            topology = db.query(DeviceTopology).filter(DeviceTopology.id == topology_id).first()
            if not topology:
                return jsonify({"error": "拓扑连接不存在"}), 404
            
            # 更新字段
            if "connection_type" in data:
                topology.connection_type = data["connection_type"]
            if "description" in data:
                topology.description = data["description"]
            
            from datetime import datetime
            topology.updated_at = datetime.utcnow()
            
            db.commit()
            
            return jsonify({
                "message": "拓扑连接更新成功",
                "topology": topology.to_dict()
            }), 200
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.delete("/api/topology/<int:topology_id>")
    def delete_topology_connection(topology_id):
        """删除网络拓扑连接"""
        try:
            db = next(get_db())
            
            topology = db.query(DeviceTopology).filter(DeviceTopology.id == topology_id).first()
            if not topology:
                return jsonify({"error": "拓扑连接不存在"}), 404
            
            db.delete(topology)
            db.commit()
            
            return jsonify({
                "message": "拓扑连接删除成功"
            }), 200
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.post("/api/plm/topology/save")
    def save_topology_layout():
        """保存图块和连接线布局"""
        db = None
        try:
            db = next(get_db())
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "请求数据为空"}), 400
            
            # 检查表是否存在，如果不存在则创建
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            if "tk_positions" not in inspector.get_table_names():
                # 表不存在，创建表
                TK_Positions.__table__.create(db.bind, checkfirst=True)
                print("✓ tk_positions 表已自动创建")
            
            # 清空原有数据
            db.query(TK_Positions).delete()
            
            # 保存图块数据
            nodes = data.get("nodes", [])
            for node in nodes:
                position = TK_Positions(
                    item_type="node",
                    item_id=node.get("id"),
                    base_label=node.get("baseLabel"),
                    label=node.get("label"),
                    x=node.get("x"),
                    y=node.get("y"),
                    color=node.get("color"),
                    item_type_code=node.get("type"),
                    fixed=node.get("fixed", False),
                )
                db.add(position)
            
            # 保存连接线数据
            lines = data.get("lines", [])
            for line in lines:
                position = TK_Positions(
                    item_type="line",
                    item_id=line.get("id"),
                    start_x=line.get("startX"),
                    start_y=line.get("startY"),
                    end_x=line.get("endX"),
                    end_y=line.get("endY"),
                )
                db.add(position)
            
            # 保存计数器数据（只保存一次，使用第一个记录存储）
            if nodes or lines:
                import json
                device_counters = data.get("deviceCounters", {})
                counters_record = TK_Positions(
                    item_type="metadata",
                    item_id="counters",
                    device_counters=json.dumps(device_counters) if device_counters else None,
                    node_id_counter=data.get("nodeIdCounter", 0),
                    connection_line_id_counter=data.get("connectionLineIdCounter", 0),
                )
                db.add(counters_record)
            
            db.commit()
            
            return jsonify({
                "message": "布局保存成功",
                "saved_nodes": len(nodes),
                "saved_lines": len(lines)
            }), 200
        except Exception as e:
            if 'db' in locals():
                db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()

    @app.get("/api/plm/topology/load")
    def load_topology_layout():
        """加载图块和连接线布局"""
        db = None
        try:
            db = next(get_db())
            
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            if "tk_positions" not in inspector.get_table_names():
                # 表不存在，返回空数据
                return jsonify({
                    "nodes": [],
                    "lines": [],
                    "deviceCounters": {},
                    "nodeIdCounter": 0,
                    "connectionLineIdCounter": 0
                }), 200
            
            # 获取所有位置数据
            positions = db.query(TK_Positions).all()
            
            if not positions:
                return jsonify({
                    "nodes": [],
                    "lines": [],
                    "deviceCounters": {},
                    "nodeIdCounter": 0,
                    "connectionLineIdCounter": 0
                }), 200
            
            nodes = []
            lines = []
            device_counters = {}
            node_id_counter = 0
            connection_line_id_counter = 0
            
            for pos in positions:
                if pos.item_type == "node":
                    nodes.append({
                        "id": pos.item_id,
                        "baseLabel": pos.base_label,
                        "label": pos.label,
                        "x": pos.x,
                        "y": pos.y,
                        "color": pos.color,
                        "type": pos.item_type_code,
                        "fixed": pos.fixed or False,
                    })
                elif pos.item_type == "line":
                    lines.append({
                        "id": pos.item_id,
                        "startX": pos.start_x,
                        "startY": pos.start_y,
                        "endX": pos.end_x,
                        "endY": pos.end_y,
                    })
                elif pos.item_type == "metadata":
                    # 恢复计数器数据
                    if pos.device_counters:
                        try:
                            import json
                            device_counters = json.loads(pos.device_counters) if isinstance(pos.device_counters, str) else pos.device_counters
                        except:
                            device_counters = {}
                    node_id_counter = pos.node_id_counter or 0
                    connection_line_id_counter = pos.connection_line_id_counter or 0
            
            return jsonify({
                "nodes": nodes,
                "lines": lines,
                "deviceCounters": device_counters,
                "nodeIdCounter": node_id_counter,
                "connectionLineIdCounter": connection_line_id_counter
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if 'db' in locals():
                db.close()


app = create_app()


if __name__ == "__main__":
    # 根据运行模式设置参数
    debug_mode = MODE == "development"
    port = int(os.getenv("FLASK_PORT", "10060"))
    
    print(f"启动模式: {MODE}")
    print(f"调试模式: {debug_mode}")
    print(f"监听端口: {port}")
    print(f"数据库: {os.getenv('DB_HOST', 'default')}:{os.getenv('DB_PORT', 'default')}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

