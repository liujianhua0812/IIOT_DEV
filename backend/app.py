import os
import mimetypes
import uuid
import requests
import secrets
from flask import Flask, jsonify, request, Response, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
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
)
from sqlalchemy.orm import joinedload
from config import MODE

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}

# 简单的 token 存储（生产环境应使用 Redis 或数据库）
token_store = {}


def create_app() -> Flask:
    app = Flask(__name__)
    
    # 根据运行模式配置 CORS
    if MODE == "production":
        # 部署模式：限制跨域来源
        default_origins = "http://166.111.80.127:10061,http://166.111.80.127:10062,http://166.111.80.127:10063,http://166.111.80.127:10064,http://166.111.80.127:10065,http://localhost:10061,http://localhost:10062,http://localhost:10063,http://localhost:10064,http://localhost:10065"
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
            label_type_query = db.query(LaptopLabelType)
            label_type_count = 0

            if application:
                device_count = (
                    db.query(Device)
                    .filter(Device.application_id == application.id)
                    .count()
                )
                label_type_count = (
                    label_type_query
                    .filter(
                        (LaptopLabelType.application_id == application.id) |
                        (LaptopLabelType.application_id.is_(None))
                    )
                    .count()
                )
            else:
                label_type_count = label_type_query.count()

            overview = {
                "labelTypes": label_type_count,
                "deviceCount": device_count,
                "modalTypes": 12,
                "securityEvents": 327,
                "dispatchTasks": 95,
            }
            return jsonify(overview)
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500

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
        try:
            db = next(get_db())
            
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
            
            for device in devices:
                # 从参数值中获取 ip_address
                ip_address = None
                if device.parameter_values:
                    for pv in device.parameter_values:
                        if pv.param_key == "ip_address":
                            ip_address = pv.param_value
                            break
                
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
                
                devices_data.append(device_dict)
                
                # 按设备类型分类
                device_type = device.device_type.code if device.device_type else None
                if device_type == 'camera':
                    cameras.append(device_dict)
                elif device_type == 'signal_controller':
                    signal_controllers.append(device_dict)
                elif device_type == 'switch':
                    switches.append(device_dict)
            
            # 构建返回数据
            result = {
                "devices": devices_data,
                "cameras": cameras,
                "signal_controllers": signal_controllers,
                "switches": switches
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

