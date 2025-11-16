import os
import requests
import secrets
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, Device, User, DeviceType, DeviceTypeParameter, DeviceParameterValue
from sqlalchemy.orm import joinedload
from config import MODE

# 简单的 token 存储（生产环境应使用 Redis 或数据库）
token_store = {}


def create_app() -> Flask:
    app = Flask(__name__)
    
    # 根据运行模式配置 CORS
    if MODE == "production":
        # 部署模式：限制跨域来源
        default_origins = "http://166.111.80.127:10061,http://166.111.80.127:10062,http://localhost:10061,http://localhost:10062"
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
                 r"/health": {"origins": "*"}
             },
             supports_credentials=True,
             automatic_options=True)
        print(f"CORS 允许的来源: {allowed_origins}")
    else:
        # 开发模式：允许所有来源，包括 admin_frontend 的端口
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
        overview = {
            "deviceCount": 1864,
            "modalTypes": 12,
            "securityEvents": 327,
            "dispatchTasks": 95,
        }
        return jsonify(overview)

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

    @app.put("/api/devices/<int:device_id>")
    def update_device(device_id):
        """更新设备信息"""
        try:
            data = request.get_json()
            print(f"收到更新设备 {device_id} 的请求，数据: {data}")
            db = next(get_db())
            
            device = db.query(Device).options(
                joinedload(Device.parameter_values),
                joinedload(Device.device_type).joinedload(DeviceType.parameters)
            ).filter(Device.id == device_id).first()
            
            if not device:
                return jsonify({"error": "设备不存在"}), 404
            
            print(f"设备信息: id={device.id}, name={device.name}, device_type_id={device.device_type_id}")
            if device.device_type:
                print(f"设备类型: {device.device_type.name}, 参数数量: {len(device.device_type.parameters)}")
            else:
                print("设备没有关联设备类型")
            
            # 更新设备基本信息
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
            
            # 更新参数值
            existing_params = {}
            if "parameters" in data:
                print(f"准备更新参数值: {data['parameters']}")
                # 如果设备类型被更新了，需要重新加载设备类型
                if "device_type_id" in data:
                    db.refresh(device)
                    device = db.query(Device).options(
                        joinedload(Device.parameter_values),
                        joinedload(Device.device_type).joinedload(DeviceType.parameters)
                    ).filter(Device.id == device_id).first()
                
                if not device.device_type:
                    error_msg = "设备没有关联设备类型，无法更新参数值"
                    print(f"错误: {error_msg}")
                    return jsonify({"error": error_msg}), 400
                
                # 获取设备类型的所有参数定义
                if not device.device_type.parameters:
                    error_msg = "设备类型没有定义参数"
                    print(f"错误: {error_msg}")
                    return jsonify({"error": error_msg}), 400
                
                param_definitions = {p.param_key: p for p in device.device_type.parameters}
                
                # 查询现有的参数值（直接从数据库查询，确保获取最新数据）
                existing_params_query = db.query(DeviceParameterValue).filter(
                    DeviceParameterValue.device_id == device.id
                ).all()
                existing_params = {pv.param_key: pv for pv in existing_params_query}
                
                for param_key, param_value in data["parameters"].items():
                    if param_key not in param_definitions:
                        # 跳过不在设备类型参数定义中的参数
                        continue
                    
                    param_def = param_definitions[param_key]
                    
                    # 转换参数值
                    try:
                        if param_value is None:
                            str_value = None
                        elif param_def.param_type == 'boolean':
                            str_value = 'true' if param_value else 'false'
                        elif param_def.param_type == 'date':
                            if isinstance(param_value, str):
                                str_value = param_value
                            else:
                                str_value = str(param_value) if param_value is not None else None
                        elif param_def.param_type == 'number':
                            if param_value is None or param_value == '':
                                str_value = None
                            else:
                                str_value = str(param_value)
                        else:
                            str_value = str(param_value) if param_value is not None else None
                    except Exception as e:
                        error_msg = f"参数 {param_key} 值转换失败: {str(e)}"
                        print(f"错误: {error_msg}, 参数值: {param_value}, 类型: {type(param_value)}")
                        return jsonify({"error": error_msg}), 400
                    
                    # 查找或创建参数值
                    if param_key in existing_params:
                        # 更新现有参数值
                        param_value_obj = existing_params[param_key]
                        param_value_obj.param_value = str_value
                        # 手动触发 updated_at 更新
                        from datetime import datetime
                        param_value_obj.updated_at = datetime.utcnow()
                    else:
                        # 创建新参数值
                        param_value_obj = DeviceParameterValue(
                            device_id=device.id,
                            parameter_id=param_def.id,
                            param_key=param_key,
                            param_value=str_value
                        )
                        db.add(param_value_obj)
                        existing_params[param_key] = param_value_obj
            
            db.commit()
            # 重新加载设备及其关联数据以确保获取最新数据
            db.refresh(device)
            # 刷新所有参数值对象（如果存在）
            if existing_params:
                for pv in existing_params.values():
                    db.refresh(pv)
            # 重新查询设备以获取完整的关联数据
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
            print(f"更新设备失败: {str(e)}")
            print(error_trace)
            return jsonify({"error": str(e), "traceback": error_trace}), 500
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

