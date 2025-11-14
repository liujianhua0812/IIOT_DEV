#!/usr/bin/env python3
"""测试 CORS 配置"""
import os
os.environ["FLASK_ENV"] = "production"
os.environ.setdefault("CORS_ORIGINS", "http://166.111.80.127:10061,http://localhost:10061")

from app import app

print("测试 CORS 配置...")
print(f"允许的来源: {os.environ.get('CORS_ORIGINS')}")

with app.test_client() as client:
    # 测试 OPTIONS 预检请求
    print("\n1. 测试 OPTIONS 预检请求:")
    response = client.options('/api/devices', headers={
        'Origin': 'http://166.111.80.127:10061',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    })
    print(f"   状态码: {response.status_code}")
    print("   CORS 头:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"     {key}: {value}")
    
    # 测试 GET 请求
    print("\n2. 测试 GET 请求:")
    response = client.get('/api/devices', headers={
        'Origin': 'http://166.111.80.127:10061'
    })
    print(f"   状态码: {response.status_code}")
    print("   CORS 头:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"     {key}: {value}")

