"""初始化 LaptopLabelTypes 表并生成示例数据"""
from datetime import datetime, timezone
from sqlalchemy import or_

from database import Base, engine, SessionLocal, LaptopLabelType, Application


TARGET_TOTAL = 152
IMAGE_PATH = "./data/labels/label.png"

BASE_LABEL_CONFIGS = [
    {"prefix": "Intel Core Ultra", "label_type": "CPU_PERFORMANCE", "length": 38.0, "width": 18.0},
    {"prefix": "Intel Evo", "label_type": "PLATFORM_CERT", "length": 34.5, "width": 21.0},
    {"prefix": "Intel vPro", "label_type": "ENTERPRISE_SECURITY", "length": 36.0, "width": 19.0},
    {"prefix": "Energy Star", "label_type": "ENERGY_SAVING", "length": 30.0, "width": 18.5},
    {"prefix": "Dolby Vision", "label_type": "DISPLAY_CERT", "length": 33.5, "width": 17.5},
    {"prefix": "Dolby Atmos", "label_type": "AUDIO_CERT", "length": 32.0, "width": 16.5},
    {"prefix": "Lenovo AI Engine", "label_type": "AI_OPTIMIZATION", "length": 40.0, "width": 20.0},
    {"prefix": "Lenovo Premium Care", "label_type": "SERVICE_WARRANTY", "length": 37.0, "width": 18.5},
    {"prefix": "Carbon Neutral", "label_type": "SUSTAINABILITY", "length": 35.0, "width": 15.5},
    {"prefix": "Recycled Material", "label_type": "MATERIAL_INFO", "length": 34.0, "width": 15.0},
    {"prefix": "Wi-Fi 7", "label_type": "CONNECTIVITY", "length": 28.0, "width": 16.0},
    {"prefix": "Bluetooth 5.3", "label_type": "WIRELESS", "length": 28.0, "width": 16.0},
    {"prefix": "PCIe Gen4 SSD", "label_type": "STORAGE", "length": 31.0, "width": 14.5},
    {"prefix": "LPDDR5X Memory", "label_type": "MEMORY", "length": 31.5, "width": 15.0},
    {"prefix": "Thunderbolt 4", "label_type": "IO_PORT", "length": 29.0, "width": 14.0},
    {"prefix": "NVIDIA RTX Studio", "label_type": "GPU_CERT", "length": 39.0, "width": 19.0},
]


def get_default_application_id(session):
    """获取需要关联的应用ID"""
    preferred = session.query(Application).filter(
        or_(Application.name == "LenovoFMS", Application.english_name == "LenovoFMS")
    ).first()
    if preferred:
        return preferred.id

    fallback = session.query(Application).first()
    return fallback.id if fallback else None


def build_label_payload(index, application_id):
    base = BASE_LABEL_CONFIGS[index % len(BASE_LABEL_CONFIGS)]
    variant = index // len(BASE_LABEL_CONFIGS) + 1

    length_adjust = (variant % 5) * 0.4
    width_adjust = (variant % 3) * 0.3

    return {
        "name": f"{base['prefix']} 标签 {variant:03d}",
        "label_type": base["label_type"],
        "length_mm": round(base["length"] + length_adjust, 2),
        "width_mm": round(base["width"] + width_adjust, 2),
        "image_path": IMAGE_PATH,
        "application_id": application_id,
        "description": f"{base['prefix']} 认证/贴标示例（批次 {variant:03d}）",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def seed_laptop_label_types():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        application_id = get_default_application_id(session)
        if not application_id:
            raise RuntimeError("无法找到任何应用，无法为标签类型设置 application_id。请先创建应用。")

        existing_names = {name for (name,) in session.query(LaptopLabelType.name).all()}
        if len(existing_names) >= TARGET_TOTAL:
            print(f"LaptopLabelTypes 表已存在 {len(existing_names)} 条数据，无需重复创建。")
            return

        records_to_create = []
        index = 0
        while len(existing_names) + len(records_to_create) < TARGET_TOTAL:
            payload = build_label_payload(index, application_id)
            if payload["name"] not in existing_names:
                records_to_create.append(LaptopLabelType(**payload))
            index += 1

        session.bulk_save_objects(records_to_create)
        session.commit()
        print(f"成功写入 {len(records_to_create)} 条标签类型数据，总计 {len(existing_names) + len(records_to_create)} 条。")
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


if __name__ == "__main__":
    seed_laptop_label_types()

