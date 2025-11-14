import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db, Device
from config import MODE


def create_app() -> Flask:
    app = Flask(__name__)
    
    # 根据运行模式配置 CORS
    if MODE == "production":
        # 部署模式：限制跨域来源
        default_origins = "http://166.111.80.127:10061,http://localhost:10061"
        allowed_origins = os.getenv("CORS_ORIGINS", default_origins).split(",")
        # 清理空白字符
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        CORS(app, 
             resources={
                 r"/api/*": {
                     "origins": allowed_origins,
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                     "allow_headers": ["Content-Type", "Authorization"],
                     "supports_credentials": True
                 },
                 r"/health": {"origins": "*"}
             },
             supports_credentials=True)
        print(f"CORS 允许的来源: {allowed_origins}")
    else:
        # 开发模式：允许所有来源
        CORS(app, resources={r"/api/*": {"origins": "*"}, r"/health": {"origins": "*"}})

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

            # 构建查询
            query = db.query(Device)

            # 状态筛选
            if status:
                query = query.filter(Device.status == status)

            # 搜索筛选（设备名称或编码）
            if search:
                query = query.filter(
                    (Device.name.ilike(f"%{search}%")) | (Device.code.ilike(f"%{search}%"))
                )

            # 获取总数
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


app = create_app()


if __name__ == "__main__":
    # 根据运行模式设置参数
    debug_mode = MODE == "development"
    port = int(os.getenv("FLASK_PORT", "5001"))
    
    print(f"启动模式: {MODE}")
    print(f"调试模式: {debug_mode}")
    print(f"监听端口: {port}")
    print(f"数据库: {os.getenv('DB_HOST', 'default')}:{os.getenv('DB_PORT', 'default')}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

