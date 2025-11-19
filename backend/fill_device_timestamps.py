#!/usr/bin/env python3
"""
为 devices 表中 created_at 和 updated_at 为 NULL 的记录补充时间值
"""
import sys
import os
from datetime import datetime

# 确保可以导入 database 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from database import SessionLocal, Device

def fill_device_timestamps():
    """为 devices 表中 created_at 和 updated_at 为 NULL 的记录补充时间值"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始补充 devices 表的时间戳字段")
        print("=" * 60)
        
        # 获取所有需要更新的记录
        devices_with_null_created = db.query(Device).filter(Device.created_at == None).all()
        devices_with_null_updated = db.query(Device).filter(Device.updated_at == None).all()
        
        print(f"\n需要补充 created_at 的记录数: {len(devices_with_null_created)}")
        print(f"需要补充 updated_at 的记录数: {len(devices_with_null_updated)}")
        
        # 使用当前时间作为默认值（使用 timezone-aware datetime）
        from datetime import timezone
        current_time = datetime.now(timezone.utc)
        
        # 更新 created_at 为 NULL 的记录
        updated_created_count = 0
        for device in devices_with_null_created:
            # 如果 updated_at 也不为空，使用 updated_at 作为 created_at（表示设备在 updated_at 时创建）
            # 否则使用当前时间
            if device.updated_at:
                device.created_at = device.updated_at
            else:
                device.created_at = current_time
            updated_created_count += 1
            print(f"  更新设备 {device.id} ({device.code}): created_at = {device.created_at}")
        
        # 更新 updated_at 为 NULL 的记录
        updated_updated_count = 0
        for device in devices_with_null_updated:
            # 如果 created_at 存在，使用 created_at 作为 updated_at（表示设备在 created_at 时最后更新）
            # 否则使用当前时间
            if device.created_at:
                device.updated_at = device.created_at
            else:
                device.updated_at = current_time
            updated_updated_count += 1
            print(f"  更新设备 {device.id} ({device.code}): updated_at = {device.updated_at}")
        
        # 提交更改
        db.commit()
        
        print(f"\n✓ 更新完成:")
        print(f"  - 补充 created_at: {updated_created_count} 条记录")
        print(f"  - 补充 updated_at: {updated_updated_count} 条记录")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fill_device_timestamps()

