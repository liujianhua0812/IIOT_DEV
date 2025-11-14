from flask import Flask, jsonify
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    # 允许所有来源的跨域请求（开发环境）
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


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

