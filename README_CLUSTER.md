# SpatialSense 微调完整步骤指南

## 步骤1: 准备和上传项目文件

### 1.1 在本地准备文件
```bash
# 在本地SpatialSense目录下，确保我们创建的文件有执行权限
cd /Users/bob/Downloads/SpatialSense
chmod +x spatial_finetune.sh setup_environment.sh
```

### 1.2 上传项目到集群
```bash
# 方式1：使用scp上传整个项目
scp -r /Users/bob/Downloads/SpatialSense/ username@cluster-address:/home/username/

# 方式2：如果集群支持，可以先登录集群再git clone
ssh username@cluster-address
cd /home/username
git clone <your-repository-url>  # 如果你有Git仓库
```

### 1.3 登录集群并检查文件
```bash
# 登录集群
ssh username@cluster-address

# 进入项目目录
cd /home/username/SpatialSense

# 检查重要文件是否存在
ls -la spatial_finetune.sh setup_environment.sh finetune_script.py finetune_config.yaml
```

## 步骤2: 在集群上配置环境

### 2.1 执行环境配置脚本
```bash
# 确保在项目目录下
cd /home/username/SpatialSense

# 执行环境配置（需要5-10分钟）
./setup_environment.sh
```

### 2.2 验证环境安装
```bash
# 激活虚拟环境
source venv/bin/activate

# 检查关键依赖
python -c "
import torch
import transformers
import peft
import datasets
print('✓ PyTorch version:', torch.__version__)
print('✓ CUDA available:', torch.cuda.is_available())
print('✓ Transformers version:', transformers.__version__)
print('✓ PEFT version:', peft.__version__)
"
```

### 2.3 测试GPU访问
```bash
# 申请一个交互式GPU会话进行测试
srun --pty --gres=gpu:1 bash

# 在GPU节点上测试
source venv/bin/activate
python -c "
import torch
print('GPU count:', torch.cuda.device_count())
print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')
"

# 退出交互式会话
exit
```

## 步骤3: 配置和检查训练参数

### 3.1 修改SLURM脚本中的路径
```bash
# 编辑SLURM作业脚本
vim spatial_finetune.sh

# 修改第18行，将路径改为你的实际路径
# 从: cd /path/to/your/SpatialSense
# 改为: cd /home/username/SpatialSense
```

### 3.2 选择合适的配置文件
```bash
# 检查现有配置
ls -la finetune_config*.yaml

# 使用集群优化的配置（推荐）
cp finetune_config_cluster.yaml finetune_config.yaml

# 或者编辑现有配置文件
vim finetune_config.yaml
```

### 3.3 检查数据文件是否存在
```bash
# 检查原始数据文件
ls -la DEI-9IM_tools/*.jsonl

# 应该看到这些文件：
# point_point_cot_dataset.jsonl
# point_line_cot_dataset.jsonl 
# point_polygon_cot_dataset.jsonl
# line_line_cot_dataset.jsonl
# line_polygon_cot_dataset.jsonl
# polygon_polygon_cot_dataset.jsonl
```

### 3.4 手动测试数据预处理
```bash
# 激活环境
source venv/bin/activate

# 测试数据预处理
python finetune_prepare.py

# 检查生成的训练数据
ls -la finetune_data/
head -1 finetune_data/train.jsonl

# 查看数据统计
python -c "
import json
for file in ['train.jsonl', 'val.jsonl', 'test.jsonl']:
    with open(f'finetune_data/{file}', 'r') as f:
        count = sum(1 for line in f if line.strip())
    print(f'{file}: {count} samples')
"
```

## 步骤4: 提交和监控训练作业

### 4.1 提交SLURM作业
```bash
# 确保在项目目录
cd /home/username/SpatialSense

# 提交训练作业
sbatch spatial_finetune.sh

# 系统会返回作业ID，例如：
# Submitted batch job 12345
# 记住这个作业ID！
```

### 4.2 监控作业状态
```bash
# 查看作业队列状态
squeue

# 查看你的作业状态
squeue -u $USER

# 查看特定作业详情（用你的实际JOBID替换12345）
scontrol show job 12345
```

