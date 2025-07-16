# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在处理此代码库时提供指导。

## 项目概述

SpatialSense 是一个空间推理系统，使用大语言模型 (LLM) 来确定几何对象之间的空间关系。该项目包括空间推理框架和用于在空间推理任务上微调 LLM 的工具。

## 关键命令

### 开发命令
```bash
# 安装依赖项
pip install -r requirements.txt

# 准备微调数据
python finetune_prepare.py

# 运行模型微调
python finetune_script.py

# 评估模型性能
python evaluate_model.py <model_path> finetune_data/test.jsonl

# 运行空间推理测试
python test_spatial_reasoning.py
python test_spatial_reasoning.py your_data.jsonl 10 your-api-key

# 运行主要空间推理框架
python spatial_reasoning_framework.py
python spatial_reasoning_framework.py your_data.jsonl 10 your-api-key

# 使用 tensorboard 查看训练日志
tensorboard --logdir spatial_reasoning_model
```

### 测试命令
```bash
# 使用示例数据进行基本测试
python test_spatial_reasoning.py

# 使用自定义数据和有限样本进行测试
python test_spatial_reasoning.py custom_data.jsonl 50

# 使用特定 API 密钥进行测试
python test_spatial_reasoning.py data.jsonl 10 sk-your-api-key
```

## 项目架构

### 核心组件

**spatial_reasoning_framework.py**: 实现几何对象之间空间关系检测的主要框架。包含：
- `SpatialReasoningFramework`: 用于点-点、点-线、点-多边形、线-线、线-多边形和多边形-多边形关系的核心空间分析工具
- `LLMSpatialReasoningAgent`: 具有工具调用能力的空间推理 LLM 集成
- 工具描述和空间关系提取函数

**advanced_spatial_framework.py**: 增强版本，包含：
- `DE9IMMatrix`: 空间拓扑 DE-9IM（维度扩展9交集模型）的实现
- `SpatialRelation` 枚举，用于标准化空间关系类型
- 高级几何分析能力

### 微调流水线

**finetune_prepare.py**: LLM 微调的数据预处理
**finetune_script.py**: 使用 LoRA（低秩适应）的主要微调脚本
**evaluate_model.py**: 模型评估和性能测试
**finetune_config.yaml**: 训练参数配置文件

### 数据结构

- **DEI-9IM/**: 包含不同空间关系类型的思维链 (COT) 数据集
- **finetune_data/**: 处理过的训练、验证和测试集 (train.jsonl, val.jsonl, test.jsonl)
- **Spatial-Reasoning/**: 额外的空间推理数据集
- **Trajectory_datasets/**: （当前为空）用于基于轨迹的空间分析

### 支持的空间关系

框架支持 7 种空间关系类型：
- `Equals`: 对象完全相同
- `Contains`: 一个对象包含另一个对象
- `Within`: 一个对象在另一个对象内部
- `Overlaps`: 对象部分重叠
- `Crosses`: 对象相交
- `Touches`: 对象在边界处接触
- `Disjoint`: 对象分离

### 数据格式

输入数据应为 JSONL 格式，结构如下：
```json
{
  "input": "点 A 位于 (-81, -87)。点 B 位于 (-81, -87)。点 A 和点 B 之间的空间关系是什么？",
  "output": "步骤 1：使用点 (-81, -87) 和 (-81, -87) 调用 calculate_distance 工具\n→ 工具返回：0.00\n步骤 2：由于距离 = 0，空间关系是 'Equals'。"
}
```

## 配置

**硬件要求**：
- 最低要求：16GB GPU 内存
- 推荐配置：24GB+ GPU 内存
- 不推荐 CPU 训练

**模型推荐**：
- `Qwen/Qwen2-7B-Instruct`（推荐）
- `THUDM/chatglm3-6b`
- `baichuan-inc/Baichuan2-7B-Chat`

## 关键依赖项

- torch>=2.0.0
- transformers>=4.35.0
- peft>=0.6.0（用于 LoRA 微调）
- datasets>=2.14.0
- shapely（用于几何运算）
- matplotlib（用于可视化）
- openai（用于 LLM API 调用）

## API 集成

该框架与 OpenAI 的 API 集成用于 LLM 推理。设置 `OPENAI_API_KEY` 环境变量或在运行脚本时作为参数传递。

## 输出文件

- `test_results.json`: 详细的测试结果和准确率指标
- 训练日志保存在 `spatial_reasoning_model` 目录中
- 模型检查点在微调过程中自动保存