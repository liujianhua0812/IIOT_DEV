#!/usr/bin/env python3
"""部署模式启动脚本"""
import os
import sys

# 设置部署模式
os.environ["FLASK_ENV"] = "production"

# 设置部署环境数据库配置
os.environ.setdefault("DB_HOST", "192.168.34.14")
os.environ.setdefault("DB_PORT", "5432")

# 导入并运行应用
from app import app

if __name__ == "__main__":
    deploy_ip = "166.111.80.127"
    print("=" * 50)
    print("启动部署模式")
    print("=" * 50)
    print(f"数据库: {os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}")
    print(f"服务地址: http://{deploy_ip}:10060")
    print("=" * 50)
    
    # 部署模式不使用 debug，使用端口 10060，绑定到所有接口
    app.run(host="0.0.0.0", port=10060, debug=False)

