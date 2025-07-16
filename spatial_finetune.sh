#!/bin/bash
#SBATCH --job-name=spatial_finetune
#SBATCH --output=spatial_finetune_%j.log
#SBATCH --error=spatial_finetune_%j.err
#SBATCH --gres=gpu:1
#SBATCH -c 8
#SBATCH --mem=32g
#SBATCH --time=12:00:00
#SBATCH --partition=main

echo "=== SpatialSense Fine-tune Job Started ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo "Working directory: $(pwd)"
echo "Start time: $(date)"

# 设置工作目录
cd /path/to/your/SpatialSense  # 修改为你的实际路径

# 激活虚拟环境
source venv/bin/activate

# 检查环境
echo "=== Environment Check ==="
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"
nvidia-smi

# 第一阶段：数据预处理
echo "=== Step 1: Data Preparation ==="
python finetune_prepare.py
if [ $? -eq 0 ]; then
    echo "✓ Data preparation completed"
else
    echo "✗ Data preparation failed"
    exit 1
fi

# 验证数据
echo "=== Step 2: Data Validation ==="
python -c "
import json
import os
files = ['finetune_data/train.jsonl', 'finetune_data/val.jsonl', 'finetune_data/test.jsonl']
for file in files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            count = sum(1 for line in f if line.strip())
        print(f'✓ {file}: {count} samples')
    else:
        print(f'✗ Missing {file}')
        exit(1)
"

# 第二阶段：模型微调
echo "=== Step 3: Model Fine-tuning ==="
python finetune_script.py
if [ $? -eq 0 ]; then
    echo "✓ Fine-tuning completed"
else
    echo "✗ Fine-tuning failed"
    exit 1
fi

# 第三阶段：模型评估
echo "=== Step 4: Model Evaluation ==="
python evaluate_model.py spatial_reasoning_model finetune_data/test.jsonl
if [ $? -eq 0 ]; then
    echo "✓ Model evaluation completed"
else
    echo "✗ Model evaluation failed"
fi

# 第四阶段：功能测试
echo "=== Step 5: Functional Testing ==="
python test_spatial_reasoning.py finetune_data/test.jsonl 50
if [ $? -eq 0 ]; then
    echo "✓ Functional testing completed"
else
    echo "✗ Functional testing failed"
fi

echo "=== Job Completed ==="
echo "End time: $(date)"
echo "Job duration: $SECONDS seconds"
echo "Output files:"
echo "  - Model: spatial_reasoning_model/"
echo "  - Results: test_results.json"
echo "  - Logs: spatial_finetune_${SLURM_JOB_ID}.log"