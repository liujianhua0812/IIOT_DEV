#!/usr/bin/env python3
"""迁移设备拓扑连接信息到数据库"""

from database import SessionLocal, DeviceTopology
from datetime import datetime

# 从 FlexibleLabelingMachine.vue 中提取的连接信息
network_topology_data = {
    # 读码区连接
    'read': {
        # 伺服电机和指示灯连接到PLC
        'servo-read-1': 'plc-read-1',
        'indicator-read-1': 'plc-read-1',
        # PLC和摄像头连接到交换机
        'plc-read-1': 'switch-read-1',
        'camera-read-1': 'switch-read-1',
        'camera-read-2': 'switch-read-1',
        # 读码区交换机连接到核心交换机
        'switch-read-1': 'switch-network-1'
    },
    # 贴标区连接
    'label': {
        # 三个摄像头连接到读码区的交换机
        'camera-label-1': 'switch-read-1',
        'camera-label-2': 'switch-read-1',
        'camera-label-3': 'switch-read-1',
        # 两个补光灯和指示灯连接到读码区的PLC
        'light-label-1': 'plc-read-1',
        'light-label-2': 'plc-read-1',
        'indicator-label-1': 'plc-read-1'
    },
    # 取标签区连接
    'pick': {
        # 机械臂、取标签摄像头、工控机连接到质检区的交换机
        'robot-pick-1': 'switch-qc-1',
        'camera-pick-1': 'switch-qc-1',
        'monitor-pick-1': 'switch-qc-1',
        # 标签盘连接到质检区的PLC
        'tray-pick-1': 'plc-qc-1'
    },
    # 质检区连接
    'qc': {
        # 摄像头和PLC连接到交换机
        'camera-qc-1': 'switch-qc-1',
        'plc-qc-1': 'switch-qc-1',
        # 指示灯和伺服电机连接到PLC
        'indicator-qc-1': 'plc-qc-1',
        'servo-qc-1': 'plc-qc-1',
        # 质检区交换机连接到核心交换机
        'switch-qc-1': 'switch-network-1'
    },
    # 网络区域连接
    'network': {
        # 两台服务器连接到核心交换机
        'server-mes-1': 'switch-network-1',
        'server-mbi-1': 'switch-network-1'
    }
}


def migrate_device_topologies():
    """执行迁移"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("开始迁移设备拓扑连接信息")
        print("=" * 60)

        created_count = 0
        updated_count = 0

        for station, connections in network_topology_data.items():
            print(f"\n处理工位: {station}")
            for source_code, target_code in connections.items():
                # 检查连接是否已存在
                existing = db.query(DeviceTopology).filter(
                    DeviceTopology.source_device_code == source_code,
                    DeviceTopology.target_device_code == target_code
                ).first()

                if existing:
                    # 更新现有连接
                    existing.connection_type = 'network'
                    existing.description = f"{station} 工位连接"
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                    print(f"  更新连接: {source_code} -> {target_code}")
                else:
                    # 创建新连接
                    topology = DeviceTopology(
                        source_device_code=source_code,
                        target_device_code=target_code,
                        connection_type='network',
                        description=f"{station} 工位连接"
                    )
                    db.add(topology)
                    created_count += 1
                    print(f"  创建连接: {source_code} -> {target_code}")

        db.commit()
        print(f"\n✓ 迁移完成: 创建 {created_count} 条连接, 更新 {updated_count} 条连接")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_device_topologies()

