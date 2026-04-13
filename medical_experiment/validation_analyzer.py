"""
医学验证数据分析模块
验证AI分配算法的效果并生成医学验证报告
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path


@dataclass
class ValidationMetrics:
    """验证指标"""
    # 角色分配合理性
    prime_medical_match: float = 0.0   # PRIME角色医学专业人员匹配率
    prime_fitness_valid: float = 0.0   # PRIME角色体能有效性
    runner_fitness_valid: float = 0.0  # RUNNER角色体能有效性  
    guide_route_match: float = 0.0     # GUIDE角色路线熟悉度匹配率
    
    # 系统性能
    avg_response_time_ms: float = 0.0  # 平均响应时间
    success_rate: float = 0.0          # 分配成功率
    
    # 场景覆盖
    scenario_coverage: dict = field(default_factory=dict)


class ValidationAnalyzer:
    """验证分析器"""
    
    def __init__(self, results: list, scenarios_config: dict):
        self.results = results
        self.scenarios_config = scenarios_config
        
    def analyze_assignment_quality(self) -> ValidationMetrics:
        """分析分配质量"""
        
        metrics = ValidationMetrics()
        total = len(self.results)
        
        if total == 0:
            return metrics
            
        # 统计各指标
        prime_medical_count = 0
        prime_fitness_count = 0
        runner_fitness_count = 0
        guide_route_count = 0
        total_assigned = 0
        
        for result in self.results:
            assignments = result.get("assignments", {})
            candidates = result.get("candidates", [])
            candidate_map = {c["userId"]: c for c in candidates}
            
            # 检查每个角色的分配
            for role, user_id in assignments.items():
                if user_id is None:
                    continue
                    
                total_assigned += 1
                candidate = candidate_map.get(user_id, {})
                
                if role == "PRIME":
                    # 检查是否是医疗专业人员
                    profession = candidate.get("profession_identity", "")
                    if any(p in profession for p in ["医生", "护士", "急救员", "医护"]):
                        prime_medical_count += 1
                    
                    # 检查体能是否适合
                    fitness = candidate.get("fitness", "low")
                    if fitness in ["high", "medium"]:
                        prime_fitness_count += 1
                        
                elif role == "RUNNER":
                    # 检查体能是否适合跑步任务
                    fitness = candidate.get("fitness", "low")
                    if fitness in ["high", "medium"]:
                        runner_fitness_count += 1
                        
                elif role == "GUIDE":
                    # 检查是否熟悉环境
                    bio = candidate.get("profile_bio", "")
                    if any(kw in bio for kw in ["熟悉", "物业", "安保", "保安", "场地"]):
                        guide_route_count += 1
        
        # 计算比率
        role_counts = {"PRIME": 0, "RUNNER": 0, "GUIDE": 0}
        for r in self.results:
            for role in role_counts:
                if r.get("assignments", {}).get(role):
                    role_counts[role] += 1
        
        if role_counts["PRIME"] > 0:
            metrics.prime_medical_match = prime_medical_count / role_counts["PRIME"] * 100
            metrics.prime_fitness_valid = prime_fitness_count / role_counts["PRIME"] * 100
            
        if role_counts["RUNNER"] > 0:
            metrics.runner_fitness_valid = runner_fitness_count / role_counts["RUNNER"] * 100
            
        if role_counts["GUIDE"] > 0:
            metrics.guide_route_match = guide_route_count / role_counts["GUIDE"] * 100
        
        # 执行时间统计
        times = [r.get("execution_time_ms", 0) for r in self.results]
        metrics.avg_response_time_ms = sum(times) / len(times) if times else 0
        
        # 分配成功率
        metrics.success_rate = total_assigned / (total * 3) * 100  # 3个角色
        
        # 场景覆盖
        scenario_count = {}
        for r in self.results:
            scenario = r.get("scenario", "unknown")
            scenario_count[scenario] = scenario_count.get(scenario, 0) + 1
        metrics.scenario_coverage = scenario_count
        
        return metrics
    
    def generate_medical_validation_report(self) -> dict:
        """
        生成医学验证报告
        符合医创赛要求的格式
        """
        
        metrics = self.analyze_assignment_quality()
        
        report = {
            "report_title": "AI智能分配算法医学验证报告",
            "generated_at": datetime.now().isoformat(),
            "algorithm_description": {
                "name": "LifeReflex AI智能分配算法",
                "purpose": "基于大语言模型的急救现场多角色智能分配系统",
                "core_function": "根据患者画像和候选协助者画像，在PRIME（主施救者）、RUNNER（取机员）、GUIDE（引导员）三类任务中各选择最合适的人选",
                "medical_application": "院前急救协同调度",
            },
            "validation_methodology": {
                "approach": "模拟实验验证",
                "total_experiments": len(self.results),
                "scenarios": list(self.scenarios_config.keys()),
                "validation_data_type": "模拟生成的多场景急救数据",
            },
            "performance_metrics": {
                "allocation_success_rate": f"{metrics.success_rate:.1f}%",
                "avg_response_time": f"{metrics.avg_response_time_ms:.2f}ms",
                "prime_medical_professional_match_rate": f"{metrics.prime_medical_match:.1f}%",
                "prime_role_fitness_valid_rate": f"{metrics.prime_fitness_valid:.1f}%",
                "runner_role_fitness_valid_rate": f"{metrics.runner_fitness_valid:.1f}%",
                "guide_route_familiarity_match_rate": f"{metrics.guide_route_match:.1f}%",
            },
            "scenario_coverage": {
                name: {
                    "description": config.get("description", ""),
                    "experiment_count": count,
                }
                for name, count in metrics.scenario_coverage.items()
                for config in [self.scenarios_config.get(name, {})]
            },
            "conclusions": self._generate_conclusions(metrics),
            "clinical_feedback": self._generate_clinical_feedback(metrics),
        }
        
        return report
    
    def _generate_conclusions(self, metrics: ValidationMetrics) -> list:
        """生成结论"""
        
        conclusions = []
        
        # 分配成功率
        if metrics.success_rate >= 90:
            conclusions.append(f"AI分配算法成功率为{metrics.success_rate:.1f}%，能够稳定完成急救现场的角色分配任务")
        elif metrics.success_rate >= 70:
            conclusions.append(f"AI分配算法成功率为{metrics.success_rate:.1f}%，基本能够满足急救场景需求，建议优化")
        else:
            conclusions.append(f"AI分配算法成功率仅为{metrics.success_rate:.1}%，需要进一步优化算法")
        
        # PRIME角色医学专业匹配
        if metrics.prime_medical_match >= 60:
            conclusions.append(f"主施救者（PRIME）角色{metrics.prime_medical_match:.1f}%由医疗专业人员担任，符合急救医学要求")
        else:
            conclusions.append(f"主施救者（PRIME）角色仅有{metrics.prime_medical_match:.1f}%由医疗专业人员担任，建议优先分配有急救资质的人员")
        
        # 执行效率
        if metrics.avg_response_time_ms < 5000:
            conclusions.append(f"平均响应时间{metrics.avg_response_time_ms:.0f}ms，满足急救场景的时效性要求")
        else:
            conclusions.append(f"平均响应时间{metrics.avg_response_time_ms:.0f}ms，建议优化以满足急救场景需求")
        
        return conclusions
    
    def _generate_clinical_feedback(self, metrics: ValidationMetrics) -> dict:
        """生成临床反馈"""
        
        feedback = {
            "strengths": [],
            "limitations": [],
            "recommendations": [],
        }
        
        # 优势
        if metrics.success_rate >= 80:
            feedback["strengths"].append("高角色分配成功率，确保急救任务能够有效分配")
        if metrics.prime_medical_match >= 50:
            feedback["strengths"].append("能够优先将医疗专业人员分配到主施救者角色")
        if metrics.avg_response_time_ms < 3000:
            feedback["strengths"].append("响应速度快，满足急救场景的时效性要求")
            
        # 局限性
        if metrics.prime_medical_match < 50:
            feedback["limitations"].append("在非医疗场所场景下，医疗专业人员可能不足")
        if metrics.runner_fitness_valid < 80:
            feedback["limitations"].append("取机员角色体能匹配度有待提升")
            
        # 建议
        feedback["recommendations"].append("建议在实际部署中接入医疗专业人员数据库，优先调度有急救资质的人员")
        feedback["recommendations"].append("建议结合地理位置信息，优化取机员的分配策略")
        feedback["recommendations"].append("可引入更多特征（如跑步速度、历史响应时间等）进一步优化分配算法")
        
        return feedback
    
    def save_report(self, output_path: str):
        """保存验证报告"""
        
        report = self.generate_medical_validation_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"医学验证报告已保存至: {output_path}")
        
        return report


def run_validation_analysis(
    results_file: str,
    output_report: str = "medical_validation_report.json"
) -> dict:
    """运行验证分析"""
    
    from config import SCENARIO_CONFIGS
    
    # 加载实验结果
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        results = data.get("results", [])
    
    # 分析
    analyzer = ValidationAnalyzer(results, SCENARIO_CONFIGS)
    report = analyzer.save_report(output_report)
    
    # 打印摘要
    print("\n" + "="*60)
    print("医学验证报告摘要")
    print("="*60)
    print(f"\n算法名称: {report['algorithm_description']['name']}")
    print(f"医学应用: {report['algorithm_description']['medical_application']}")
    print(f"\n验证实验次数: {report['validation_methodology']['total_experiments']}")
    print(f"场景覆盖数: {len(report['validation_methodology']['scenarios'])}")
    
    print("\n【性能指标】")
    for key, value in report['performance_metrics'].items():
        print(f"  {key}: {value}")
    
    print("\n【结论】")
    for conclusion in report['conclusions']:
        print(f"  • {conclusion}")
    
    print("\n【临床反馈 - 优势】")
    for item in report['clinical_feedback']['strengths']:
        print(f"  ✓ {item}")
        
    print("\n【临床反馈 - 建议】")
    for item in report['clinical_feedback']['recommendations']:
        print(f"  → {item}")
    
    print("\n" + "="*60)
    
    return report


if __name__ == "__main__":
    import sys
    
    # 如果有结果文件，则进行分析
    if len(sys.argv) > 1:
        run_validation_analysis(sys.argv[1])
    else:
        print("请提供实验结果文件路径")
        print("用法: python validation_analyzer.py <results_file.json>")