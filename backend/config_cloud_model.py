"""
云侧模型访问控制配置文件
"""
import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).resolve().parent

# 模型配置
MODEL_CONFIG = {
    "model_path": os.getenv("MODEL_PATH", "meta-llama/Meta-Llama-3-8B-Instruct"),
    "device": os.getenv("MODEL_DEVICE", "cpu"),  # cpu, cuda, auto
    "dtype": os.getenv("MODEL_DTYPE", "float16"),
    "max_response_length": 500,
}

# 锚点配置
ANCHOR_CONFIG = {
    "anchors_dir": os.getenv("ANCHORS_DIR", str(BASE_DIR / "data/anchors")),
    "num_samples_per_department": 50,
    "num_samples_per_level": 30,
    "top_k_layers": 10,
    "activation_extraction": {
        "token_position": "last",
        "normalize": True,
    },
}

# 转向配置
STEERING_CONFIG = {
    "base_alpha": 0.5,
    "tau": 10.0,
    "temperature": 2.0,
    "adaptive": True,
    "mode": "differential",
    "inference_type": "aaac",
}

# 访问控制配置
ACCESS_CONTROL_CONFIG = {
    "tau_safe": 8.0,
    "tau_reject": 15.0,
    "max_response_length": 500,
}

# 部门和职位等级定义
DEPARTMENTS = ["Marketing", "Technical", "Personnel", "Finance", "Operations"]

POSITION_LEVELS = {
    "L1": "初级员工",
    "L2": "中级员工",
    "L3": "高级员工",
    "L4": "经理",
    "L5": "高级经理",
}