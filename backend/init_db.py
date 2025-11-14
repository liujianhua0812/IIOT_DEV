"""数据库初始化脚本"""
import sys
from database import init_db, engine, Base
from sqlalchemy import inspect


def check_tables_exist():
    """检查表是否已存在"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return "organizations" in existing_tables and "applications" in existing_tables


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

    if check_tables_exist():
        print("✓ 表已存在，跳过创建")
        response = input("是否要重新创建表？这将删除现有数据！(y/N): ")
        if response.lower() != 'y':
            print("已取消操作")
            return
        # 删除现有表
        Base.metadata.drop_all(bind=engine)
        print("✓ 已删除现有表")

    print("正在创建数据库表...")
    try:
        init_db()
        print("✓ 数据库表创建成功！")
        print("\n已创建的表：")
        print("  - organizations (组织表)")
        print("  - applications (应用表)")
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

