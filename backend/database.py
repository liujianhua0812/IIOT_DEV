"""数据库连接和模型定义"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
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


class DeviceType(Base):
    """设备类型表"""
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, index=True, comment="设备类型ID")
    code = Column(String(50), nullable=False, unique=True, comment="类型代码（唯一标识）")
    name = Column(String(100), nullable=False, comment="类型名称")
    description = Column(Text, nullable=True, comment="类型描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    parameters = relationship("DeviceTypeParameter", back_populates="device_type", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="device_type")

    def __repr__(self):
        return f"<DeviceType(id={self.id}, code='{self.code}', name='{self.name}')>"

    def to_dict(self):
        """转换为字典格式"""
        # 确保参数按 sort_order 排序
        sorted_params = []
        if self.parameters:
            sorted_params = sorted(self.parameters, key=lambda p: p.sort_order if p.sort_order is not None else 999)
        
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "parameters": [param.to_dict() for param in sorted_params],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DeviceTypeParameter(Base):
    """设备类型参数表"""
    __tablename__ = "device_type_parameters"
    __table_args__ = (
        UniqueConstraint('device_type_id', 'param_key', name='uq_device_type_param'),
    )

    id = Column(Integer, primary_key=True, index=True, comment="参数ID")
    device_type_id = Column(Integer, ForeignKey("device_types.id", ondelete="CASCADE"), nullable=False, comment="关联设备类型ID")
    param_key = Column(String(50), nullable=False, comment="参数键（英文）")
    param_name = Column(String(100), nullable=False, comment="参数名称（中文）")
    param_type = Column(String(20), nullable=False, comment="参数类型（string, number, boolean, date）")
    required = Column(Boolean, default=False, comment="是否必填")
    default_value = Column(Text, nullable=True, comment="默认值")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序（数字越小越靠前）")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    device_type = relationship("DeviceType", back_populates="parameters")
    device_values = relationship("DeviceParameterValue", back_populates="parameter", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DeviceTypeParameter(id={self.id}, param_key='{self.param_key}', param_name='{self.param_name}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "key": self.param_key,
            "name": self.param_name,
            "type": self.param_type,
            "required": self.required,
            "default_value": self.default_value,
            "sort_order": self.sort_order,
        }


class Device(Base):
    """设备表"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, comment="设备ID")
    name = Column(String(200), nullable=False, comment="设备名称")
    code = Column(String(100), nullable=False, unique=True, comment="设备编码（唯一）")
    device_type_id = Column(Integer, ForeignKey("device_types.id", ondelete="SET NULL"), nullable=True, comment="关联设备类型ID")
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True, comment="所属应用程序ID")
    position_x = Column(Float, nullable=True, comment="显示X坐标")
    position_y = Column(Float, nullable=True, comment="显示Y坐标")
    serial_number = Column(String(100), nullable=True, comment="序列号")
    longitude = Column(Float, nullable=True, comment="经度")
    latitude = Column(Float, nullable=True, comment="纬度")
    status = Column(String(20), nullable=True, comment="设备状态")
    health_status = Column(String(20), nullable=True, comment="健康状态")
    description = Column(Text, nullable=True, comment="设备描述")
    last_heartbeat = Column(DateTime, nullable=True, comment="最后心跳时间")
    created_at = Column(DateTime, nullable=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    device_type = relationship("DeviceType", back_populates="devices")
    application = relationship("Application", backref="devices")
    parameter_values = relationship("DeviceParameterValue", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', code='{self.code}')>"

    def to_dict(self, include_parameters=False):
        """转换为字典格式"""
        # 从参数值中获取 ip_address 和 port（用于列表显示）
        ip_address = None
        port = None
        parameters = {}
        if self.parameter_values:
            for pv in self.parameter_values:
                if include_parameters:
                    parameters[pv.param_key] = pv.param_value
                if pv.param_key == "ip_address":
                    ip_address = pv.param_value
                elif pv.param_key == "port":
                    port = pv.param_value
        
        # 转换 port 为整数（如果可能）
        port_int = None
        if port:
            try:
                port_int = int(port)
            except (ValueError, TypeError):
                port_int = port
        
        result = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "device_type_id": self.device_type_id,
            "type": self.device_type.code if self.device_type else None,
            "device_type": self.device_type.to_dict() if self.device_type else None,
            "application_id": self.application_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "ip_address": ip_address,
            "port": port_int,
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
        
        if include_parameters:
            result["parameters"] = parameters
        
        return result


class DeviceParameterValue(Base):
    """设备参数值表"""
    __tablename__ = "device_parameter_values"
    __table_args__ = (
        UniqueConstraint('device_id', 'param_key', name='uq_device_param'),
    )

    id = Column(Integer, primary_key=True, index=True, comment="参数值ID")
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, comment="关联设备ID")
    parameter_id = Column(Integer, ForeignKey("device_type_parameters.id", ondelete="CASCADE"), nullable=False, comment="关联参数ID")
    param_key = Column(String(50), nullable=False, comment="参数键（冗余字段，便于查询）")
    param_value = Column(Text, nullable=True, comment="参数值")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    device = relationship("Device", back_populates="parameter_values")
    parameter = relationship("DeviceTypeParameter", back_populates="device_values")

    def __repr__(self):
        return f"<DeviceParameterValue(id={self.id}, device_id={self.device_id}, param_key='{self.param_key}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "parameter_id": self.parameter_id,
            "param_key": self.param_key,
            "param_value": self.param_value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LaptopLabelType(Base):
    """笔记本贴标类型表"""
    __tablename__ = "laptop_label_types"

    id = Column(Integer, primary_key=True, index=True, comment="标签类型ID")
    name = Column(String(200), nullable=False, comment="标签名称")
    label_type = Column(String(100), nullable=False, comment="标签类别")
    length_mm = Column(Float, nullable=True, comment="标签长度（mm）")
    width_mm = Column(Float, nullable=True, comment="标签宽度（mm）")
    image_path = Column(String(500), nullable=False, comment="标签图片路径")
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        comment="所属应用ID",
    )
    description = Column(Text, nullable=True, comment="标签描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    application = relationship("Application", backref="laptop_label_types")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "label_type": self.label_type,
            "length_mm": self.length_mm,
            "width_mm": self.width_mm,
            "image_path": self.image_path,
            "application_id": self.application_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<LaptopLabelType(id={self.id}, name='{self.name}', label_type='{self.label_type}')>"


class ProductType(Base):
    """产品类型表（笔记本机型）"""
    __tablename__ = "product_types"

    id = Column(Integer, primary_key=True, index=True, comment="产品类型ID")
    product_code = Column(String(100), nullable=False, unique=True, comment="产品编号")
    product_name = Column(String(200), nullable=False, comment="产品名称")
    rule_file_path = Column(String(500), nullable=True, comment="产品规则文件路径")
    description = Column(Text, nullable=True, comment="产品描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    orders = relationship("ProductionOrder", back_populates="product_type", cascade="all, delete-orphan")
    products = relationship("ProductionProduct", back_populates="product_type")

    def __repr__(self):
        return f"<ProductType(id={self.id}, code='{self.product_code}', name='{self.product_name}')>"


class ProductionOrder(Base):
    """生产订单表"""
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    order_code = Column(String(100), nullable=True, unique=True, comment="订单编号")
    product_code = Column(String(100), nullable=False, comment="产品编号（冗余）")
    product_type_id = Column(Integer, ForeignKey("product_types.id", ondelete="SET NULL"), nullable=True, comment="产品类型ID")
    quantity = Column(Integer, nullable=False, default=0, comment="产品数量")
    scheduled_date = Column(Date, nullable=True, comment="排产日期")
    delivery_date = Column(Date, nullable=True, comment="交付日期")
    status = Column(String(50), nullable=True, comment="订单状态")
    remarks = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    product_type = relationship("ProductType", back_populates="orders")
    products = relationship("ProductionProduct", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductionOrder(id={self.id}, order_code='{self.order_code}', product_code='{self.product_code}')>"


class ProductionProduct(Base):
    """生产产品表（具体序列号）"""
    __tablename__ = "production_products"

    id = Column(Integer, primary_key=True, index=True, comment="产品记录ID")
    serial_number = Column(String(150), nullable=False, unique=True, comment="产品序列号")
    order_id = Column(Integer, ForeignKey("production_orders.id", ondelete="SET NULL"), nullable=True, comment="所属订单ID")
    product_type_id = Column(Integer, ForeignKey("product_types.id", ondelete="SET NULL"), nullable=True, comment="产品类型ID")
    status = Column(String(50), nullable=True, comment="产品状态")
    produced_at = Column(DateTime, nullable=True, comment="生产完成时间")
    produced_end = Column(DateTime, nullable=True, comment="生产完成时间（精确时间点）")
    description = Column(Text, nullable=True, comment="备注信息")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    order = relationship("ProductionOrder", back_populates="products")
    product_type = relationship("ProductType", back_populates="products")

    def __repr__(self):
        return f"<ProductionProduct(id={self.id}, serial_number='{self.serial_number}')>"


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    email = Column(String(100), nullable=False, unique=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典格式（不包含密码）"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class DeviceTopology(Base):
    """设备拓扑连接表"""
    __tablename__ = "device_topologies"

    id = Column(Integer, primary_key=True, index=True, comment="连接ID")
    source_device_code = Column(String(100), nullable=False, comment="源设备编码")
    target_device_code = Column(String(100), nullable=False, comment="目标设备编码")
    connection_type = Column(String(50), nullable=True, comment="连接类型（如：network, control等）")
    description = Column(Text, nullable=True, comment="连接描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 唯一约束：同一对设备只能有一条连接
    __table_args__ = (
        UniqueConstraint('source_device_code', 'target_device_code', name='uq_device_topology'),
    )

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "source_device_code": self.source_device_code,
            "target_device_code": self.target_device_code,
            "connection_type": self.connection_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<DeviceTopology(id={self.id}, source='{self.source_device_code}', target='{self.target_device_code}')>"


class VideoStream(Base):
    """视频流表"""
    __tablename__ = "video_streams"

    id = Column(Integer, primary_key=True, index=True, comment="视频流ID")
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, comment="设备ID")
    stream_name = Column(String(200), nullable=False, comment="流名称")
    stream_url = Column(String(500), nullable=True, comment="流URL（RTSP/HTTP/HLS等）")
    file_path = Column(String(500), nullable=True, comment="视频文件路径")
    stream_type = Column(String(50), nullable=True, default="file", comment="流类型: file/rtsp/http/hls")
    status = Column(String(20), nullable=True, default="active", comment="状态: active/inactive")
    resolution = Column(String(50), nullable=True, comment="分辨率")
    bitrate = Column(Integer, nullable=True, comment="码率(kbps)")
    fps = Column(Integer, nullable=True, comment="帧率")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关联关系
    device = relationship("Device", backref="video_streams")

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "stream_name": self.stream_name,
            "stream_url": self.stream_url,
            "file_path": self.file_path,
            "stream_type": self.stream_type,
            "status": self.status,
            "resolution": self.resolution,
            "bitrate": self.bitrate,
            "fps": self.fps,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<VideoStream(id={self.id}, device_id={self.device_id}, stream_name='{self.stream_name}')>"


class TK_Positions(Base):
    """图块和连接线位置表"""
    __tablename__ = "tk_positions"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    item_type = Column(String(20), nullable=False, comment="类型: node(图块) 或 line(连接线)")
    item_id = Column(String(100), nullable=False, comment="图块或连接线的唯一ID")
    base_label = Column(String(100), nullable=True, comment="图块的基础标签（仅图块有）")
    label = Column(String(100), nullable=True, comment="图块或连接线的显示标签（仅图块有）")
    x = Column(Float, nullable=True, comment="X坐标（百分比）")
    y = Column(Float, nullable=True, comment="Y坐标（百分比）")
    start_x = Column(Float, nullable=True, comment="连接线起点X坐标（仅连接线有）")
    start_y = Column(Float, nullable=True, comment="连接线起点Y坐标（仅连接线有）")
    end_x = Column(Float, nullable=True, comment="连接线终点X坐标（仅连接线有）")
    end_y = Column(Float, nullable=True, comment="连接线终点Y坐标（仅连接线有）")
    color = Column(String(20), nullable=True, comment="图块颜色（仅图块有）")
    item_type_code = Column(String(50), nullable=True, comment="图块类型代码（仅图块有）")
    fixed = Column(Boolean, nullable=True, default=False, comment="是否固定（仅图块有）")
    device_counters = Column(Text, nullable=True, comment="设备计数器JSON（用于图块命名）")
    node_id_counter = Column(Integer, nullable=True, default=0, comment="节点ID计数器")
    connection_line_id_counter = Column(Integer, nullable=True, default=0, comment="连接线ID计数器")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "base_label": self.base_label,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y,
            "color": self.color,
            "item_type_code": self.item_type_code,
            "fixed": self.fixed,
            "device_counters": self.device_counters,
            "node_id_counter": self.node_id_counter,
            "connection_line_id_counter": self.connection_line_id_counter,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<TK_Positions(id={self.id}, item_type='{self.item_type}', item_id='{self.item_id}')>"


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

