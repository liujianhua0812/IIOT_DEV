import os
from dataclasses import dataclass
from typing import Literal

# 加载环境变量（如果使用 .env 文件）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# 运行模式：development 或 production
MODE = os.getenv("FLASK_ENV", "development").lower()
if MODE not in ["development", "production"]:
    MODE = "development"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def connection_string(self) -> str:
        """返回 PostgreSQL 连接字符串"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def sqlalchemy_url(self) -> str:
        """返回 SQLAlchemy 连接 URL"""
        return self.connection_string


def get_database_config() -> DatabaseConfig:
    """根据运行模式获取数据库配置"""
    if MODE == "production":
        # 部署模式：内网连接
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "192.168.34.14"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "iiotAdmin123"),
            database=os.getenv("DB_NAME", "iiot_platform"),
        )
    else:
        # 开发模式：优先使用环境变量，如果没有则使用内网数据库（因为外部数据库可能不可用）
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "192.168.34.14"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "iiotAdmin123"),
            database=os.getenv("DB_NAME", "iiot_platform"),
        )


db_config = get_database_config()

# 云侧模型访问控制配置
class CloudModelAccessConfig:
    """云侧模型访问控制配置"""
    
    # 模型配置
    MODEL_PATH = os.getenv("MODEL_PATH", "/home/1024zzp/project/zdyf/access_control/model_cloud/model/llama3-8b-Instruct")
    MODEL_DEVICE = os.getenv("MODEL_DEVICE", "auto")
    MODEL_DTYPE = "float16"
    
    # 数据配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIR = os.path.join(BASE_DIR, "..", "model_cloud", "dataset")
    ANCHOR_DATA_DIR = os.path.join(DATASET_DIR, "anchor_data")
    QUERY_DATA_DIR = os.path.join(DATASET_DIR, "query_data")
    
    # 结果存储配置
    RESULTS_DIR = os.path.join(BASE_DIR, "..", "model_cloud", "results")
    ANCHORS_DIR = os.path.join(RESULTS_DIR, "anchors")
    VISUALIZATIONS_DIR = os.path.join(RESULTS_DIR, "visualizations")
    CACHE_DIR = os.path.join(RESULTS_DIR, "cache")
    
    # 部门配置
    DEPARTMENTS = ["Marketing", "Technical", "Personnel", "Finance", "Operations"]
    
    # 职位等级配置
    POSITION_LEVELS = {
        "L1": {"name": "初级", "level": 1, "permissions": ["read"]},
        "L2": {"name": "中级", "level": 2, "permissions": ["read", "write"]},
        "L3": {"name": "高级", "level": 3, "permissions": ["read", "write", "admin"]},
        "L4": {"name": "专家", "level": 4, "permissions": ["read", "write", "admin", "super"]},
        "L5": {"name": "总监", "level": 5, "permissions": ["read", "write", "admin", "super", "executive"]}
    }
    
    # 锚点构建配置
    ANCHOR_CONFIG = {
        "num_samples_per_dept": 150,  # 每个部门的锚点样本数
        "num_samples_per_level": 100,  # 每个职位等级的锚点样本数
        "key_layers_count": 8,  # 关键层数量
        "activation_extraction": {
            "token_position": "last",  # last, mean, all
            "normalize": True
        }
    }
    
    # 激活偏移配置
    STEERING_CONFIG = {
        "base_alpha": 0.8,  # 转向强度
        "adaptive": True,  # 是否使用自适应alpha
        "tau": 8.0,  # ASI阈值
        "temperature": 5.0,  # 温度参数
        "mode": "differential",  # differential, absolute
        "inference_type": "aaac"  # aaac推理模式
    }
    
    # 访问控制配置
    ACCESS_CONTROL_CONFIG = {
        "tau_safe": 5.0,  # 安全阈值
        "tau_reject": 25.0,  # 拒绝阈值
        "enable_steering": True,  # 是否启用转向干预
        "max_response_length": 500  # 最大响应长度
    }
    
    # 可视化配置
    VIZ_CONFIG = {
        "mds_components": 2,
        "figsize": (12, 10),
        "dpi": 300,
        "color_map": {
            "Marketing": "#e74c3c",
            "Technical": "#3498db",
            "Personnel": "#2ecc71",
            "Finance": "#f39c12",
            "Operations": "#9b59b6"
        }
    }

# 初始化云侧模型访问控制配置
cloud_model_config = CloudModelAccessConfig()

