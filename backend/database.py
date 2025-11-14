"""数据库连接和模型定义"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import db_config

# 创建数据库引擎
engine = create_engine(
    db_config.sqlalchemy_url,
    pool_pre_ping=True,
    echo=False,  # 设置为 True 可以看到 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class Organization(Base):
    """组织表（使用现有表结构）"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, comment="组织ID")
    name = Column(String(200), nullable=False, comment="组织名称")
    code = Column(String(100), nullable=True, comment="组织代码")
    parent_id = Column(Integer, nullable=True, comment="父组织ID")
    level = Column(Integer, nullable=True, comment="组织层级")
    region = Column(String(100), nullable=True, comment="所属区域")
    address = Column(String(500), nullable=True, comment="地址")
    contact = Column(String(100), nullable=True, comment="联系人")
    phone = Column(String(20), nullable=True, comment="联系电话")
    description = Column(Text, nullable=True, comment="组织描述")
    is_active = Column(Boolean, nullable=True, comment="是否激活")
    created_at = Column(DateTime, nullable=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    # 关联关系
    applications = relationship("Application", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Application(Base):
    """应用表"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, comment="应用ID")
    name = Column(String(100), nullable=False, comment="应用名称")
    english_name = Column(String(100), nullable=True, comment="应用英文名")
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, comment="所属组织ID")
    description = Column(Text, nullable=True, comment="应用描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    organization = relationship("Organization", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, name='{self.name}', organization_id={self.organization_id})>"


class Device(Base):
    """设备表"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, comment="设备ID")
    name = Column(String(200), nullable=False, comment="设备名称")
    code = Column(String(100), nullable=False, comment="设备编码")
    type = Column(String(50), nullable=False, comment="设备类型")
    model = Column(String(100), nullable=True, comment="设备型号")
    manufacturer = Column(String(100), nullable=True, comment="制造商")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    port = Column(Integer, nullable=True, comment="端口")
    mac_address = Column(String(50), nullable=True, comment="MAC地址")
    serial_number = Column(String(100), nullable=True, comment="序列号")
    longitude = Column(Float, nullable=True, comment="经度")
    latitude = Column(Float, nullable=True, comment="纬度")
    status = Column(String(20), nullable=True, comment="设备状态")
    health_status = Column(String(20), nullable=True, comment="健康状态")
    description = Column(Text, nullable=True, comment="设备描述")
    last_heartbeat = Column(DateTime, nullable=True, comment="最后心跳时间")
    created_at = Column(DateTime, nullable=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', code='{self.code}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type": self.type,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "ip_address": self.ip_address,
            "port": self.port,
            "mac_address": self.mac_address,
            "serial_number": self.serial_number,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "status": self.status,
            "health_status": self.health_status,
            "description": self.description,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

