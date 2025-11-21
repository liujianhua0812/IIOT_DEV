#!/usr/bin/env python3
"""
添加四个红绿灯设备到数据库
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

from database import SessionLocal, Device, DeviceType, DeviceTypeParameter, DeviceParameterValue, Application

def add_traffic_light_devices():
    """添加四个红绿灯设备"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始添加红绿灯设备")
        print("=" * 60)
        
        # 获取红绿灯设备类型
        device_type = db.query(DeviceType).filter(DeviceType.code == 'traffic_light').first()
        if not device_type:
            print("错误: 红绿灯设备类型不存在，请先运行 add_traffic_light_device_type.py")
            return
        
        print(f"✓ 找到设备类型: {device_type.name} (ID: {device_type.id})")
        
        # 获取 TellhowTraffic 应用
        tellhowtraffic_app = db.query(Application).filter(
            (Application.english_name.ilike('%TellhowTraffic%')) | 
            (Application.name.ilike('%TellhowTraffic%')) |
            (Application.english_name.ilike('%Tellhow%Traffic%')) |
            (Application.name.ilike('%Tellhow%Traffic%')) |
            (Application.english_name.ilike('%Traffic%')) |
            (Application.name.ilike('%Traffic%'))
        ).first()
        
        if not tellhowtraffic_app:
            print("警告: 未找到 TellhowTraffic 应用，设备将不关联应用")
            app_id = None
        else:
            app_id = tellhowtraffic_app.id
            print(f"✓ 找到应用: {tellhowtraffic_app.name} (ID: {app_id})")
        
        # 获取红绿灯状态参数
        status_param = db.query(DeviceTypeParameter).filter(
            DeviceTypeParameter.device_type_id == device_type.id,
            DeviceTypeParameter.param_key == 'traffic_light_status'
        ).first()
        
        if not status_param:
            print("错误: 未找到红绿灯状态参数")
            return
        
        # 定义四个红绿灯设备
        traffic_lights = [
            {
                'code': 'TRAFFIC_LIGHT_001',
                'name': '红绿灯01',
                'status': 'online',
                'traffic_light_status': 'red'  # 初始状态为红色
            },
            {
                'code': 'TRAFFIC_LIGHT_002',
                'name': '红绿灯02',
                'status': 'online',
                'traffic_light_status': 'green'  # 初始状态为绿色
            },
            {
                'code': 'TRAFFIC_LIGHT_003',
                'name': '红绿灯03',
                'status': 'online',
                'traffic_light_status': 'yellow'  # 初始状态为黄色
            },
            {
                'code': 'TRAFFIC_LIGHT_004',
                'name': '红绿灯04',
                'status': 'online',
                'traffic_light_status': 'red'  # 初始状态为红色
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for light_data in traffic_lights:
            # 检查设备是否已存在
            existing_device = db.query(Device).filter(Device.code == light_data['code']).first()
            if existing_device:
                print(f"  设备已存在: {light_data['name']} ({light_data['code']})，跳过")
                skipped_count += 1
                continue
            
            # 创建设备
            device = Device(
                name=light_data['name'],
                code=light_data['code'],
                device_type_id=device_type.id,
                application_id=app_id,
                status=light_data['status'],
                # 位置信息后续补充，暂时不设置
                longitude=None,
                latitude=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(device)
            db.flush()
            print(f"  ✓ 创建设备: {light_data['name']} ({light_data['code']}), ID: {device.id}")
            
            # 创建红绿灯状态参数值
            param_value = DeviceParameterValue(
                device_id=device.id,
                parameter_id=status_param.id,
                param_key='traffic_light_status',
                param_value=light_data['traffic_light_status']
            )
            db.add(param_value)
            print(f"    设置参数 traffic_light_status: {light_data['traffic_light_status']}")
            
            created_count += 1
        
        db.commit()
        print("\n" + "=" * 60)
        print(f"红绿灯设备添加完成!")
        print(f"  创建: {created_count} 个")
        print(f"  跳过: {skipped_count} 个")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_traffic_light_devices()

