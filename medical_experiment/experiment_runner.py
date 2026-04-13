"""
AI分配算法验证实验模块
使用模拟数据验证AI分配算法的效果
"""

import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# 将原项目的dispatch_ai模块路径添加到sys.path
PROJECT_ROOT = Path(__file__).parent.parent / "software_innovation" / "Semifinal" / "project" / "server（云端服务）"
sys.path.insert(0, str(PROJECT_ROOT))

from config import ExperimentConfig, ExperimentResult, SCENARIO_CONFIGS
from data_generator import DataGenerator
from client_info import ClientInfo


class ExperimentRunner:
    """实验运行器"""
    
    def __init__(self, config: ExperimentConfig, output_dir: str = "results"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.generator = DataGenerator(config)
        self.results: list[ExperimentResult] = []
        
    def run_single_experiment(
        self, 
        experiment_id: str, 
        scenario: str,
        patient: dict,
        candidates: list[dict],
        use_ai: bool = True
    ) -> ExperimentResult:
        """运行单次实验"""
        
        from app.services.dispatch_ai import DispatchPlanner
        
        # 直接使用本地ClientInfo（dataclass）
        patient_client = ClientInfo(**patient)
        
        # 转换候选人数据
        candidate_clients = [ClientInfo(**c) for c in candidates]
        
        # 创建调度器
        # 优先使用配置文件中的API Key，其次环境变量
        api_key = self.config.api_key or os.environ.get("SILICONFLOW_API_KEY")
        
        dispatch_planner = DispatchPlanner(
            api_key=api_key if use_ai else None,
            model=self.config.api_model,
            base_url=self.config.api_base_url,
            timeout_sec=self.config.api_timeout,
        )
        
        # 执行分配
        start_time = time.time()
        assignments, source = dispatch_planner.assign_roles(
            patient_client.userId, 
            candidate_clients
        )
        execution_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 记录结果
        # 保存完整的候选人信息用于后续分析
        candidates_full = []
        for c in candidates:
            candidates_full.append({
                "userId": c["userId"],
                "displayName": c["displayName"],
                "professionIdentity": c["professionIdentity"],
                "fitness": c.get("fitness", "medium"),
                "healthCondition": c.get("healthCondition", "healthy"),
                "distance": c.get("distance", 50),  # 距离患者的米数
            })
        
        result = ExperimentResult(
            experiment_id=experiment_id,
            scenario=scenario,
            patient_id=patient["userId"],
            candidates=candidates_full,  # 保存完整候选人信息
            assignments=assignments,
            dispatch_source=source,
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat(),
        )
        
        return result
    
    def run_all_experiments(self, seed: int = 42) -> list[ExperimentResult]:
        """运行所有实验"""
        
        self.generator.set_seed(seed)
        experiment_data = self.generator.generate_experiment_data()
        
        print(f"开始运行 {len(experiment_data)} 次实验...")
        
        for i, data in enumerate(experiment_data):
            result = self.run_single_experiment(
                experiment_id=data["experiment_id"],
                scenario=data["scenario"],
                patient=data["patient"],
                candidates=data["candidates"],
                use_ai=self.config.use_ai_model,
            )
            self.results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"已完成 {i+1}/{len(experiment_data)} 次实验")
                
        print(f"实验完成！共 {len(self.results)} 次实验")
        
        return self.results
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """保存实验结果到文件"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experiment_results_{timestamp}.json"
            
        filepath = self.output_dir / filename
        
        # 转换为可序列化的格式
        results_data = []
        for r in self.results:
            results_data.append({
                "experiment_id": r.experiment_id,
                "scenario": r.scenario,
                "patient_id": r.patient_id,
                "candidates": r.candidates,
                "assignments": r.assignments,
                "dispatch_source": r.dispatch_source,
                "execution_time_ms": r.execution_time_ms,
                "timestamp": r.timestamp,
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "config": {
                    "name": self.config.name,
                    "num_experiments": self.config.num_experiments,
                    "scenarios": self.config.scenarios,
                    "use_ai_model": self.config.use_ai_model,
                },
                "results": results_data,
            }, f, ensure_ascii=False, indent=2)
            
        return str(filepath)


class ResultAnalyzer:
    """实验结果分析器"""
    
    def __init__(self, results: list[ExperimentResult]):
        self.results = results
        
    def generate_report(self) -> dict:
        """生成分析报告"""
        
        total = len(self.results)
        if total == 0:
            return {"error": "No results to analyze"}
            
        # 基本统计
        ai_success = sum(1 for r in self.results if r.dispatch_source == "siliconflow")
        fallback_count = sum(1 for r in self.results if r.dispatch_source == "fallback")
        
        # 场景分布
        scenarios = {}
        for r in self.results:
            scenarios[r.scenario] = scenarios.get(r.scenario, 0) + 1
            
        # 分配成功率
        assignment_rates = {}
        for role in ["PRIME", "RUNNER", "GUIDE"]:
            assigned = sum(1 for r in self.results 
                          if r.assignments.get(role) is not None)
            assignment_rates[role] = assigned / total * 100
            
        # 执行时间统计
        exec_times = [r.execution_time_ms for r in self.results]
        avg_time = sum(exec_times) / total
        max_time = max(exec_times)
        min_time = min(exec_times)
        
        # 候选人数量分布
        candidate_counts = [len(r.candidates) for r in self.results]
        avg_candidates = sum(candidate_counts) / total
        
        report = {
            "summary": {
                "total_experiments": total,
                "ai_success_rate": ai_success / total * 100,
                "fallback_rate": fallback_count / total * 100,
            },
            "scenarios": scenarios,
            "assignment_rates": assignment_rates,
            "execution_time": {
                "avg_ms": round(avg_time, 2),
                "max_ms": round(max_time, 2),
                "min_ms": round(min_time, 2),
            },
            "candidates": {
                "avg_count": round(avg_candidates, 2),
                "min_count": min(candidate_counts),
                "max_count": max(candidate_counts),
            },
        }
        
        return report
    
    def print_report(self):
        """打印分析报告"""
        
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("AI分配算法验证实验报告")
        print("="*60)
        
        print("\n【基本信息】")
        print(f"  实验总次数: {report['summary']['total_experiments']}")
        print(f"  AI模式成功率: {report['summary']['ai_success_rate']:.1f}%")
        print(f"  备用模式比例: {report['summary']['fallback_rate']:.1f}%")
        
        print("\n【场景分布】")
        for scenario, count in report['scenarios'].items():
            config = SCENARIO_CONFIGS.get(scenario, {})
            desc = config.get("description", scenario)
            print(f"  {desc}: {count}次 ({count/report['summary']['total_experiments']*100:.1f}%)")
        
        print("\n【角色分配成功率】")
        for role, rate in report['assignment_rates'].items():
            role_names = {"PRIME": "主施救者", "RUNNER": "取机员", "GUIDE": "引导员"}
            print(f"  {role_names.get(role, role)}: {rate:.1f}%")
        
        print("\n【执行时间】")
        print(f"  平均: {report['execution_time']['avg_ms']:.2f} ms")
        print(f"  最快: {report['execution_time']['min_ms']:.2f} ms")
        print(f"  最慢: {report['execution_time']['max_ms']:.2f} ms")
        
        print("\n【候选人统计】")
        print(f"  平均人数: {report['candidates']['avg_count']:.1f}")
        print(f"  范围: {report['candidates']['min_count']} - {report['candidates']['max_count']}")
        
        print("\n" + "="*60)
        
        return report
    
    def export_csv(self, output_path: str):
        """导出为CSV格式"""
        
        import csv
        
        # 场景名称映射（英文 -> 中文）
        scenario_names = {
            "campus_emergency": "校园急救",
            "community_emergency": "社区急救",
            "workplace_emergency": "工作场所急救",
            "sports_emergency": "运动场所急救",
        }
        
        # 分发源映射
        source_names = {
            "siliconflow": "AI智能分配",
            "fallback": "备用规则分配",
        }
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                '实验ID', '场景', '患者ID', '候选人数量', 
                '主施救者(PRIME)', '取机员(RUNNER)', '引导员(GUIDE)', '分发方式', '执行时间(ms)', '时间戳'
            ])
            
            for r in self.results:
                writer.writerow([
                    r.experiment_id,
                    scenario_names.get(r.scenario, r.scenario),
                    r.patient_id,
                    len(r.candidates),
                    r.assignments.get('PRIME', ''),
                    r.assignments.get('RUNNER', ''),
                    r.assignments.get('GUIDE', ''),
                    source_names.get(r.dispatch_source, r.dispatch_source),
                    round(r.execution_time_ms, 2),
                    r.timestamp,
                ])


def run_experiment(
    num_experiments: int = 100,
    scenarios: list = None,
    use_ai: bool = True,
    seed: int = 42,
    output_dir: str = "results"
) -> dict:
    """
    运行完整的实验流程
    
    Args:
        num_experiments: 实验次数
        scenarios: 场景列表
        use_ai: 是否使用AI模型
        seed: 随机种子
        output_dir: 输出目录
        
    Returns:
        实验报告
    """
    
    config = ExperimentConfig(
        num_experiments=num_experiments,
        scenarios=scenarios,
        use_ai_model=use_ai,
        output_dir=output_dir,
    )
    
    # 运行实验
    runner = ExperimentRunner(config, output_dir)
    results = runner.run_all_experiments(seed)
    
    # 保存结果
    result_file = runner.save_results()
    print(f"\n结果已保存至: {result_file}")
    
    # 分析结果
    analyzer = ResultAnalyzer(results)
    report = analyzer.print_report()
    
    # 导出CSV
    csv_path = Path(output_dir) / "experiment_results.csv"
    analyzer.export_csv(str(csv_path))
    print(f"CSV已导出至: {csv_path}")
    
    return report


if __name__ == "__main__":
    # 示例运行
    run_experiment(num_experiments=20, seed=42)