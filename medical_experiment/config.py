"""
医学创新实验配置文件
用于生成模拟急救场景数据和验证AI分配算法
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / "ai_dispatch_config.yaml"


def load_config_from_yaml() -> dict:
    """从YAML配置文件加载配置"""
    config_path = CONFIG_FILE
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


# 加载YAML配置
YAML_CONFIG = load_config_from_yaml()


@dataclass
class ExperimentConfig:
    """实验配置"""
    # 实验名称
    name: str = "LifeReflex AI分配算法验证实验"
    
    # 实验次数
    num_experiments: int = 100
    
    # 每次实验的候选人数
    min_candidates: int = 5
    max_candidates: int = 15
    
    # 场景配置
    scenarios: list[str] = None
    
    # 是否使用AI模型（vs 规则引擎）
    use_ai_model: bool = True
    
    # 输出路径
    output_dir: str = "results"
    
    # API配置
    api_key: str = ""
    api_model: str = "Qwen/Qwen2.5-7B-Instruct"
    api_base_url: str = "https://api.siliconflow.cn/v1"
    api_timeout: int = 8
    
    def __post_init__(self):
        # 从YAML配置覆盖默认值
        if YAML_CONFIG:
            exp_config = YAML_CONFIG.get("experiment", {})
            sf_config = YAML_CONFIG.get("siliconflow", {})
            
            if exp_config:
                self.num_experiments = exp_config.get("num_experiments", self.num_experiments)
                self.min_candidates = exp_config.get("min_candidates", self.min_candidates)
                self.max_candidates = exp_config.get("max_candidates", self.max_candidates)
                self.use_ai_model = exp_config.get("use_ai_model", self.use_ai_model)
            
            if sf_config:
                self.api_key = sf_config.get("api_key", "")
                self.api_model = sf_config.get("model", self.api_model)
                self.api_base_url = sf_config.get("base_url", self.api_base_url)
                self.api_timeout = sf_config.get("timeout_sec", self.api_timeout)
        
        if self.scenarios is None:
            self.scenarios = [
                "campus_emergency",      # 校园急救
                "community_emergency",  # 社区急救  
                "workplace_emergency",  # 工作场所急救
                "sports_emergency",     # 运动场所急救
                "elderly_emergency",    # 老年人活动中心急救
            ]


@dataclass
class RoleAssignment:
    """角色分配结果"""
    role: Literal["PRIME", "RUNNER", "GUIDE"]
    user_id: str
    score: float
    reasoning: str


@dataclass
class ExperimentResult:
    """单次实验结果"""
    experiment_id: str
    scenario: str
    patient_id: str
    candidates: list
    assignments: dict
    dispatch_source: str  # "siliconflow" or "fallback"
    execution_time_ms: float
    timestamp: str


# 场景配置文件
SCENARIO_CONFIGS = {
    "campus_emergency": {
        "description": "校园急救场景",
        "location": "大学校园",
        "typical_people": [
            {"profession": "学生", "count_range": (3, 8), "fitness": "high"},
            {"profession": "教师", "count_range": (1, 3), "fitness": "medium"},
            {"profession": "校医", "count_range": (0, 1), "fitness": "medium"},
            {"profession": "保安", "count_range": (1, 2), "fitness": "medium"},
        ],
        "aed_distance_m": 200,
    },
    "community_emergency": {
        "description": "社区急救场景",
        "location": "居民小区",
        "typical_people": [
            {"profession": "居民", "count_range": (2, 6), "fitness": "low"},
            {"profession": "物业", "count_range": (1, 2), "fitness": "medium"},
            {"profession": "保安", "count_range": (1, 2), "fitness": "medium"},
        ],
        "aed_distance_m": 300,
    },
    "workplace_emergency": {
        "description": "工作场所急救场景",
        "location": "写字楼/办公楼",
        "typical_people": [
            {"profession": "员工", "count_range": (3, 8), "fitness": "medium"},
            {"profession": "前台", "count_range": (1, 1), "fitness": "medium"},
            {"profession": "保安", "count_range": (1, 2), "fitness": "medium"},
        ],
        "aed_distance_m": 150,
    },
    "sports_emergency": {
        "description": "运动场所急救场景",
        "location": "体育馆/健身房",
        "typical_people": [
            {"profession": "运动员", "count_range": (2, 5), "fitness": "high"},
            {"profession": "教练", "count_range": (1, 2), "fitness": "high"},
            {"profession": "工作人员", "count_range": (1, 2), "fitness": "medium"},
        ],
        "aed_distance_m": 100,
    },
    "elderly_emergency": {
        "description": "老年人活动中心急救场景",
        "location": "老年活动中心/养老院",
        "typical_people": [
            {"profession": "老人", "count_range": (2, 5), "fitness": "low"},
            {"profession": "护理员", "count_range": (1, 2), "fitness": "medium"},
            {"profession": "志愿者", "count_range": (1, 2), "fitness": "medium"},
        ],
        "aed_distance_m": 250,
    },
}


# 候选人画像模板
CANDIDATE_TEMPLATES = {
    # 医疗专业人员
    "doctor": {
        "profession_identity": "医生",
        "health_condition": "健康",
        "profile_bio": "持有执业医师资格证，接受过系统急救培训，有多年临床经验",
        "fitness": "high",
    },
    "nurse": {
        "profession_identity": "护士", 
        "health_condition": "健康",
        "profile_bio": "急诊科护士，熟练掌握CPR和AED操作，接受过专业急救训练",
        "fitness": "high",
    },
    "paramedic": {
        "profession_identity": "急救员",
        "health_condition": "健康",
        "profile_bio": "专业急救人员，持证上岗，熟悉各类急救场景",
        "fitness": "high",
    },
    # 普通有急救培训
    "first_aid_trained": {
        "profession_identity": "培训讲师",
        "health_condition": "健康",
        "profile_bio": "参加过红十字会急救培训，掌握心肺复苏和AED使用",
        "fitness": "medium",
    },
    "fitness_coach": {
        "profession_identity": "健身教练",
        "health_condition": "健康",
        "profile_bio": "体能优秀，跑得快，熟悉运动急救知识",
        "fitness": "high",
    },
    "security": {
        "profession_identity": "保安",
        "health_condition": "健康",
        "profile_bio": "负责场所安保，熟悉场地环境和应急通道",
        "fitness": "medium",
    },
    "property": {
        "profession_identity": "物业管理人员",
        "health_condition": "健康",
        "profile_bio": "熟悉楼宇结构，了解应急通道和电梯位置",
        "fitness": "medium",
    },
    "student": {
        "profession_identity": "学生",
        "health_condition": "健康",
        "profile_bio": "在校大学生，参加过急救知识讲座",
        "fitness": "high",
    },
    "office_worker": {
        "profession_identity": "公司职员",
        "health_condition": "亚健康",
        "profile_bio": "久坐办公，偶尔运动，了解基础急救知识",
        "fitness": "low",
    },
    "elderly": {
        "profession_identity": "退休人员",
        "health_condition": "有慢性病",
        "profile_bio": "年龄较大，行动缓慢，但有耐心和经验",
        "fitness": "low",
    },
    "volunteer": {
        "profession_identity": "社区志愿者",
        "health_condition": "健康",
        "profile_bio": "热心公益，经常参与社区活动，了解本地情况",
        "fitness": "medium",
    },
}