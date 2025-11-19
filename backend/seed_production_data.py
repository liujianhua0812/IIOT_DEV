"""Seed production-related tables with mock data."""
import random
import string
from datetime import datetime, timedelta, date, timezone

from database import (
    Base,
    engine,
    SessionLocal,
    ProductType,
    ProductionOrder,
    ProductionProduct,
)

TARGET_PRODUCT_TYPES = 6
TARGET_ORDERS = 30
TARGET_PRODUCTS = 100


PRODUCT_TYPE_TEMPLATES = [
    {
        "product_code": "LNV-FMS-ULTRA-14",
        "product_name": "Lenovo FMS Ultra 14\"",
        "rule_file": "./data/rules/lenovo_fms_ultra_14.yaml",
    },
    {
        "product_code": "LNV-EDGE-15",
        "product_name": "Lenovo Edge 15\"",
        "rule_file": "./data/rules/lenovo_edge_15.yaml",
    },
    {
        "product_code": "LNV-CARBON-13",
        "product_name": "Lenovo Carbon 13\"",
        "rule_file": "./data/rules/lenovo_carbon_13.yaml",
    },
    {
        "product_code": "LNV-PRO-16",
        "product_name": "Lenovo Pro 16\"",
        "rule_file": "./data/rules/lenovo_pro_16.yaml",
    },
    {
        "product_code": "LNV-GAMING-17",
        "product_name": "Lenovo Gaming 17\"",
        "rule_file": "./data/rules/lenovo_gaming_17.yaml",
    },
    {
        "product_code": "LNV-ATELIER-14",
        "product_name": "Lenovo Atelier 14\"",
        "rule_file": "./data/rules/lenovo_atelier_14.yaml",
    },
]

ORDER_STATUSES = ["planned", "scheduled", "in_progress", "completed", "delayed"]
PRODUCT_STATUSES = ["assembling", "testing", "packaged", "shipped", "hold"]


def ensure_product_types(session):
    existing_codes = {
        pt.product_code for pt in session.query(ProductType.product_code).all()
    }
    created = 0
    for template in PRODUCT_TYPE_TEMPLATES:
        if template["product_code"] not in existing_codes:
            session.add(
                ProductType(
                    product_code=template["product_code"],
                    product_name=template["product_name"],
                    rule_file_path=template["rule_file"],
                    description=f"{template['product_name']} 生产规则",
                )
            )
            created += 1
    if created:
        session.commit()
    return session.query(ProductType).all()


def random_date(base: date, *, min_offset=-10, max_offset=25):
    return base + timedelta(days=random.randint(min_offset, max_offset))


def ensure_orders(session, product_types):
    orders = session.query(ProductionOrder).all()
    if len(orders) >= TARGET_ORDERS:
        return orders

    base_date = date.today()
    for idx in range(TARGET_ORDERS - len(orders)):
        product_type = random.choice(product_types)
        scheduled = random_date(base_date, min_offset=-5, max_offset=10)
        delivery = scheduled + timedelta(days=random.randint(5, 20))
        order_code = f"ORD-{base_date.strftime('%Y%m')}-{len(orders)+idx+1:04d}"

        order = ProductionOrder(
            order_code=order_code,
            product_code=product_type.product_code,
            product_type_id=product_type.id,
            quantity=random.randint(20, 200),
            scheduled_date=scheduled,
            delivery_date=delivery,
            status=random.choice(ORDER_STATUSES),
            remarks=f"{product_type.product_name} 批次生产",
        )
        session.add(order)
    session.commit()
    return session.query(ProductionOrder).all()


def generate_serial_number(product_code, counter):
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{product_code}-{datetime.now(timezone.utc).strftime('%y%m%d')}-{counter:04d}-{suffix}"


def ensure_products(session, product_types, orders):
    existing_serials = {
        serial for (serial,) in session.query(ProductionProduct.serial_number).all()
    }
    products_needed = TARGET_PRODUCTS - len(existing_serials)
    if products_needed <= 0:
        return

    counter = len(existing_serials) + 1
    for _ in range(products_needed):
        order = random.choice(orders)
        product_type = next(
            (pt for pt in product_types if pt.id == order.product_type_id),
            random.choice(product_types),
        )
        serial = generate_serial_number(order.product_code, counter)
        counter += 1

        product = ProductionProduct(
            serial_number=serial,
            order_id=order.id,
            product_type_id=product_type.id,
            status=random.choice(PRODUCT_STATUSES),
            produced_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 10)),
            description=f"{product_type.product_name} 序列号 {serial}",
        )
        session.add(product)
    session.commit()


def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        product_types = ensure_product_types(session)
        if not product_types:
            raise RuntimeError("未能创建产品类型，无法继续。")

        orders = ensure_orders(session, product_types)
        if not orders:
            raise RuntimeError("未能生成生产订单，无法继续。")

        ensure_products(session, product_types, orders)
        print(
            "生产数据已准备完成："
            f"{session.query(ProductType).count()} 种产品类型，"
            f"{session.query(ProductionOrder).count()} 条订单，"
            f"{session.query(ProductionProduct).count()} 条产品记录。"
        )
    finally:
        session.close()


if __name__ == "__main__":
    seed()