### 4.3 实时查看训练日志
```bash
# 查看作业输出日志（用实际JOBID替换12345）
tail -f spatial_finetune_12345.log

# 或者实时监控，每5秒刷新一次
watch -n 5 tail -20 spatial_finetune_12345.log
```

### 4.4 监控GPU使用情况
```bash
# 如果你的作业正在运行，可以查看GPU使用情况
# 首先找到作业运行的节点
squeue -j 12345 -o "%N"

# 然后登录到计算节点查看GPU状态
ssh compute-node-name
nvidia-smi
exit
```

### 4.5 训练过程中的关键检查点
```bash
# 数据预处理完成后，应该看到：
# ✓ Data preparation completed

# 模型开始训练时，应该看到：
# === Step 3: Model Fine-tuning ===
# Loading model: Qwen/Qwen2-7B-Instruct

# 训练过程中会看到类似的输出：
# Training samples: 4000
# Validation samples: 500
# Starting training...
```

## 步骤5: 验证和评估训练结果

### 5.1 等待作业完成
```bash
# 持续检查作业状态，直到状态变为COMPLETED
squeue -j 12345

# 当作业完成时，查看最终日志
cat spatial_finetune_12345.log | tail -20

# 检查是否有错误
cat spatial_finetune_12345.err
```

### 5.2 检查训练输出文件
```bash
# 检查模型文件是否生成
ls -la spatial_reasoning_model/

# 应该看到以下文件：
# pytorch_model.bin 或 pytorch_model.safetensors
# config.json
# tokenizer.model
# adapter_config.json (LoRA配置)

# 检查评估结果
cat test_results.json
```

### 5.3 手动验证模型功能
```bash
# 激活环境
source venv/bin/activate

# 运行快速功能测试
python test_spatial_reasoning.py finetune_data/test.jsonl 10

# 查看测试结果
ls -la *test_results.json
```

### 5.4 验证模型加载
```bash
# 测试模型是否可以正常加载
python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

print('Loading base model...')
tokenizer = AutoTokenizer.from_pretrained('spatial_reasoning_model')
base_model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2-7B-Instruct')

print('Loading fine-tuned adapter...')
model = PeftModel.from_pretrained(base_model, 'spatial_reasoning_model')

print('✓ Model loaded successfully!')
print(f'Model type: {type(model)}')
"
```

## 完整执行时间线

**预期时间安排**：
- 步骤1-2: 环境配置 (~15分钟)
- 步骤3: 参数配置 (~5分钟)
- 步骤4: 训练执行 (~3-6小时)
- 步骤5: 结果验证 (~10分钟)

## 常见问题及解决方案

### 如果遇到OOM错误：
```bash
# 编辑配置文件
vim finetune_config.yaml
# 将 per_device_train_batch_size 改为 2
# 将 gradient_accumulation_steps 改为 8
```

### 如果作业被取消：
```bash
# 查看取消原因
sacct -j 12345 --format=JobID,JobName,State,ExitCode,Reason

# 重新提交作业
sbatch spatial_finetune.sh
```

### 如果模型下载失败：
```bash
# 可以尝试使用镜像源
export HF_ENDPOINT=https://hf-mirror.com
sbatch spatial_finetune.sh
```

## 关键命令汇总

### 准备阶段：
```bash
ssh username@cluster-address
cd /home/username/SpatialSense
./setup_environment.sh
```

### 配置阶段：
```bash
vim spatial_finetune.sh  # 修改路径
cp finetune_config_cluster.yaml finetune_config.yaml
source venv/bin/activate && python finetune_prepare.py
```

### 执行阶段：
```bash
sbatch spatial_finetune.sh
squeue -u $USER
tail -f spatial_finetune_*.log
```

### 验证阶段：
```bash
ls -la spatial_reasoning_model/
cat test_results.json
python test_spatial_reasoning.py finetune_data/test.jsonl 10
```

按照这些详细步骤，你应该能够成功完成SpatialSense项目的微调。每个步骤都有具体的命令和预期输出，遇到问题时可以参考相应的故障排除方案。