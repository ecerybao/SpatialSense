import json
import random
from typing import List, Dict, Any
import os

def load_jsonl_data(file_path: str) -> List[Dict[str, Any]]:
    """Load JSONL format data"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def format_for_finetune(data: List[Dict[str, Any]], task_type: str) -> List[Dict[str, Any]]:
    """Format data for fine-tuning"""
    formatted_data = []
    
    for item in data:
        # Build system prompt
        system_prompt = f"""You are a spatial reasoning expert. Given two geometric objects, you need to determine their spatial relationship through step-by-step reasoning.

Available spatial relations include:
- Disjoint
- Touches
- Within
- Overlaps
- Equals
- Contains
- Crosses

Please follow these steps for reasoning:
1. Analyze the properties of geometric objects
2. Use appropriate geometric tools for calculation
3. Reason step-by-step about spatial relationships
4. Draw final conclusions

Task type: {task_type}"""

        # Build user prompt
        user_prompt = item['input']
        
        # Build assistant response
        assistant_response = item['output']
        
        formatted_item = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response}
            ]
        }
        
        formatted_data.append(formatted_item)
    
    return formatted_data

def split_data(data: List[Dict[str, Any]], train_ratio: float = 0.8, val_ratio: float = 0.1) -> tuple:
    """Split data into training, validation and test sets"""
    random.shuffle(data)
    
    total = len(data)
    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))
    
    train_data = data[:train_end]
    val_data = data[train_end:val_end]
    test_data = data[val_end:]
    
    return train_data, val_data, test_data

def save_jsonl(data: List[Dict[str, Any]], file_path: str):
    """Save data as JSONL format"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    # Data file paths
    data_files = {
        'point_point': 'DEI-9IM_tools/point_point_cot_dataset.jsonl',
        'point_line': 'DEI-9IM_tools/point_line_cot_dataset.jsonl',
        'point_polygon': 'DEI-9IM_tools/point_polygon_cot_dataset.jsonl',
        'line_line': 'DEI-9IM_tools/line_line_cot_dataset.jsonl',
        'line_polygon': 'DEI-9IM_tools/line_polygon_cot_dataset.jsonl',
        'polygon_polygon': 'DEI-9IM_tools/polygon_polygon_cot_dataset.jsonl'
    }
    
    all_formatted_data = []
    
    # Process each type of data
    for task_type, file_path in data_files.items():
        print(f"Processing {task_type} data...")
        
        # Load raw data
        raw_data = load_jsonl_data(file_path)
        print(f"  - Loaded {len(raw_data)} samples")
        
        # Format for fine-tuning
        formatted_data = format_for_finetune(raw_data, task_type)
        all_formatted_data.extend(formatted_data)
        
        print(f"  - Formatting completed")
    
    print(f"\nTotal processed samples: {len(all_formatted_data)}")
    
    # Split data
    train_data, val_data, test_data = split_data(all_formatted_data)
    
    print(f"Training set: {len(train_data)} samples")
    print(f"Validation set: {len(val_data)} samples")
    print(f"Test set: {len(test_data)} samples")
    
    # Save data
    os.makedirs('finetune_data', exist_ok=True)
    
    save_jsonl(train_data, 'finetune_data/train.jsonl')
    save_jsonl(val_data, 'finetune_data/val.jsonl')
    save_jsonl(test_data, 'finetune_data/test.jsonl')
    
    print("\nData saved to finetune_data/ directory")

if __name__ == "__main__":
    main() 