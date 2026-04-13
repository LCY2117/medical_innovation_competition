"""
AI智能分配施救者压测脚本
用于记录1000次调用和分配结果，涵盖各种情况

⚠️ 警告：此脚本会消耗API配额，请谨慎使用！
建议：先使用小数量测试，确认无误后再运行完整1000次
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
MEDICAL_EXPERIMENT_DIR = PROJECT_ROOT / "medical_experiment"
sys.path.insert(0, str(MEDICAL_EXPERIMENT_DIR))

from config import ExperimentConfig
from data_generator import DataGenerator
from client_info import ClientInfo


class StressTestRunner:
    """压测运行器"""
    
    def __init__(self, config: ExperimentConfig, output_dir: str = "stress_test_results"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.generator = DataGenerator(config)
        self.results = []
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "siliconflow": 0,
            "fallback": 0,
            "by_scenario": {},
            "by_special_case": {},
            "by_role": {"PRIME": 0, "RUNNER": 0, "GUIDE": 0},
            "total_api_calls": 0,
            "total_tokens": 0,
        }
        
    def run_single_test(
        self, 
        experiment_id: int,
        scenario: str,
        patient: dict,
        candidates: list[dict],
        special_case: str = None,
    ) -> dict:
        """运行单次测试"""
        # 添加服务器路径
        server_path = PROJECT_ROOT / "software_innovation" / "Semifinal" / "project" / "server（云端服务）"
        if str(server_path) not in sys.path:
            sys.path.insert(0, str(server_path))
        
        from app.services.dispatch_ai import DispatchPlanner
        
        patient_client = ClientInfo(**patient)
        candidate_clients = [ClientInfo(**c) for c in candidates]
        
        dispatch_planner = DispatchPlanner(
            api_key=self.config.api_key if self.config.use_ai_model else None,
            model=self.config.api_model,
            base_url=self.config.api_base_url,
            timeout_sec=self.config.api_timeout,
        )
        
        start_time = time.time()
        try:
            assignments, source = dispatch_planner.assign_roles(
                patient_client.userId, 
                candidate_clients
            )
            execution_time = (time.time() - start_time) * 1000
            
            # 统计
            self.stats["total"] += 1
            if source == "siliconflow":
                self.stats["success"] += 1
                self.stats["siliconflow"] += 1
                self.stats["total_api_calls"] += 1
            else:
                self.stats["fallback"] += 1
            
            # 按场景统计
            if scenario not in self.stats["by_scenario"]:
                self.stats["by_scenario"][scenario] = {"total": 0, "success": 0}
            self.stats["by_scenario"][scenario]["total"] += 1
            if source == "siliconflow":
                self.stats["by_scenario"][scenario]["success"] += 1
            
            # 按特殊用例统计
            case_key = special_case or "normal"
            if case_key not in self.stats["by_special_case"]:
                self.stats["by_special_case"][case_key] = {"total": 0, "success": 0}
            self.stats["by_special_case"][case_key]["total"] += 1
            if source == "siliconflow":
                self.stats["by_special_case"][case_key]["success"] += 1
            
            # 角色分配统计
            for role, user_id in assignments.items():
                if user_id:
                    self.stats["by_role"][role] += 1
            
            return {
                "experiment_id": experiment_id,
                "scenario": scenario,
                "special_case": special_case or "normal",
                "patient_id": patient["userId"],
                "patient_profession": patient.get("professionIdentity", ""),
                "num_candidates": len(candidates),
                "assignments": assignments,
                "dispatch_source": source,
                "execution_time_ms": round(execution_time, 2),
                "timestamp": datetime.now().isoformat(),
                "candidates_summary": [
                    {
                        "userId": c["userId"],
                        "professionIdentity": c.get("professionIdentity", ""),
                        "healthCondition": c.get("healthCondition", ""),
                        "distance": c.get("distance", 0),
                    }
                    for c in candidates
                ],
                "status": "success",
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.stats["total"] += 1
            self.stats["failed"] += 1
            
            return {
                "experiment_id": experiment_id,
                "scenario": scenario,
                "status": "failed",
                "error": str(e),
                "execution_time_ms": round(execution_time, 2),
                "timestamp": datetime.now().isoformat(),
            }
    
    def generate_test_data(self, scenario: str, seed: int, special_case: str = None) -> tuple:
        """生成测试数据
        
        Args:
            scenario: 场景名称
            seed: 随机种子
            special_case: 特殊测试用例类型
                - None: 正常场景
                - "few_candidates": 候选人不足(2-3人)
                - "many_candidates": 候选人过多(15+人)
                - "all_high_risk": 全部高风险(老人/体弱)
                - "no_medical": 无专业急救人员
                - "far_distance": 距离差异大(10m-2km)
                - "mixed_health": 混合健康状况
        """
        import random
        import math
        
        self.generator.set_seed(seed)
        
        # 根据特殊用例调整生成
        if special_case == "few_candidates":
            # 候选人不足：2-3人
            count = random.randint(2, 3)
            candidates = self.generator.generate_candidates(scenario, count=count)
        elif special_case == "many_candidates":
            # 候选人过多：15-20人
            count = random.randint(15, 20)
            candidates = self.generator.generate_candidates(scenario, count=count)
        elif special_case == "all_high_risk":
            # 全部高风险：生成后替换为老人/体弱
            candidates = self.generator.generate_candidates(scenario, count=8)
            for c in candidates:
                c["professionIdentity"] = "退休人员"
                c["healthCondition"] = "有慢性病"
                c["profileBio"] = "年龄较大，行动缓慢"
                c["fitness"] = "low"
        elif special_case == "no_medical":
            # 无专业急救人员：只生成普通居民/职员
            candidates = self.generator.generate_candidates(scenario, count=8)
            for c in candidates:
                if c["professionIdentity"] in ["医生", "护士", "急救员", "培训讲师"]:
                    c["professionIdentity"] = "公司职员"
                    c["healthCondition"] = "亚健康"
                    c["profileBio"] = "普通职员，了解基础急救知识"
                    c["fitness"] = "low"
        elif special_case == "mixed_health":
            # 混合健康状况
            candidates = self.generator.generate_candidates(scenario, count=8)
            health_types = ["健康", "健康", "健康", "亚健康", "亚健康", "有慢性病", "健康", "健康"]
            for i, c in enumerate(candidates):
                c["healthCondition"] = health_types[i % len(health_types)]
        else:
            # 正常场景
            candidates = self.generator.generate_candidates(scenario)
        
        # 随机选择患者
        patient_idx = random.randint(0, len(candidates) - 1)
        patient = candidates.pop(patient_idx)
        patient["isPatient"] = True
        
        # 添加位置信息
        base_lat = 31.825
        base_lon = 117.215
        
        patient["latitude"] = base_lat
        patient["longitude"] = base_lon
        
        # 为候选人添加不同距离
        for i, c in enumerate(candidates):
            c["userId"] = f"user_{i+1:02d}"
            
            if special_case == "far_distance":
                # 距离差异大：10-2000米
                distance = random.randint(10, 2000)
            else:
                # 正常距离分布
                distance = random.randint(10, 500)
            
            angle = random.uniform(0, 2 * math.pi)
            c["latitude"] = base_lat + (distance / 111000) * math.cos(angle)
            c["longitude"] = base_lon + (distance / 111000) * math.sin(angle)
            c["distance"] = distance
        
        return patient, candidates
    
    def run_stress_test(
        self, 
        total_experiments: int = 1000,
        scenarios: list = None,
        delay_between_calls: float = 0.1,
        max_concurrent: int = 1,
        resume: bool = False,
    ) -> dict:
        """
        运行压测
        
        Args:
            total_experiments: 总实验次数
            scenarios: 场景列表，默认使用配置中的所有场景
            delay_between_calls: 每次调用间隔（秒），防止过快调用
            max_concurrent: 最大并发数，建议设为1避免API限流
        """
        if scenarios is None:
            scenarios = self.config.scenarios
        
        print("=" * 60, flush=True)
        print("AI智能分配施救者 - 压测开始", flush=True)
        print("=" * 60, flush=True)
        print(f"总实验次数: {total_experiments}", flush=True)
        print(f"场景列表: {scenarios}", flush=True)
        print(f"调用间隔: {delay_between_calls}秒", flush=True)
        print(f"并发数: {max_concurrent}", flush=True)
        print(f"API模型: {self.config.api_model}", flush=True)
        print("=" * 60, flush=True)
        
        # 预估API费用
        # 每次调用约消耗 600-700 tokens
        estimated_tokens = total_experiments * 650
        estimated_cost = estimated_tokens / 1000000 * 0.2  # Qwen2.5-7B 约 $0.2/1M tokens
        print(f"\n[!] 预估API消耗:", flush=True)
        print(f"  预计Token: {estimated_tokens:,}", flush=True)
        print(f"  预计费用: ${estimated_cost:.2f} (约 RMB {estimated_cost * 7:.2f})", flush=True)
        print(flush=True)
        
        start_time = time.time()
        results = []
        
        # 特殊用例列表
        special_cases = [
            None,  # 正常场景
            "few_candidates",  # 候选人不足
            "many_candidates",  # 候选人过多
            "all_high_risk",  # 全部高风险
            "no_medical",  # 无专业急救人员
            "far_distance",  # 距离差异大
            "mixed_health",  # 混合健康状况
        ]
        
        test_inputs = []
        
        print(f"🚀 开启智能压测模式: 目标收集 {total_experiments} 次 AI 成功分配数据 (失败或回落不计入总数)", flush=True)

        # ✨ 边跑边写机制：提早创建并打开文件/处理断点续传
        import csv
        import glob
        
        jsonl_file = None
        csv_file = None
        
        if resume:
            csv_files = sorted(glob.glob(str(self.output_dir / "stress_test_stream_*.csv")))
            if csv_files:
                csv_file = Path(csv_files[-1])
                jsonl_file = csv_file.with_suffix(".jsonl")
                try:
                    with open(csv_file, "r", encoding="utf-8-sig") as cf:
                        existing_count = sum(1 for _ in csv.reader(cf)) - 1
                        if existing_count < 0: existing_count = 0
                        self.stats["siliconflow"] = existing_count
                except Exception:
                    pass
                print(f"\n🔄 [断点续传] 已绑定最新文件: {csv_file.name}", flush=True)
                print(f"📌 之前已收集 {self.stats['siliconflow']} 条！正向目标 {total_experiments} 条前进...\n", flush=True)
                
        if not csv_file or not jsonl_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            jsonl_file = self.output_dir / f"stress_test_stream_{timestamp}.jsonl"
            csv_file = self.output_dir / f"stress_test_stream_{timestamp}.csv"
            
            # 预写 CSV 表头
            with open(csv_file, 'w', encoding='utf-8-sig', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(['实验ID', '触发场景', '特殊事件测试', '患者身份', '候选协助者池人数', 
                                    'AI/规则', '耗时(毫秒)', 'PRIME_主要施救者', 'RUNNER_物品取送者', 'GUIDE_向导与协调者'])

        i = 0
        consecutive_failures = 0
        
        # 实时单行追记助手
        def _stream_save_result(res: dict):
            # 1. 记入 JSONL (按行存放)
            with open(jsonl_file, "a", encoding="utf-8") as jf:
                jf.write(json.dumps(res, ensure_ascii=False) + "\n")
            
            # 2. 记入 CSV
            import os
            scenario_map = {
                "campus_emergency": "校园-体育馆",
                "community_emergency": "社区-老人跌倒",
                "workplace_emergency": "办公楼-过劳或过敏",
                "sports_emergency": "运动场-马拉松/剧烈运动",
                "elderly_emergency": "养老院-基础疾病发作"
            }
            spec_map = {
                "normal": "无异常",
                "few_candidates": "协助者稀缺(2-3人)",
                "many_candidates": "协助者较多(15-20人)",
                "all_high_risk": "协助者均为高风险(老人/病患)",
                "no_medical": "协助者中无专业医疗/急救员",
                "far_distance": "协助者距离方差极大(10m~2km)",
                "mixed_health": "协助者健康状况混杂"
            }
            
            assignments = res.get("assignments", {})
            c_dict = {c["userId"]: c for c in res.get("candidates_summary", [])}
            
            def fmt_role(uid):
                if not uid: return "【未分配】"
                if uid in c_dict:
                    prof = c_dict[uid].get('professionIdentity', '未知')
                    dist = c_dict[uid].get('distance', 0)
                    heal = c_dict[uid].get('healthCondition', '未知')
                    return f"{uid} ({prof}, {heal}, 距离{dist}米)"
                return uid

            with open(csv_file, "a", encoding="utf-8-sig", newline="") as cf:
                writer = csv.writer(cf)
                writer.writerow([
                    res.get("experiment_id", ""),
                    scenario_map.get(res.get("scenario", ""), res.get("scenario", "")),
                    spec_map.get(res.get("special_case", "normal"), res.get("special_case", "normal")),
                    res.get("patient_profession", ""),
                    res.get("num_candidates", 0),
                    "💡AI分配" if res.get("dispatch_source") == "siliconflow" else "⚙️本地规则",
                    res.get("execution_time_ms", 0),
                    fmt_role(assignments.get("PRIME")),
                    fmt_role(assignments.get("RUNNER")),
                    fmt_role(assignments.get("GUIDE")),
                ])

        while self.stats['siliconflow'] < total_experiments:
            current_batch_size = min(max_concurrent, total_experiments - self.stats['siliconflow'])
            
            # 生成一批测试数据
            batch_inputs = []
            for _ in range(current_batch_size):
                scenario = scenarios[i % len(scenarios)]
                special_case = special_cases[i % len(special_cases)]
                patient, candidates = self.generate_test_data(scenario, seed=42 + i, special_case=special_case)
                batch_inputs.append((i + 1, scenario, patient, candidates, special_case))
                i += 1

            if max_concurrent > 1:
                with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                    future_to_test = {executor.submit(self.run_single_test, *inputs): inputs for inputs in batch_inputs}
                    for future in as_completed(future_to_test):
                        result = future.result()
                        is_success = result.get("dispatch_source") == "siliconflow" or (result.get("status") == "success" and result.get("dispatch_source") == "siliconflow")
                        
                        # 仅保留 API 成功的分配记录
                        if is_success:
                            consecutive_failures = 0
                            if len(results) < total_experiments: # 防止末尾超发时多于目标数量
                                results.append(result)
                                _stream_save_result(result)  # 立刻落盘！
                        else:
                            consecutive_failures += 1
                        
                        elapsed = time.time() - start_time
                        success_rate = self.stats["siliconflow"] / self.stats["total"] * 100 if self.stats["total"] > 0 else 0
                        print(f"进度: 成功收集 {len(results)}/{total_experiments} | "
                              f"数据已实时落盘 💾 | "
                              f"累计调用: {self.stats['total']} | "
                              f"失败/回落抛弃: {self.stats['fallback']} | "
                              f"一次性成功率: {success_rate:.1f}% | "
                              f"耗时: {elapsed:.1f}秒", flush=True)
            else:
                for inputs in batch_inputs:
                    result = self.run_single_test(*inputs)
                    is_success = result.get("dispatch_source") == "siliconflow" or (result.get("status") == "success" and result.get("dispatch_source") == "siliconflow")
                    
                    if is_success:
                        consecutive_failures = 0
                        if len(results) < total_experiments:
                            results.append(result)
                            _stream_save_result(result)  # 立刻落盘！
                    else:
                        consecutive_failures += 1
                            
                    elapsed = time.time() - start_time
                    success_rate = self.stats["siliconflow"] / self.stats["total"] * 100 if self.stats["total"] > 0 else 0
                    print(f"进度: 成功收集 {len(results)}/{total_experiments} | "
                          f"数据已实时落盘 💾 | "
                          f"累计调用: {self.stats['total']} | "
                          f"失败/回落抛弃: {self.stats['fallback']} | "
                          f"一次性成功率: {success_rate:.1f}% | "
                          f"耗时: {elapsed:.1f}秒", flush=True)
                          
                    # 单线程模式下防封禁拦截判断
                    if consecutive_failures >= 5:
                        print(f"\n[⚠️ API防封禁] 连续失败/拦截达到 {consecutive_failures} 次！触发自动冷却机制，休眠 20 秒...", flush=True)
                        time.sleep(20)
                        consecutive_failures = 0
                    elif delay_between_calls > 0:
                        time.sleep(delay_between_calls)
                        
            # 多线程模式下的防封禁冷切判断处理
            if max_concurrent > 1:
                if consecutive_failures >= 5:
                    print(f"\n[⚠️ API防封禁] 批处理内出现大量失败（连续 {consecutive_failures} 次），强制冷却休眠 20 秒...", flush=True)
                    time.sleep(20)
                    consecutive_failures = 0
                elif delay_between_calls > 0:
                    time.sleep(delay_between_calls)
                    
        total_time = time.time() - start_time
        
        # 整体流程结束，由于已经流式存过了，这里进行最后完整的汇总保存(可选)
        try:
            self._save_results(results, total_time)
        except Exception as e:
            print(f"最后封装JSON数组时出错(但流式记录完整无缺)：{e}")
        
        # 打印统计
        self._print_stats(total_time)
        
        return {
            "results": results,
            "stats": self.stats,
            "total_time": total_time,
        }
    
    def _save_results(self, results: list, total_time: float):
        """保存结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON详细结果
        json_file = self.output_dir / f"stress_test_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "config": {
                    "total_experiments": self.stats["total"],
                    "api_model": self.config.api_model,
                    "api_base_url": self.config.api_base_url,
                },
                "stats": self.stats,
                "total_time_seconds": round(total_time, 2),
                "results": results,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细结果已保存: {json_file}")
        
        # 保存全中文CSV汇总 (使用utf-8-sig以兼容Excel直接打开)
        csv_file = self.output_dir / f"stress_test_{timestamp}.csv"
        import csv
        
        scenario_map = {
            "campus_emergency": "校园急救",
            "community_emergency": "社区急救",
            "workplace_emergency": "工作场所急救",
            "sports_emergency": "运动场所急救",
            "elderly_emergency": "老年人活动中心急救"
        }
        
        case_map = {
            "normal": "正常场景",
            "few_candidates": "候选人不足(2-3人)",
            "many_candidates": "候选人过多(15+人)",
            "all_high_risk": "全部高风险",
            "no_medical": "无专业急救人员",
            "far_distance": "距离差异大",
            "mixed_health": "混合健康状况"
        }
        
        source_map = {
            "siliconflow": "AI智能分配",
            "fallback": "本地规则分配"
        }
        
        status_map = {
            "success": "成功",
            "failed": "失败"
        }
        
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "实验编号", "急救场景", "特殊情况", "患者职业", "候选人数", 
                "主急救员(PRIME)", "奔跑者(RUNNER)", "引导员(GUIDE)", 
                "分配来源", "耗时(毫秒)", "任务状态", "测试时间"
            ])
            for r in results:
                # 获取候选人信息的映射，以便展示带有身份备注的详情
                summary_map = {c["userId"]: c for c in r.get("candidates_summary", [])}
                
                def get_desc(role_name):
                    uid = r.get("assignments", {}).get(role_name)
                    if not uid:
                        return "未分配"
                    info = summary_map.get(uid)
                    if info:
                        prof = info.get("professionIdentity", "未知")
                        health = info.get("healthCondition", "未知")
                        dist = info.get("distance", "?")
                        dist_str = f"{dist:.0f}" if isinstance(dist, (int, float)) else dist
                        return f"{uid} ({prof}, {health}, 距离{dist_str}米)"
                    return uid

                writer.writerow([
                    r.get("experiment_id", ""),
                    scenario_map.get(r.get("scenario", ""), r.get("scenario", "")),
                    case_map.get(r.get("special_case", "normal"), r.get("special_case", "")),
                    r.get("patient_profession", ""),
                    r.get("num_candidates", ""),
                    get_desc("PRIME"),
                    get_desc("RUNNER"),
                    get_desc("GUIDE"),
                    source_map.get(r.get("dispatch_source", ""), r.get("dispatch_source", "")),
                    r.get("execution_time_ms", ""),
                    status_map.get(r.get("status", ""), r.get("status", "")),
                    r.get("timestamp", ""),
                ])
        
        print(f"全中文CSV汇总已保存: {csv_file}")
    
    def _print_stats(self, total_time: float):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("压测统计结果")
        print("=" * 60)
        print(f"总实验次数: {self.stats['total']}")
        print(f"  - 成功 (AI分配): {self.stats['siliconflow']}")
        print(f"  - 成功 (本地规则): {self.stats['fallback']}")
        print(f"  - 失败: {self.stats['failed']}")
        print(f"总API调用次数: {self.stats['total_api_calls']}")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"平均耗时: {total_time/self.stats['total']*1000:.2f}ms/次")
        
        print("\n按场景统计:")
        for scenario, data in self.stats["by_scenario"].items():
            rate = data["success"] / data["total"] * 100 if data["total"] > 0 else 0
            print(f"  {scenario}: {data['total']}次, 成功 {data['success']}次 ({rate:.1f}%)")
        
        print("\n按特殊用例统计:")
        case_names = {
            "normal": "正常场景",
            "few_candidates": "候选人不足(2-3人)",
            "many_candidates": "候选人过多(15+人)",
            "all_high_risk": "全部高风险",
            "no_medical": "无专业急救人员",
            "far_distance": "距离差异大",
            "mixed_health": "混合健康状况",
        }
        for case_key, data in self.stats["by_special_case"].items():
            case_name = case_names.get(case_key, case_key)
            rate = data["success"] / data["total"] * 100 if data["total"] > 0 else 0
            print(f"  {case_name}: {data['total']}次, 成功 {data['success']}次 ({rate:.1f}%)")
        
        print("\n角色分配统计:")
        for role, count in self.stats["by_role"].items():
            print(f"  {role}: {count}次")
        
        print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI智能分配压测脚本")
    parser.add_argument("-n", "--num", type=int, default=100, 
                        help="实验次数，默认100")
    parser.add_argument("-d", "--delay", type=float, default=2.0,
                        help="调用间隔(秒)，默认2.0")
    parser.add_argument("-c", "--concurrent", type=int, default=1,
                        help="最大并发数(线程数)，默认1")
    parser.add_argument("-s", "--scenarios", nargs="+", 
                        default=["campus_emergency", "community_emergency", 
                                "workplace_emergency", "sports_emergency", 
                                "elderly_emergency"],
                        help="指定场景")
    parser.add_argument("--resume", action="store_true",
                        help="开启断点续传，自动接着最新的文件写")
    parser.add_argument("--dry-run", action="store_true",
                        help="试运行模式，只生成数据不调用API")
    
    args = parser.parse_args()
    
    # 加载配置
    config = ExperimentConfig(
        name="压测实验",
        num_experiments=args.num,
    )
    
    # 如果是试运行，关闭AI
    if args.dry_run:
        config.use_ai_model = False
        print("[!] 试运行模式：使用本地规则引擎，不调用API")
    
    # 创建运行器
    runner = StressTestRunner(config)
    
    # 运行压测
    runner.run_stress_test(
        total_experiments=args.num,
        scenarios=args.scenarios,
        delay_between_calls=args.delay,
        max_concurrent=args.concurrent,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()