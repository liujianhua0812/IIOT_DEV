#!/usr/bin/env python3
"""开发模式启动脚本"""
import os
import sys

# 设置开发模式
os.environ["FLASK_ENV"] = "development"

# 设置开发环境数据库配置
os.environ.setdefault("DB_HOST", "166.111.80.127")
os.environ.setdefault("DB_PORT", "15432")

# 导入并运行应用
from app import app

if __name__ == "__main__":
    print("=" * 50)
    print("启动开发模式")
    print("=" * 50)
    print(f"数据库: {os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5001, debug=True)

