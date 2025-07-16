# SpatialSense 集群Fine-tune执行指南

## 前置准备

### 1. 上传项目到集群
```bash
# 方式1: 如果有git仓库
git clone <your-repository> /path/to/SpatialSense
cd /path/to/SpatialSense

# 方式2: 直接上传文件
scp -r /local/SpatialSense/ username@cluster:/path/to/SpatialSense/
```

### 2. 环境配置
```bash
# 进入项目目录
cd /path/to/SpatialSense

# 执行环境配置
chmod +x setup_environment.sh
./setup_environment.sh
```

### 3. 修改配置文件
```bash
# 编辑SLURM作业脚本，修改工作目录路径
vim spatial_finetune.sh
# 将第18行修改为实际路径：
# cd /your/actual/path/to/SpatialSense

# 可选：使用集群优化的配置文件
cp finetune_config_cluster.yaml finetune_config.yaml
```

## 执行Fine-tune

### 方式1：提交批处理作业（推荐）
```bash
# 提交作业
sbatch spatial_finetune.sh

# 查看作业状态
squeue

# 查看作业详情
squeue -j <JOBID>

# 实时查看日志
tail -f spatial_finetune_<JOBID>.log
```

### 方式2：交互式调试
```bash
# 申请交互式会话
srun --pty --gres=gpu:1 -c 8 --mem=32g bash

# 激活环境
source venv/bin/activate

# 手动执行各步骤
python finetune_prepare.py
python finetune_script.py
python evaluate_model.py spatial_reasoning_model finetune_data/test.jsonl
```

## 监控和管理

### 作业监控
```bash
# 查看所有作业
squeue

# 查看特定用户作业
squeue -u $USER

# 查看作业详细信息
scontrol show job <JOBID>

# 取消作业
scancel <JOBID>
```

### 资源监控
```bash
# 查看GPU使用情况（在计算节点上）
nvidia-smi

# 查看节点资源状态
sinfo

# 查看分区信息
sinfo -p main
```

### 日志查看
```bash
# 查看标准输出日志
cat spatial_finetune_<JOBID>.log

# 查看错误日志
cat spatial_finetune_<JOBID>.err

# 实时跟踪日志
tail -f spatial_finetune_<JOBID>.log
```

## 结果文件

训练完成后，将生成以下文件：

```
SpatialSense/
├── spatial_reasoning_model/          # 微调后的模型
│   ├── pytorch_model.bin            # 模型权重
│   ├── config.json                  # 模型配置
│   ├── tokenizer.model              # 分词器
│   └── adapter_config.json          # LoRA配置
├── test_results.json                # 评估结果
├── finetune_data/                   # 训练数据
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
└── spatial_finetune_<JOBID>.log     # 训练日志
```

## 故障排除

### 常见问题

1. **OOM (Out of Memory) 错误**
   ```bash
   # 修改配置文件，降低batch size
   vim finetune_config.yaml
   # 将per_device_train_batch_size改为2或1
   # 增加gradient_accumulation_steps到8或16
   ```

2. **CUDA版本不兼容**
   ```bash
   # 确认CUDA版本
   nvcc --version
   # 重新安装对应版本的PyTorch
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

3. **模型下载失败**
   ```bash
   # 手动下载模型到本地
   python -c "
   from transformers import AutoModelForCausalLM
   model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2-7B-Instruct')
   model.save_pretrained('./models/Qwen2-7B-Instruct')
   "
   # 修改配置文件使用本地模型路径
   ```

4. **权限问题**
   ```bash
   # 确保脚本可执行
   chmod +x spatial_finetune.sh
   chmod +x setup_environment.sh
   ```

### 性能优化建议

1. **显存优化**
   - 使用gradient_checkpointing
   - 启用bf16混合精度训练
   - 降低max_length或batch_size

2. **速度优化**
   - 增加dataloader_num_workers
   - 启用dataloader_pin_memory
   - 使用更大的batch_size（如果显存允许）

3. **稳定性优化**
   - 设置合适的save_steps和eval_steps
   - 启用load_best_model_at_end
   - 使用warmup防止训练初期不稳定

## 作业提交示例

```bash
# 完整的作业提交流程
cd /path/to/SpatialSense
chmod +x spatial_finetune.sh setup_environment.sh

# 如果是首次运行，先配置环境
./setup_environment.sh

# 编辑配置（可选）
vim finetune_config.yaml

# 提交作业
sbatch spatial_finetune.sh

# 记录作业ID
JOBID=$(squeue -h -o %i -u $USER | tail -1)
echo "Job ID: $JOBID"

# 监控作业
watch squeue -u $USER
```

预期训练时间：3-6小时（取决于数据量和GPU性能）
预期资源使用：单GPU + 8CPU + 32GB内存