"""
医学创新实验验证 - 主入口
用于生成模拟数据、运行AI分配实验并生成验证报告
"""

import argparse
import sys
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import ExperimentConfig
from experiment_runner import ExperimentRunner, ResultAnalyzer
from validation_analyzer import ValidationAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="LifeReflex AI分配算法医学验证实验"
    )
    parser.add_argument(
        "--experiments", "-n", 
        type=int, 
        default=50,
        help="实验次数 (默认: 50)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="随机种子 (默认: 42)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results",
        help="输出目录 (默认: results)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="不使用AI模型，使用规则引擎"
    )
    parser.add_argument(
        "--analyze",
        type=str,
        help="仅分析现有结果文件"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成医学验证报告"
    )
    
    args = parser.parse_args()
    
    # 分析模式
    if args.analyze:
        from config import SCENARIO_CONFIGS
        from validation_analyzer import run_validation_analysis
        
        output_report = str(Path(args.output) / "medical_validation_report.json")
        run_validation_analysis(args.analyze, output_report)
        return
    
    # 运行实验模式
    print("="*60)
    print("LifeReflex AI智能分配算法 - 医学验证实验")
    print("="*60)
    print(f"\n实验配置:")
    print(f"  实验次数: {args.experiments}")
    print(f"  随机种子: {args.seed}")
    print(f"  输出目录: {args.output}")
    print(f"  使用AI: {not args.no_ai}")
    print()
    
    # 创建配置
    config = ExperimentConfig(
        num_experiments=args.experiments,
        use_ai_model=not args.no_ai,
        output_dir=args.output,
    )
    
    # 运行实验
    runner = ExperimentRunner(config, args.output)
    results = runner.run_all_experiments(args.seed)
    
    # 保存原始结果
    result_file = runner.save_results()
    print(f"\n原始结果已保存至: {result_file}")
    
    # 生成分析报告
    analyzer = ResultAnalyzer(results)
    report = analyzer.print_report()
    
    # 导出CSV
    csv_path = Path(args.output) / "experiment_results.csv"
    analyzer.export_csv(str(csv_path))
    print(f"CSV已导出至: {csv_path}")
    
    # 生成医学验证报告
    if args.report:
        from config import SCENARIO_CONFIGS
        validation_analyzer = ValidationAnalyzer(results, SCENARIO_CONFIGS)
        medical_report = validation_analyzer.generate_medical_validation_report()
        
        report_path = Path(args.output) / "medical_validation_report.json"
        validation_analyzer.save_report(str(report_path))
        print(f"医学验证报告已保存至: {report_path}")
    
    print("\n实验完成！")


if __name__ == "__main__":
    main()