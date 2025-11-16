#!/usr/bin/env python3
"""
将 LenovoFMS 系统中的设备数据迁移到数据库
包括设备类型、设备类型参数、设备和设备参数值
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Device, DeviceType, DeviceTypeParameter, DeviceParameterValue

# LenovoFMS 设备数据定义
LENOVOFMS_DEVICES = {
    'read': [
        {'id': 'camera-read-1', 'name': '读码摄像头1', 'type': 'camera', 'station': 'read', 'status': 'online', 'position': {'x': 21.27, 'y': -57.96}, 'details': {'ip': '192.168.1.101', 'exposure': '8ms', 'resolution': '1920x1080'}},
        {'id': 'camera-read-2', 'name': '读码摄像头2', 'type': 'camera', 'station': 'read', 'status': 'online', 'position': {'x': 93.99, 'y': -35.72}, 'details': {'ip': '192.168.1.102', 'exposure': '8ms', 'resolution': '1920x1080'}},
        {'id': 'indicator-read-1', 'name': '指示灯', 'type': 'indicator', 'station': 'read', 'status': 'online', 'position': {'x': 65.77, 'y': -0.15}, 'details': {'status': '运行中', 'color': '绿色'}},
        {'id': 'plc-read-1', 'name': 'PLC控制器', 'type': 'plc', 'station': 'read', 'status': 'online', 'position': {'x': 85.47, 'y': 40.40}, 'details': {'ip': '192.168.1.103', 'program': 'ReadCode_V2.1', 'port': 'ETH1'}},
        {'id': 'switch-read-1', 'name': '交换机', 'type': 'switch', 'station': 'read', 'status': 'online', 'position': {'x': 132.59, 'y': -48.55}, 'details': {'ip': '192.168.1.104', 'model': 'TL-SG1024', 'port': 'ETH2'}},
        {'id': 'servo-read-1', 'name': '伺服电机', 'type': 'servo', 'station': 'read', 'status': 'online', 'position': {'x': 61.96, 'y': 61.35}, 'details': {'ip': '192.168.1.105', 'speed': '1500 rpm', 'torque': '2.5 N·m'}},
    ],
    'label': [
        {'id': 'camera-label-1', 'name': '贴标摄像头1', 'type': 'camera', 'station': 'label', 'status': 'online', 'position': {'x': 32.98, 'y': -51.89}, 'details': {'ip': '192.168.1.201', 'exposure': '6ms', 'resolution': '1920x1080'}},
        {'id': 'camera-label-2', 'name': '贴标摄像头2', 'type': 'camera', 'station': 'label', 'status': 'online', 'position': {'x': 45.42, 'y': -29.66}, 'details': {'ip': '192.168.1.202', 'exposure': '6ms', 'resolution': '1920x1080'}},
        {'id': 'camera-label-3', 'name': '贴标摄像头3', 'type': 'camera', 'station': 'label', 'status': 'online', 'position': {'x': 54.30, 'y': -51.53}, 'details': {'ip': '192.168.1.203', 'exposure': '6ms', 'resolution': '1920x1080'}},
        {'id': 'light-label-1', 'name': '补光灯1', 'type': 'light', 'station': 'label', 'status': 'online', 'position': {'x': 24.40, 'y': -12.96}, 'details': {'brightness': '85%', 'color': '6500K', 'power': '24W'}},
        {'id': 'light-label-2', 'name': '补光灯2', 'type': 'light', 'station': 'label', 'status': 'online', 'position': {'x': 66.95, 'y': -9.42}, 'details': {'brightness': '85%', 'color': '6500K', 'power': '24W'}},
        {'id': 'indicator-label-1', 'name': '指示灯', 'type': 'indicator', 'station': 'label', 'status': 'online', 'position': {'x': 3.44, 'y': -5.20}, 'details': {'status': '运行中', 'color': '绿色'}},
    ],
    'pick': [
        {'id': 'robot-pick-1', 'name': '机械臂', 'type': 'robot', 'station': 'pick', 'status': 'online', 'position': {'x': 10.07, 'y': 4.84}, 'details': {'model': 'UR5', 'payload': '5kg', 'reach': '850mm'}},
        {'id': 'tray-pick-1', 'name': '标签盘', 'type': 'tray', 'station': 'pick', 'status': 'online', 'position': {'x': 81.03, 'y': 41.68}, 'details': {'capacity': '500', 'remaining': '342', 'type': '标签卷'}},
        {'id': 'camera-pick-1', 'name': '取标签摄像头', 'type': 'camera', 'station': 'pick', 'status': 'online', 'position': {'x': 87.74, 'y': -9.37}, 'details': {'ip': '192.168.1.301', 'exposure': '8ms', 'resolution': '1920x1080'}},
        {'id': 'monitor-pick-1', 'name': '工控机', 'type': 'monitor', 'station': 'pick', 'status': 'online', 'position': {'x': -3.43, 'y': -108.18}, 'details': {'ip': '192.168.1.302', 'model': 'IPC-610', 'cpu': 'Intel i5'}},
    ],
    'qc': [
        {'id': 'camera-qc-1', 'name': '质检摄像头', 'type': 'camera', 'station': 'qc', 'status': 'online', 'position': {'x': 15.91, 'y': -36.73}, 'details': {'ip': '192.168.1.401', 'exposure': '10ms', 'resolution': '2048x1536'}},
        {'id': 'indicator-qc-1', 'name': '指示灯', 'type': 'indicator', 'station': 'qc', 'status': 'online', 'position': {'x': 18.96, 'y': -9.71}, 'details': {'status': '运行中', 'color': '绿色'}},
        {'id': 'plc-qc-1', 'name': 'PLC控制器', 'type': 'plc', 'station': 'qc', 'status': 'online', 'position': {'x': 11.60, 'y': 45.45}, 'details': {'ip': '192.168.1.402', 'program': 'QC_V1.8', 'port': 'ETH1'}},
        {'id': 'switch-qc-1', 'name': '交换机', 'type': 'switch', 'station': 'qc', 'status': 'online', 'position': {'x': -23.81, 'y': -44.01}, 'details': {'ip': '192.168.1.403', 'model': 'TL-SG1024', 'port': 'ETH3'}},
        {'id': 'servo-qc-1', 'name': '伺服电机', 'type': 'servo', 'station': 'qc', 'status': 'online', 'position': {'x': 29.14, 'y': 78.54}, 'details': {'ip': '192.168.1.404', 'speed': '1500 rpm', 'torque': '2.5 N·m'}},
    ],
    'network': [
        {'id': 'switch-network-1', 'name': '核心交换机', 'type': 'switch', 'station': 'network', 'status': 'online', 'position': {'x': 50.00, 'y': 20.00}, 'details': {'ip': '192.168.1.1', 'model': 'TL-SG5428', 'port': '24口千兆'}},
        {'id': 'server-mes-1', 'name': 'MES服务器', 'type': 'server', 'station': 'network', 'status': 'online', 'position': {'x': 49.26, 'y': -63.39}, 'details': {'ip': '192.168.1.10', 'model': 'Dell PowerEdge', 'cpu': 'Intel Xeon'}},
        {'id': 'server-mbi-1', 'name': 'MBI服务器', 'type': 'server', 'station': 'network', 'status': 'online', 'position': {'x': 90.69, 'y': 21.68}, 'details': {'ip': '192.168.1.11', 'model': 'Dell PowerEdge', 'cpu': 'Intel Xeon'}},
    ]
}

# 设备类型定义（包含参数定义）
DEVICE_TYPES_CONFIG = {
    'camera': {
        'name': '摄像头',
        'description': '工业摄像头设备，用于图像采集和识别',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'port', 'name': '端口', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'exposure', 'name': '曝光时间', 'type': 'string', 'required': False, 'sort_order': 2},
            {'key': 'resolution', 'name': '分辨率', 'type': 'string', 'required': False, 'sort_order': 3},
        ]
    },
    'switch': {
        'name': '交换机',
        'description': '网络交换机设备，用于网络连接和数据转发',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'port', 'name': '端口', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'model', 'name': '型号', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'plc': {
        'name': 'PLC',
        'description': '可编程逻辑控制器，用于工业自动化控制',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'port', 'name': '端口', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'program', 'name': '程序版本', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'indicator': {
        'name': '指示灯',
        'description': '状态指示灯设备',
        'parameters': [
            {'key': 'status', 'name': '状态', 'type': 'string', 'required': False, 'sort_order': 0},
            {'key': 'color', 'name': '颜色', 'type': 'string', 'required': False, 'sort_order': 1},
        ]
    },
    'servo': {
        'name': '伺服电机',
        'description': '伺服电机设备',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'speed', 'name': '转速', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'torque', 'name': '扭矩', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'robot': {
        'name': '机械臂',
        'description': '工业机械臂设备',
        'parameters': [
            {'key': 'model', 'name': '型号', 'type': 'string', 'required': False, 'sort_order': 0},
            {'key': 'payload', 'name': '负载', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'reach', 'name': '工作半径', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'tray': {
        'name': '标签盘',
        'description': '标签盘设备',
        'parameters': [
            {'key': 'capacity', 'name': '容量', 'type': 'string', 'required': False, 'sort_order': 0},
            {'key': 'remaining', 'name': '剩余', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'type', 'name': '类型', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'monitor': {
        'name': '工控机',
        'description': '工控机设备',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'model', 'name': '型号', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'cpu', 'name': 'CPU', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'light': {
        'name': '补光灯',
        'description': '补光灯设备',
        'parameters': [
            {'key': 'brightness', 'name': '亮度', 'type': 'string', 'required': False, 'sort_order': 0},
            {'key': 'color', 'name': '色温', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'power', 'name': '功率', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
    'server': {
        'name': '服务器',
        'description': '服务器设备，用于数据存储和业务处理',
        'parameters': [
            {'key': 'ip_address', 'name': 'IP地址', 'type': 'string', 'required': True, 'sort_order': 0},
            {'key': 'model', 'name': '型号', 'type': 'string', 'required': False, 'sort_order': 1},
            {'key': 'cpu', 'name': 'CPU', 'type': 'string', 'required': False, 'sort_order': 2},
        ]
    },
}

def create_or_get_device_type(db, type_code, config):
    """创建或获取设备类型"""
    device_type = db.query(DeviceType).filter(DeviceType.code == type_code).first()
    if not device_type:
        device_type = DeviceType(
            code=type_code,
            name=config['name'],
            description=config.get('description', '')
        )
        db.add(device_type)
        db.flush()
        print(f"  创建设备类型: {config['name']} ({type_code})")
    else:
        print(f"  设备类型已存在: {config['name']} ({type_code})")
    
    # 创建或更新参数定义
    if 'parameters' in config:
        for param_config in config['parameters']:
            param = db.query(DeviceTypeParameter).filter(
                DeviceTypeParameter.device_type_id == device_type.id,
                DeviceTypeParameter.param_key == param_config['key']
            ).first()
            
            if not param:
                param = DeviceTypeParameter(
                    device_type_id=device_type.id,
                    param_key=param_config['key'],
                    param_name=param_config['name'],
                    param_type=param_config['type'],
                    required=param_config.get('required', False),
                    sort_order=param_config.get('sort_order', 0)
                )
                db.add(param)
                print(f"    创建参数: {param_config['name']} ({param_config['key']})")
    
    return device_type

def create_device(db, device_data, device_type):
    """创建设备及其参数值"""
    # 检查设备是否已存在
    existing_device = db.query(Device).filter(Device.code == device_data['id']).first()
    if existing_device:
        print(f"  设备已存在: {device_data['name']} ({device_data['id']})")
        return existing_device
    
    # 创建设备
    device = Device(
        name=device_data['name'],
        code=device_data['id'],
        device_type_id=device_type.id,
        position_x=device_data['position']['x'],
        position_y=device_data['position']['y'],
        status=device_data.get('status', 'online'),
        description=f"工位: {device_data.get('station', 'unknown')}"
    )
    db.add(device)
    db.flush()
    print(f"  创建设备: {device_data['name']} ({device_data['id']})")
    
    # 创建参数值
    if 'details' in device_data:
        details = device_data['details']
        # 映射前端字段名到数据库字段名
        field_mapping = {
            'ip': 'ip_address',  # 前端使用 'ip'，数据库使用 'ip_address'
        }
        
        for param in device_type.parameters:
            param_key = param.param_key
            # 先检查直接匹配
            if param_key in details:
                value = details[param_key]
            # 再检查字段映射
            elif param_key in field_mapping.values():
                # 查找映射的键
                mapped_key = None
                for frontend_key, db_key in field_mapping.items():
                    if db_key == param_key and frontend_key in details:
                        mapped_key = frontend_key
                        break
                if mapped_key:
                    value = details[mapped_key]
                else:
                    continue
            else:
                continue
            
            param_value = DeviceParameterValue(
                device_id=device.id,
                parameter_id=param.id,
                param_key=param_key,
                param_value=str(value)
            )
            db.add(param_value)
            print(f"    设置参数 {param_key}: {value}")
    
    return device

def migrate_lenovofms_devices():
    """执行迁移"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始迁移 LenovoFMS 设备数据")
        print("=" * 60)
        
        # 1. 创建设备类型
        print("\n1. 创建设备类型...")
        device_types = {}
        for type_code, config in DEVICE_TYPES_CONFIG.items():
            device_types[type_code] = create_or_get_device_type(db, type_code, config)
        
        db.commit()
        print("  ✓ 设备类型创建完成")
        
        # 2. 创建设备
        print("\n2. 创建设备...")
        total_devices = 0
        for station, device_list in LENOVOFMS_DEVICES.items():
            print(f"\n  工位: {station}")
            for device_data in device_list:
                device_type = device_types.get(device_data['type'])
                if device_type:
                    create_device(db, device_data, device_type)
                    total_devices += 1
                else:
                    print(f"  ⚠ 警告: 未找到设备类型 {device_data['type']}")
        
        db.commit()
        print(f"\n  ✓ 共创建 {total_devices} 个设备")
        
        print("\n" + "=" * 60)
        print("迁移完成!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_lenovofms_devices()

