#!/usr/bin/env python3
"""
添加交通诱导屏设备类型到数据库
支持通过环境变量控制连接的数据库（默认为开发环境）
"""

import os
import sys
from datetime import datetime

# 将项目根目录加入 sys.path，确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 如果未显式设置，则默认使用开发环境配置
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DB_HOST', '166.111.80.127')
os.environ.setdefault('DB_PORT', '15432')

from database import SessionLocal, DeviceType, DeviceTypeParameter

DEVICE_TYPE_CODE = 'traffic_guidance_screen'

PARAMETERS_CONFIG = [
    {
        'param_key': 'model',
        'param_name': '型号',
        'param_type': 'string',
        'required': True,
        'sort_order': 0
    },
    {
        'param_key': 'ip_address',
        'param_name': 'IP地址',
        'param_type': 'string',
        'required': True,
        'sort_order': 1
    },
    {
        'param_key': 'communication_protocol',
        'param_name': '通信协议',
        'param_type': 'string',
        'required': False,
        'sort_order': 2
    },
    {
        'param_key': 'screen_size',
        'param_name': '屏幕尺寸',
        'param_type': 'string',
        'required': False,
        'sort_order': 3
    },
    {
        'param_key': 'resolution',
        'param_name': '分辨率',
        'param_type': 'string',
        'required': False,
        'sort_order': 4
    },
    {
        'param_key': 'brightness',
        'param_name': '亮度(cd/m²)',
        'param_type': 'number',
        'required': False,
        'sort_order': 5
    },
    {
        'param_key': 'installation_location',
        'param_name': '安装位置',
        'param_type': 'string',
        'required': False,
        'sort_order': 6
    },
    {
        'param_key': 'content_template',
        'param_name': '内容模板',
        'param_type': 'string',
        'required': False,
        'sort_order': 7
    }
]


def create_traffic_guidance_screen_type():
    """在数据库中创建交通诱导屏设备类型"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始添加交通诱导屏设备类型")
        print("=" * 60)

        existing_type = db.query(DeviceType).filter(DeviceType.code == DEVICE_TYPE_CODE).first()
        if existing_type:
            print(f"设备类型 '交通诱导屏' ({DEVICE_TYPE_CODE}) 已存在，ID: {existing_type.id}")
            print("跳过创建")
            return existing_type

        device_type = DeviceType(
            code=DEVICE_TYPE_CODE,
            name='交通诱导屏',
            description='交通信息诱导发布屏，用于实时展示道路通行和告警信息',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(device_type)
        db.flush()
        print(f"✓ 创建设备类型: 交通诱导屏 ({DEVICE_TYPE_CODE}), ID: {device_type.id}")

        for param_config in PARAMETERS_CONFIG:
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
        print("交通诱导屏设备类型添加成功!")
        print("=" * 60)
        return device_type
    except Exception as exc:
        db.rollback()
        print(f"\n✗ 错误: {exc}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_traffic_guidance_screen_type()


