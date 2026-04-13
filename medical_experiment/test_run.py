"""测试脚本 - 输出到文件"""
import sys
from pathlib import Path
import traceback

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

output_file = PROJECT_ROOT / "test_output.txt"

with open(output_file, "w", encoding="utf-8") as f:
    try:
        f.write("Starting test script...\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Project root: {PROJECT_ROOT}\n")
        
        from config import ExperimentConfig
        f.write("Imported ExperimentConfig successfully\n")
        
        config = ExperimentConfig(
            num_experiments=5,
            seed=42,
            output_dir="test_results"
        )
        f.write(f"Created config: {config.num_experiments} experiments\n")
        
        from experiment_runner import ExperimentRunner
        f.write("Imported ExperimentRunner successfully\n")
        
        runner = ExperimentRunner(config)
        f.write("Created ExperimentRunner successfully\n")
        
        # 运行单次实验
        result = runner.run_single_experiment(1)
        f.write(f"Experiment 1 completed. Success: {result.success}\n")
        f.write("Test completed successfully!\n")
        
    except Exception as e:
        f.write(f"Error: {type(e).__name__}: {e}\n")
        traceback.print_exc(file=f)

print(f"Test completed. Output written to {output_file}")