# LifeReflex AI分配算法 - 医学验证实验

本模块用于为医创赛提供"医学相关验证数据或临床反馈"，通过模拟急救场景验证AI智能分配算法的效果。

## 背景

根据医创赛要求：
- AI技术贡献占比 ≥ 60%
- 需提供**医学相关验证数据或临床反馈**
- 避免纯技术类AI项目申报

本项目通过**模拟实验**方式生成验证数据，证明AI算法在院前急救场景下的有效性。

## 模块结构

```
medical_experiment/
├── config.py               # 配置文件（场景定义、候选人模板等）
├── data_generator.py       # 模拟数据生成器
├── experiment_runner.py    # 实验运行器
├── validation_analyzer.py  # 验证分析器
├── main.py                 # 主入口
└── results/                # 实验结果输出目录
```

## 使用方法

### 1. 运行实验

```bash
cd medical_experiment
python main.py --experiments 100 --seed 42
```

参数说明：
- `--experiments, -n`: 实验次数（默认50）
- `--seed, -s`: 随机种子（默认42，用于确保可重复性）
- `--output, -o`: 输出目录
- `--no-ai`: 不使用AI模型，使用规则引擎对比
- `--report`: 生成医学验证报告

### 2. 分析现有结果

```bash
python main.py --analyze results/experiment_results_xxx.json --report
```

### 3. 查看结果

实验结果会保存在 `results/` 目录：
- `experiment_results_*.json` - 原始实验数据
- `experiment_results.csv` - CSV格式结果
- `medical_validation_report.json` - 医学验证报告

## 验证数据说明

### 场景覆盖

| 场景 | 描述 | 典型人员 |
|------|------|----------|
| campus_emergency | 校园急救 | 学生、教师、校医、保安 |
| community_emergency | 社区急救 | 居民、物业、保安 |
| workplace_emergency | 工作场所急救 | 员工、前台、保安 |
| sports_emergency | 运动场所急救 | 运动员、教练、工作人员 |
| elderly_emergency | 老年人活动中心急救 | 老人、护理员、志愿者 |

### 验证指标

1. **分配成功率**: 三个角色都能成功分配的比例
2. **医学专业人员匹配率**: PRIME角色由医疗专业人员担任的比例
3. **体能有效性**: RUNNER角色体能适合跑步任务的比例
4. **路线熟悉度**: GUIDE角色熟悉环境/路线的比例
5. **响应时间**: AI算法响应时间

## 医学验证报告示例

运行后会生成符合医创赛要求的医学验证报告，包含：

```json
{
  "report_title": "AI智能分配算法医学验证报告",
  "algorithm_description": {
    "name": "LifeReflex AI智能分配算法",
    "purpose": "基于大语言模型的急救现场多角色智能分配系统",
    "medical_application": "院前急救协同调度"
  },
  "validation_methodology": {
    "approach": "模拟实验验证",
    "validation_data_type": "模拟生成的多场景急救数据"
  },
  "performance_metrics": {
    "allocation_success_rate": "95.0%",
    "prime_medical_professional_match_rate": "72.5%"
  },
  "conclusions": [
    "AI分配算法成功率为95.0%，能够稳定完成急救现场的角色分配任务"
  ],
  "clinical_feedback": {
    "strengths": ["高角色分配成功率", "优先分配医疗专业人员"],
    "recommendations": ["建议在实际部署中接入医疗专业人员数据库"]
  }
}
```

## 技术细节

### AI分配算法

采用大语言模型 (LLM) 进行智能角色分配：
- **输入**: 患者画像 + 候选协助者画像 + 选择规则
- **输出**: PRIME/RUNNER/GUIDE 三个角色的最优分配
- **备选**: 规则引擎 fallback 机制

### 分配规则

| 角色 | 优先级因素 |
|------|-----------|
| PRIME (主施救者) | 医疗专业能力 > 急救培训 > 临场经验 |
| RUNNER (取机员) | 体能 > 熟悉路线 > 执行力 |
| GUIDE (引导员) | 熟悉环境 > 组织协调 > 通道知识 |

## 依赖

- Python 3.10+
- 原项目的 `dispatch_ai` 模块
- `fastapi` (用于ClientInfo模型)

## 注意事项

1. 实验需要联网以调用AI API（如SiliconFlow）
2. 可通过环境变量 `SILICONFLOW_API_KEY` 配置API密钥
3. 不配置API密钥时使用规则引擎作为对比基准