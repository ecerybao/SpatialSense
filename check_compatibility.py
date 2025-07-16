#!/usr/bin/env python3
"""
检查训练脚本兼容性的测试脚本
"""

import sys
import importlib.util

def check_transformers_version():
    """检查transformers版本"""
    try:
        import transformers
        from transformers import TrainingArguments
        
        version = transformers.__version__
        print(f"✓ Transformers version: {version}")
        
        # 测试TrainingArguments参数
        try:
            # 测试新版本参数
            args = TrainingArguments(
                output_dir="./test",
                eval_strategy="steps",
                num_train_epochs=1
            )
            print("✓ Using 'eval_strategy' parameter (new version)")
            return True
        except TypeError:
            try:
                # 测试旧版本参数
                args = TrainingArguments(
                    output_dir="./test",
                    evaluation_strategy="steps",
                    num_train_epochs=1
                )
                print("✓ Using 'evaluation_strategy' parameter (old version)")
                print("⚠️  建议更新到transformers>=4.20.0版本")
                return True
            except TypeError as e:
                print(f"✗ TrainingArguments参数错误: {e}")
                return False
        
    except ImportError as e:
        print(f"✗ Transformers导入失败: {e}")
        return False

def check_other_dependencies():
    """检查其他依赖"""
    deps = {
        'torch': 'PyTorch',
        'peft': 'PEFT (LoRA)',
        'datasets': 'Datasets',
        'yaml': 'PyYAML'
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            if module == 'yaml':
                import yaml
            else:
                __import__(module)
            print(f"✓ {name} 已安装")
        except ImportError:
            print(f"✗ {name} 未安装")
            all_ok = False
    
    return all_ok

def check_cuda():
    """检查CUDA可用性"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA 可用，GPU数量: {torch.cuda.device_count()}")
            print(f"✓ GPU设备: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️  CUDA 不可用，将使用CPU训练（不推荐）")
            return False
    except ImportError:
        print("✗ PyTorch 未安装")
        return False

def check_config_file():
    """检查配置文件"""
    import os
    
    if os.path.exists("finetune_config.yaml"):
        print("✓ 配置文件 finetune_config.yaml 存在")
        try:
            import yaml
            with open("finetune_config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            print("✓ 配置文件格式正确")
            return True
        except Exception as e:
            print(f"✗ 配置文件格式错误: {e}")
            return False
    else:
        print("✗ 配置文件 finetune_config.yaml 不存在")
        return False

def main():
    print("="*50)
    print("SpatialSense 训练环境兼容性检查")
    print("="*50)
    
    checks = [
        ("Transformers版本", check_transformers_version),
        ("其他依赖", check_other_dependencies),
        ("CUDA支持", check_cuda),
        ("配置文件", check_config_file)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        result = check_func()
        results.append(result)
    
    print("\n" + "="*50)
    print("检查结果:")
    
    if all(results):
        print("✓ 所有检查通过，可以开始训练")
        print("\n建议执行命令:")
        print("python finetune_script.py")
    else:
        print("✗ 存在问题，需要修复")
        print("\n建议操作:")
        if not results[0]:
            print("1. 更新transformers: pip install transformers>=4.35.0")
        if not results[1]:
            print("2. 安装缺失依赖: pip install -r requirements.txt")
        if not results[2]:
            print("3. 检查CUDA安装或使用CPU训练")
        if not results[3]:
            print("4. 检查配置文件是否存在和格式正确")

if __name__ == "__main__":
    main()