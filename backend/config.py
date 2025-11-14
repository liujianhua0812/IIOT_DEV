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
        # 开发模式：外部连接
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "166.111.80.127"),
            port=int(os.getenv("DB_PORT", "15432")),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "iiotAdmin123"),
            database=os.getenv("DB_NAME", "iiot_platform"),
        )


db_config = get_database_config()

