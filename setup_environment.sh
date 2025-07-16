#!/bin/bash
# SpatialSense 环境配置脚本

echo "=== SpatialSense Environment Setup ==="

# 1. 创建虚拟环境
echo "1. Creating virtual environment..."
virtualenv -p python3 venv
if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi

# 2. 激活虚拟环境
echo "2. Activating virtual environment..."
source venv/bin/activate

# 3. 安装PyTorch (适配CUDA 12.4)
echo "3. Installing PyTorch with CUDA 12.4 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. 安装项目依赖
echo "4. Installing project dependencies..."
pip install -r requirements.txt

# 5. 安装额外依赖（空间推理相关）
echo "5. Installing additional dependencies..."
pip install shapely matplotlib openai

# 6. 配置CUDA环境变量
echo "6. Configuring CUDA environment..."
cat >> venv/bin/activate << 'EOF'

# CUDA 12.4 environment for SpatialSense
CUDA_HOME=/usr/local/cuda-12.4
export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
export PATH=${CUDA_HOME}/bin:${PATH}

# Additional Python path for project
export PYTHONPATH=$PYTHONPATH:$(pwd)
EOF

# 7. 验证安装
echo "7. Verifying installation..."
python -c "
import torch
import transformers
import peft
import datasets
import shapely
import matplotlib
print('✓ All dependencies installed successfully')
print(f'PyTorch version: {torch.__version__}')
print(f'Transformers version: {transformers.__version__}')
print(f'PEFT version: {peft.__version__}')
"

echo "✓ Environment setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit spatial_finetune.sh and update the working directory path"
echo "2. Submit job: sbatch spatial_finetune.sh"
echo "3. Monitor job: squeue"