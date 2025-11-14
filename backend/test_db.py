"""测试数据库连接和表结构"""
from database import SessionLocal, Organization, Application
from sqlalchemy import inspect
from database import engine


def test_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("测试数据库连接和表结构")
    print("=" * 50)
    
    # 检查表是否存在
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n✓ 数据库中的表: {', '.join(tables)}")
    
    # 检查 organizations 表结构
    if "organizations" in tables:
        print("\n【organizations 表结构】")
        columns = inspector.get_columns("organizations")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} {'NOT NULL' if not col.get('nullable') else 'NULL'}")
    
    # 检查 applications 表结构
    if "applications" in tables:
        print("\n【applications 表结构】")
        columns = inspector.get_columns("applications")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} {'NOT NULL' if not col.get('nullable') else 'NULL'}")
        
        # 检查外键
        foreign_keys = inspector.get_foreign_keys("applications")
        print("\n【外键约束】")
        for fk in foreign_keys:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # 测试插入数据
    print("\n" + "=" * 50)
    print("测试插入数据")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查询现有组织（使用第一个组织进行测试）
        existing_org = db.query(Organization).first()
        if not existing_org:
            # 如果没有组织，创建一个测试组织
            org = Organization(
                name="测试组织",
                code="TEST_ORG",
                description="这是一个测试组织",
                is_active=True
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"\n✓ 创建组织成功: ID={org.id}, 名称={org.name}")
            test_org_id = org.id
            should_cleanup_org = True
        else:
            print(f"\n✓ 使用现有组织: ID={existing_org.id}, 名称={existing_org.name}")
            test_org_id = existing_org.id
            should_cleanup_org = False
        
        # 创建测试应用
        app = Application(
            name="测试应用",
            english_name="Test Application",
            organization_id=test_org_id,
            description="这是一个测试应用"
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        print(f"✓ 创建应用成功: ID={app.id}, 名称={app.name}, 组织ID={app.organization_id}")
        
        # 查询测试
        print("\n【查询测试】")
        orgs = db.query(Organization).limit(5).all()
        print(f"✓ 组织总数（前5个）: {len(orgs)}")
        for o in orgs:
            print(f"  - {o.name} (ID: {o.id})")
        
        apps = db.query(Application).limit(5).all()
        print(f"\n✓ 应用总数（前5个）: {len(apps)}")
        for a in apps:
            org_name = a.organization.name if a.organization else "未知"
            print(f"  - {a.name} (ID: {a.id}, 组织: {org_name})")
        
        # 清理测试数据
        print("\n【清理测试数据】")
        db.delete(app)
        if should_cleanup_org:
            db.delete(org)
        db.commit()
        print("✓ 测试数据已清理")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_connection()

