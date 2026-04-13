"""
模拟急救场景数据生成器
生成符合真实分布的候选人画像和患者数据
"""

import random
import uuid
from datetime import datetime
from typing import Optional

from config import CANDIDATE_TEMPLATES, SCENARIO_CONFIGS, ExperimentConfig


class DataGenerator:
    """数据生成器"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.rng = random.Random()
        
    def set_seed(self, seed: int):
        """设置随机种子以确保可重复性"""
        self.rng = random.Random(seed)
        
    def generate_candidates(self, scenario: str, count: Optional[int] = None) -> list[dict]:
        """
        生成指定场景的候选人列表
        
        Args:
            scenario: 场景名称
            count: 候选人数目，默认随机
            
        Returns:
            候选人字典列表
        """
        if scenario not in SCENARIO_CONFIGS:
            raise ValueError(f"Unknown scenario: {scenario}")
            
        scenario_config = SCENARIO_CONFIGS[scenario]
        
        if count is None:
            count = self.rng.randint(
                self.config.min_candidates, 
                self.config.max_candidates
            )
            
        candidates = []
        
        # 根据场景配置生成候选人
        people_types = scenario_config["typical_people"]
        
        # 随机选择候选人类型组合
        remaining = count
        selected_types = []
        
        for people_type in people_types:
            min_count, max_count = people_type["count_range"]
            selected_count = min(remaining, self.rng.randint(min_count, max_count))
            selected_types.extend([people_type["profession"]] * selected_count)
            remaining -= selected_count
            if remaining <= 0:
                break
                
        # 补齐剩余名额
        while remaining > 0:
            selected_types.append(self.rng.choice(people_types)["profession"])
            remaining -= 1
            
        # 打乱顺序
        self.rng.shuffle(selected_types)
        
        # 为每个候选人选择画像模板
        for i, profession in enumerate(selected_types):
            template = self._select_template(profession, scenario)
            candidate = self._apply_template(template, i + 1)
            candidates.append(candidate)
            
        return candidates
    
    def _select_template(self, profession: str, scenario: str) -> dict:
        """根据职业选择合适的画像模板"""
        
        template_mapping = {
            "医生": "doctor",
            "护士": "nurse", 
            "急救员": "paramedic",
            "培训讲师": "first_aid_trained",
            "教练": "fitness_coach",
            "保安": "security",
            "物业": "property",
            "学生": "student",
            "员工": "office_worker",
            "老人": "elderly",
            "护理员": "nurse",
            "志愿者": "volunteer",
            "运动员": "fitness_coach",
            "前台": "office_worker",
            "工作人员": "first_aid_trained",
            "居民": "office_worker",
        }
        
        template_key = template_mapping.get(profession, "office_worker")
        
        # 根据场景调整模板
        if scenario == "sports_emergency" and profession == "运动员":
            template_key = "fitness_coach"
        elif scenario == "elderly_emergency" and profession == "护理员":
            template_key = "nurse"
            
        return CANDIDATE_TEMPLATES[template_key]
    
    def _apply_template(self, template: dict, index: int) -> dict:
        """应用画像模板并添加唯一标识"""
        import time
        # 随机调整一些属性以增加多样性
        bio_additions = [
            "熟悉附近环境",
            "有急救经验",
            "经常锻炼",
            "擅长沟通协调",
            "速度快",
            "反应敏捷",
        ]
        
        bio = template["profile_bio"]
        if self.rng.random() > 0.5:
            bio += "，" + self.rng.choice(bio_additions)
            
        return {
            "userId": f"user_{uuid.uuid4().hex[:8]}",
            "displayName": f"用户{index:02d}",
            "organization": self._random_organization(),
            "healthCondition": template["health_condition"],
            "professionIdentity": template["profession_identity"],
            "profileBio": bio,
            "deviceType": self.rng.choice(["ANDROID", "IOS", "WEB"]),
            "online": True,
            "lastSeenTs": int(time.time() * 1000),  # 当前时间戳（毫秒）
            "patientCandidate": False,
            "isPatient": False,
            "fitness": template["fitness"],  # 体能评分
            "distance": self._random_distance(),  # 距离患者的距离(米)
            # 位置信息（用于精确距离计算）
            "latitude": None,  # 将在生成后根据distance计算
            "longitude": None,
        }
    
    def _random_organization(self) -> str:
        """随机生成组织/单位"""
        
        organizations = [
            "本校学生", "本校教师", "XX大学", 
            "XX小区物业", "XX公司", "XX社区",
            "XX体育馆", "XX健身中心", "XX养老院",
            "XX医院", "XX卫生服务中心",
        ]
        return self.rng.choice(organizations)
    
    def _random_distance(self) -> int:
        """随机生成距离患者的距离(米)，模拟实际场景"""
        # 距离分布：大部分人在附近，少部分较远
        # 使用指数分布模拟真实情况
        distance = int(self.rng.expovariate(0.02))
        # 限制在1-200米范围内
        return max(1, min(200, distance))
    
    def generate_patient(self, scenario: str) -> dict:
        """
        生成患者数据
        
        Args:
            scenario: 场景名称
            
        Returns:
            患者字典
        """
        import time
        # 根据场景生成不同类型的患者
        if scenario == "elderly_emergency":
            return {
                "userId": f"patient_{uuid.uuid4().hex[:8]}",
                "displayName": "患者",
                "organization": "本地",
                "healthCondition": self.rng.choice(["心脏病史", "高血压", "有冠心病风险"]),
                "professionIdentity": "退休人员",
                "profileBio": "需要紧急救助",
                "deviceType": "ANDROID",
                "online": True,
                "lastSeenTs": int(time.time() * 1000),
                "patientCandidate": True,
                "isPatient": True,
            }
        else:
            return {
                "userId": f"patient_{uuid.uuid4().hex[:8]}",
                "displayName": "患者",
                "organization": "本地",
                "healthCondition": self.rng.choice(["健康", "亚健康", "有轻微心脏问题"]),
                "professionIdentity": self.rng.choice(["学生", "职员", "居民"]),
                "profileBio": "突然晕倒，需要紧急救助",
                "deviceType": "ANDROID",
                "online": True,
                "lastSeenTs": int(time.time() * 1000),
                "patientCandidate": True,
                "isPatient": True,
            }
    
    def generate_experiment_data(self) -> list[dict]:
        """
        生成完整的实验数据集
        
        Returns:
            实验数据列表，每项包含场景、患者和候选人
        """
        experiments = []
        
        for i in range(self.config.num_experiments):
            # 随机选择场景
            scenario = self.rng.choice(self.config.scenarios)
            
            # 生成患者和候选人
            patient = self.generate_patient(scenario)
            candidates = self.generate_candidates(scenario)
            
            experiments.append({
                "experiment_id": f"exp_{i+1:04d}",
                "scenario": scenario,
                "patient": patient,
                "candidates": candidates,
                "timestamp": datetime.now().isoformat(),
            })
            
        return experiments


def load_real_candidates() -> list[dict]:
    """
    从实际项目加载真实的候选人数据
    这是一个占位函数，实际应该从项目的客户端数据中获取
    """
    # 预留接口，可以从项目的实际运行数据中导入
    return []