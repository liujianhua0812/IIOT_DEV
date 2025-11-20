"""创建 tk_positions 表的脚本"""
import sys
from database import init_db, engine, Base, TK_Positions
from sqlalchemy import inspect


def main():
    """主函数"""
    print("正在连接数据库...")
    try:
        # 测试数据库连接
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        sys.exit(1)

    # 检查表是否已存在
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "tk_positions" in existing_tables:
        print("✓ tk_positions 表已存在")
        response = input("是否要删除并重新创建表？这将删除现有数据！(y/N): ")
        if response.lower() != 'y':
            print("已取消操作")
            return
        # 删除现有表
        TK_Positions.__table__.drop(engine, checkfirst=True)
        print("✓ 已删除现有表")

    print("正在创建 tk_positions 表...")
    try:
        # 只创建 tk_positions 表
        TK_Positions.__table__.create(engine, checkfirst=True)
        print("✓ tk_positions 表创建成功！")
        print("\n表结构：")
        print("  - id: 主键")
        print("  - item_type: 类型 (node/line/metadata)")
        print("  - item_id: 图块或连接线的唯一ID")
        print("  - base_label, label, x, y, color, item_type_code, fixed: 图块相关字段")
        print("  - start_x, start_y, end_x, end_y: 连接线相关字段")
        print("  - device_counters, node_id_counter, connection_line_id_counter: 元数据字段")
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

