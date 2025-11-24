#!/usr/bin/env python3
"""开发模式启动脚本"""
import os
import sys

# 设置开发模式
os.environ["FLASK_ENV"] = "development"

# 设置开发环境数据库配置
# 本地开发环境使用内网数据库（外部地址166.111.80.127:15432仅对公网访问有效）
os.environ.setdefault("DB_HOST", "192.168.34.14")
os.environ.setdefault("DB_PORT", "5432")

# 导入并运行应用
from app import app

if __name__ == "__main__":
    print("=" * 50)
    print("启动开发模式")
    print("=" * 50)
    print(f"数据库: {os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}")
    print("=" * 50)
    
    # Use SocketIO to run the app for WebSocket support
    # allow_unsafe_werkzeug=True is needed for development mode
    app.socketio.run(app, host="0.0.0.0", port=10060, debug=True, allow_unsafe_werkzeug=True)

