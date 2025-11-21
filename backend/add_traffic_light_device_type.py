#!/usr/bin/env python3
"""
添加红绿灯设备类型到数据库
支持通过环境变量指定数据库连接（开发/生产环境）
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量（如果未设置，默认使用开发环境）
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'
if not os.environ.get('DB_HOST'):
    os.environ['DB_HOST'] = '166.111.80.127'
if not os.environ.get('DB_PORT'):
    os.environ['DB_PORT'] = '15432'

from database import SessionLocal, DeviceType, DeviceTypeParameter

def create_traffic_light_device_type():
    """创建红绿灯设备类型"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始添加红绿灯设备类型")
        print("=" * 60)
        
        # 检查设备类型是否已存在
        existing_type = db.query(DeviceType).filter(DeviceType.code == 'traffic_light').first()
        
        if existing_type:
            print(f"设备类型 '红绿灯' (traffic_light) 已存在，ID: {existing_type.id}")
            print("跳过创建")
            return existing_type
        
        # 创建设备类型
        device_type = DeviceType(
            code='traffic_light',
            name='红绿灯',
            description='交通信号灯，用于控制路口交通流量',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(device_type)
        db.flush()
        print(f"✓ 创建设备类型: 红绿灯 (traffic_light), ID: {device_type.id}")
        
        # 创建参数定义
        parameters_config = [
            {
                'param_key': 'traffic_light_status',
                'param_name': '红绿灯状态',
                'param_type': 'string',
                'required': True,
                'sort_order': 0
            },
            {
                'param_key': 'model',
                'param_name': '型号',
                'param_type': 'string',
                'required': False,
                'sort_order': 1
            },
            {
                'param_key': 'ip_address',
                'param_name': 'IP地址',
                'param_type': 'string',
                'required': False,
                'sort_order': 2
            },
            {
                'param_key': 'installation_location',
                'param_name': '安装位置',
                'param_type': 'string',
                'required': False,
                'sort_order': 3
            },
            {
                'param_key': 'direction',
                'param_name': '方向',
                'param_type': 'string',
                'required': False,
                'sort_order': 4
            }
        ]
        
        for param_config in parameters_config:
            # 检查参数是否已存在
            existing_param = db.query(DeviceTypeParameter).filter(
                DeviceTypeParameter.device_type_id == device_type.id,
                DeviceTypeParameter.param_key == param_config['param_key']
            ).first()
            
            if existing_param:
                print(f"  参数 '{param_config['param_name']}' ({param_config['param_key']}) 已存在，跳过")
                continue
            
            param = DeviceTypeParameter(
                device_type_id=device_type.id,
                param_key=param_config['param_key'],
                param_name=param_config['param_name'],
                param_type=param_config['param_type'],
                required=param_config['required'],
                sort_order=param_config['sort_order'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(param)
            print(f"  ✓ 创建参数: {param_config['param_name']} ({param_config['param_key']})")
        
        db.commit()
        print("\n" + "=" * 60)
        print("红绿灯设备类型添加成功!")
        print("=" * 60)
        
        return device_type
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_traffic_light_device_type()

