# AI 院前急救协同调度大脑 (Pre-hospital Emergency AI Dispatcher)

该项目是用于医疗比赛的院前急救调度算法内核。基于 `Qwen2.5-7B-Instruct` 大模型，通过高质量急救调度数据集进行 LoRA 微调，能够根据周围协助者的地理位置、健康状况和职业身份等特征，自动化、零格式错误地分配 `PRIME`（主要施救者）、`RUNNER`（取设备护跑者）、`GUIDE`（救护车指引者）任务。

## 项目结构
- `LLaMA-Factory/`: 包含微调工具和挂载启动 API 的相关脚本。
  - `saves/Qwen2.5-7B-Instruct/lora/train_1/`: 微调后的 LoRA 权重适配器。
  - `start_api.sh`: 一键启动模型推理 API 服务的脚本。
- `STRESS_TEST_REPORT.md`: 单机压测性能与逻辑分析报告。
- `stress_test_report_20260414.csv`: 1000次压力测试的详细用例、模型原始输出与耗时记录（可用 Excel 直接查看）。
- `prepare_dataset.py` & `data_generator.py`: 测试用例生成与数据清洗转换工具。

## 模型微调详情
- **基座模型**: `Qwen/Qwen2.5-7B-Instruct`
- **微调方法**: LoRA (Rank=16, Alpha=32, target_modules=all)
- **精度**: bf16
- **核心成果**: 模型由原本的对话机器人完全转化为具备严格约束规范的调度算法，确保输出100%为紧凑型 JSON 格式，解析成功率接近 100%。

## 性能压测结果
由于采用并发压测，在单张 RTX 3090 Ti 实验环境下，取得了优异的推理性能和极端的格式服从度。详细记录请参见 [压测分析报告](STRESS_TEST_REPORT.md)。

## 部署与调用

### 1. 启动本地推理后端
进入 `LLaMA-Factory` 目录并运行脚本启动本地服务器（暴露于 8008 端口）：
```bash
./start_api.sh
```

### 2. 客户端调用方式 (API 兼容 OpenAI 格式)
在主控 Java/Python 系统中，将 Base URL 指向启动的地址即可：
```python
import requests
import json

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "system", "content": "你是院前急救协同系统的调度大脑。请根据候选协助者画像（包括位置信息），在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。只返回紧凑 JSON，格式必须是 {\"PRIME\":\"userId或null\",\"RUNNER\":\"userId或null\",\"GUIDE\":\"userId或null\"}。"},
        {"role": "user", "content": "{\"patient_id\": \"id_123\", \"candidates_summary\": [...]}"}
    ],
    "temperature": 0.0
}

response = requests.post("http://127.0.0.1:8008/v1/chat/completions", json=payload)
print(response.json()["choices"][0]["message"]["content"])
```

## 注意事项
由于 `adapter_model.safetensors` 大小超出了 GitHub 单个文件 100MB 的限制，请确保您在提交前已经开启了 [Git LFS (Large File Storage)](https://git-lfs.github.com/) 跟踪 `.safetensors` 文件，或者将其单独上传至 HuggingFace / ModelScope。
