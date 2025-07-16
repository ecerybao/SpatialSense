#!/usr/bin/env python3
"""
空间推理LLM微调脚本
"""

import os
import yaml
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import json

def load_config(config_path: str) -> dict:
    """Load configuration file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 确保数值类型参数是正确的类型
    training_config = config.get("training", {})
    
    # 转换数值类型参数
    numeric_params = {
        'learning_rate': float,
        'weight_decay': float,
        'num_train_epochs': int,
        'per_device_train_batch_size': int,
        'per_device_eval_batch_size': int,
        'gradient_accumulation_steps': int,
        'warmup_steps': int,
        'save_steps': int,
        'eval_steps': int,
        'save_total_limit': int,
        'logging_steps': int
    }
    
    for param, param_type in numeric_params.items():
        if param in training_config:
            training_config[param] = param_type(training_config[param])
    
    # 转换布尔类型参数
    bool_params = ['remove_unused_columns', 'dataloader_pin_memory', 'bf16', 'gradient_checkpointing']
    for param in bool_params:
        if param in training_config:
            training_config[param] = bool(training_config[param])
    
    # 转换LoRA参数
    if "lora" in config:
        lora_config = config["lora"]
        lora_numeric_params = {
            'r': int,
            'lora_alpha': int,
            'lora_dropout': float
        }
        for param, param_type in lora_numeric_params.items():
            if param in lora_config:
                lora_config[param] = param_type(lora_config[param])
    
    return config

def load_jsonl_data(file_path: str) -> list:
    """Load JSONL data"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def format_chat_template(messages: list) -> str:
    """Format chat template"""
    formatted = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "system":
            formatted += f"<|im_start|>system\n{content}<|im_end|>\n"
        elif role == "user":
            formatted += f"<|im_start|>user\n{content}<|im_end|>\n"
        elif role == "assistant":
            formatted += f"<|im_start|>assistant\n{content}<|im_end|>\n"
    
    return formatted

def prepare_dataset(data: list, tokenizer) -> Dataset:
    """Prepare dataset"""
    formatted_data = []
    
    for item in data:
        # 格式化聊天模板
        text = format_chat_template(item["messages"])
        
        # 编码文本
        encoded = tokenizer(
            text,
            truncation=True,
            max_length=2048,
            padding=False,
            return_tensors=None
        )
        
        formatted_data.append({
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"]
        })
    
    return Dataset.from_list(formatted_data)

def main():
    # 加载配置
    config = load_config("finetune_config.yaml")
    
    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # 检查transformers版本
    import transformers
    print(f"Transformers version: {transformers.__version__}")
    
    # Load model and tokenizer
    model_name = config["model"]["base_model"]
    print(f"Loading model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Set pad_token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load data
    print("Loading training data...")
    train_data = load_jsonl_data(config["training"]["train_file"])
    val_data = load_jsonl_data(config["training"]["validation_file"])
    
    print(f"Training samples: {len(train_data)}")
    print(f"Validation samples: {len(val_data)}")
    
    # Prepare datasets
    print("Preparing datasets...")
    train_dataset = prepare_dataset(train_data, tokenizer)
    val_dataset = prepare_dataset(val_data, tokenizer)
    
    # Configure LoRA
    lora_config = LoraConfig(
        r=config["lora"]["r"],
        lora_alpha=config["lora"]["lora_alpha"],
        target_modules=config["lora"]["target_modules"],
        lora_dropout=config["lora"]["lora_dropout"],
        bias=config["lora"]["bias"],
        task_type=TaskType.CAUSAL_LM
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=config["training"]["output_dir"],
        num_train_epochs=config["training"]["num_train_epochs"],
        per_device_train_batch_size=config["training"]["per_device_train_batch_size"],
        per_device_eval_batch_size=config["training"]["per_device_eval_batch_size"],
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        optim=config["training"]["optim"],
        weight_decay=config["training"]["weight_decay"],
        save_steps=config["training"]["save_steps"],
        eval_steps=config["training"]["eval_steps"],
        save_total_limit=config["training"]["save_total_limit"],
        logging_steps=config["training"]["logging_steps"],
        report_to=config["training"]["report_to"],
        remove_unused_columns=config["training"]["remove_unused_columns"],
        dataloader_pin_memory=config["training"]["dataloader_pin_memory"],
        bf16=config["training"]["bf16"],
        gradient_checkpointing=config["training"]["gradient_checkpointing"],
        eval_strategy="steps",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )
    
    # Trainer (版本兼容性处理)
    import transformers
    transformers_version = tuple(map(int, transformers.__version__.split('.')[:2]))
    
    if transformers_version >= (4, 40):
        # 新版本使用 processing_class
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            processing_class=tokenizer,
        )
    else:
        # 旧版本使用 tokenizer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )
    
    # Start training
    print("Starting training...")
    trainer.train()
    
    # Save model
    print("Saving model...")
    trainer.save_model()
    tokenizer.save_pretrained(config["training"]["output_dir"])
    
    print("Training completed!")

if __name__ == "__main__":
    main() 