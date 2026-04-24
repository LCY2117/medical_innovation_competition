# 🏥 AI 院前急救协同调度大脑 (Pre-hospital Emergency AI Dispatcher)

> 基于大语言模型的院前急救智能调度系统，用于医疗创新大赛项目。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 项目概述

本项目是一个**医疗创新大赛**的院前急救调度算法内核。基于 `Qwen2.5-7B-Instruct` 大语言模型，通过 LoRA 微调技术，使其能够根据周围协助者的**地理位置**、**健康状况**和**职业身份**等特征，自动化、零格式错误地分配以下三类任务：

| 角色 | 说明 |
|------|------|
| `PRIME` | **主要施救者** - 负责对患者进行紧急救治 |
| `RUNNER` | **取设备护跑者** - 负责取急救设备并护送患者 |
| `GUIDE` | **救护车指引者** - 负责引导救护车到达现场 |

## ✨ 核心特性

- 🤖 **大模型驱动**：基于 Qwen2.5-7B-Instruct 微调，具备强大的语义理解能力
- 🎯 **精确调度**：自动分析候选人画像，做出最优任务分配
- 📊 **格式保证**：输出 100% 紧凑型 JSON 格式，解析成功率接近 100%
- ⚡ **高性能**：支持并发请求，RTX 3090 Ti 环境下推理性能优异
- 🔬 **科学验证**：通过模拟实验生成医学验证数据，满足医创赛要求

---

## 📁 项目结构

```
medical_competition/
├── README.md                          # 项目说明文档
├── ai_dispatch_config.yaml            # 全局配置文件
├── requirements.txt                   # Python 依赖
├── STRESS_TEST_REPORT.md              # 压测分析报告
│
├── medical_experiment/                # 🧪 医学验证实验模块
│   ├── main.py                        # 主入口（实验运行/分析）
│   ├── config.py                      # 实验配置（场景定义、候选人模板）
│   ├── data_generator.py              # 模拟数据生成器
│   ├── experiment_runner.py           # 实验运行器
│   ├── validation_analyzer.py         # 验证分析器
│   ├── generate_report.py             # 医学验证报告生成
│   ├── client_info.py                 # 客户端信息模型
│   ├── prepare_dataset.py             # 数据集准备工具
│   ├── stress_test.py                 # 压力测试脚本
│   ├── stress_test_lora.py            # LoRA 压力测试
│   └── results/                       # 实验结果输出
│
├── LLaMA-Factory/                     # 🤖 模型微调框架
│   ├── src/                           # 源代码
│   ├── examples/                      # 训练示例
│   ├── saves/                         # 模型保存目录
│   │   └── Qwen2.5-7B-Instruct/lora/  # LoRA 微调权重
│   └── start_api.sh                   # 启动 API 服务脚本
│
├── stress_test_results/               # 📈 压测结果数据
│   ├── stress_test_*.csv              # CSV 格式压测记录
│   └── stress_test_*.json             # JSON 格式压测记录
│
└── model_trainig/                     # 模型训练相关
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd medical_competition

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行医学验证实验

```bash
cd medical_experiment

# 运行 100 次模拟实验
python main.py --experiments 100 --seed 42

# 生成医学验证报告
python main.py --experiments 100 --seed 42 --report

# 分析现有结果
python main.py --analyze results/experiment_results_xxx.json --report
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--experiments` | `-n` | 50 | 实验次数 |
| `--seed` | `-s` | 42 | 随机种子（确保可重复性） |
| `--output` | `-o` | results | 输出目录 |
| `--no-ai` | - | - | 不使用 AI 模型，使用规则引擎对比 |
| `--report` | - | - | 生成医学验证报告 |
| `--analyze` | - | - | 仅分析现有结果文件 |

### 3. 启动模型推理服务

```bash
# 进入 LLaMA-Factory 目录
cd LLaMA-Factory

# 启动 API 服务（默认端口 8008）
./start_api.sh
```

### 4. 调用调度 API

```python
import requests
import json

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {
            "role": "system",
            "content": "你是院前急救协同系统的调度大脑。请根据候选协助者画像（包括位置信息），在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。只返回紧凑 JSON。"
        },
        {
            "role": "user",
            "content": '{"patient_id": "id_123", "candidates_summary": [...]}'
        }
    ],
    "temperature": 0.0
}

response = requests.post(
    "http://127.0.0.1:8008/v1/chat/completions",
    json=payload
)
result = response.json()["choices"][0]["message"]["content"]
print(result)
```

---

## 📊 模型微调详情

| 项目 | 配置 |
|------|------|
| **基座模型** | `Qwen/Qwen2.5-7B-Instruct` |
| **微调方法** | LoRA (Rank=16, Alpha=32, target_modules=all) |
| **训练精度** | bf16 |
| **输出格式** | 紧凑型 JSON |
| **解析成功率** | 接近 100% |
| **核心成果** | 模型从对话机器人转化为严格约束规范的调度算法 |

## 📈 性能压测结果

在单张 **RTX 3090 Ti** 实验环境下，采用并发压测方式，取得了优异的推理性能。

详细压测记录请参见：
- 📄 [压测分析报告](STRESS_TEST_REPORT.md)
- 📊 [CSV 压测数据](stress_test_report_20260414.csv)

---

## 🔬 医学验证说明

根据医疗创新大赛要求：
- AI 技术贡献占比 ≥ 60%
- 需提供**医学相关验证数据或临床反馈**
- 避免纯技术类 AI 项目申报

本项目通过**模拟实验**方式生成验证数据，证明 AI 算法在院前急救场景下的有效性。实验模块结构：

```
medical_experiment/
├── 数据层：模拟急救场景数据生成
├── 算法层：AI 分配 vs 规则引擎对比验证
└── 分析层：生成医学验证报告
```

---

## ⚠️ 注意事项

### Git LFS 配置

由于 `adapter_model.safetensors` 文件超过 GitHub 单个文件 100MB 限制，请在提交前启用 Git LFS：

```bash
# 安装 Git LFS
git lfs install

# 跟踪 .safetensors 文件
git lfs track "*.safetensors"

# 将 .gitattributes 提交到仓库
git add .gitattributes
git commit -m "Add Git LFS tracking for model files"
```

或者将模型文件单独上传至：
- [HuggingFace](https://huggingface.co/)
- [ModelScope](https://modelscope.cn/)

### 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| GPU | RTX 3090 (24GB) | RTX 4090 (24GB) |
| 内存 | 32GB | 64GB |
| 存储 | 100GB | 200GB |

---

## 📄 许可证

本项目仅供医疗创新大赛使用。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 联系方式

如有问题，请通过 Issue 或邮件联系项目维护者。
# model_training
# model_training
