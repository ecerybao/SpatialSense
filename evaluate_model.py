#!/usr/bin/env python3
"""
空间推理模型评估脚本
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import re
from typing import List, Dict, Any

def load_model_and_tokenizer(model_path: str):
    """Load model and tokenizer"""
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True
    )
    return model, tokenizer

def extract_spatial_relation(text: str) -> str:
    """Extract spatial relation from text"""
    # Common spatial relation patterns
    patterns = [
        r"Spatial relation: ['\"]([^'\"]+)['\"]",
        r"Final conclusion: ['\"]([^'\"]+)['\"]",
        r"Conclusion: ['\"]([^'\"]+)['\"]",
        r"Answer: ['\"]([^'\"]+)['\"]",
        r"Result: ['\"]([^'\"]+)['\"]",
        r"([A-Z][a-z]+)"  # Match capitalized words
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Filter out valid spatial relations
            valid_relations = ['Disjoint', 'Touches', 'Within', 'Overlaps', 'Equals', 'Contains', 'Crosses']
            for match in matches:
                if match in valid_relations:
                    return match
    
    return "Unknown"

def evaluate_single_sample(model, tokenizer, input_text: str, expected_output: str) -> Dict[str, Any]:
    """Evaluate a single sample"""
    # Build input
    system_prompt = """You are a spatial reasoning expert. Given two geometric objects, you need to determine their spatial relationship through step-by-step reasoning.

Available spatial relations include:
- Disjoint (separate)
- Touches (contact)
- Within (contained)
- Overlaps (overlapping)
- Equals (equal)
- Contains (containing)
- Crosses (crossing)

Please follow these steps for reasoning:
1. Analyze the properties of geometric objects
2. Use appropriate geometric tools for calculation
3. Reason step-by-step about spatial relationships
4. Draw final conclusions"""

    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{input_text}<|im_end|>\n<|im_start|>assistant\n"
    
    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract generated response part
    assistant_start = generated_text.find("<|im_start|>assistant\n")
    if assistant_start != -1:
        generated_response = generated_text[assistant_start:].replace("<|im_start|>assistant\n", "").replace("<|im_end|>", "").strip()
    else:
        generated_response = generated_text
    
    # Extract spatial relations
    predicted_relation = extract_spatial_relation(generated_response)
    expected_relation = extract_spatial_relation(expected_output)
    
    # Calculate correctness
    is_correct = predicted_relation == expected_relation
    
    return {
        "input": input_text,
        "expected_output": expected_output,
        "generated_output": generated_response,
        "expected_relation": expected_relation,
        "predicted_relation": predicted_relation,
        "is_correct": is_correct
    }

def evaluate_model(model_path: str, test_file: str):
    """Evaluate model"""
    print(f"Loading model: {model_path}")
    model, tokenizer = load_model_and_tokenizer(model_path)
    
    # Load test data
    print(f"Loading test data: {test_file}")
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = [json.loads(line) for line in f]
    
    print(f"Number of test samples: {len(test_data)}")
    
    # Evaluation results
    results = []
    correct_count = 0
    
    for i, item in enumerate(test_data):
        print(f"Evaluating sample {i+1}/{len(test_data)}")
        
        # Extract user input
        user_input = None
        for msg in item["messages"]:
            if msg["role"] == "user":
                user_input = msg["content"]
                break
        
        if user_input is None:
            continue
        
        # Extract expected output
        expected_output = None
        for msg in item["messages"]:
            if msg["role"] == "assistant":
                expected_output = msg["content"]
                break
        
        if expected_output is None:
            continue
        
        # Evaluate single sample
        result = evaluate_single_sample(model, tokenizer, user_input, expected_output)
        results.append(result)
        
        if result["is_correct"]:
            correct_count += 1
        
        # Print progress
        if (i + 1) % 10 == 0:
            accuracy = correct_count / (i + 1) * 100
            print(f"Current accuracy: {accuracy:.2f}%")
    
    # Calculate overall metrics
    total_samples = len(results)
    accuracy = correct_count / total_samples * 100 if total_samples > 0 else 0
    
    print(f"\n=== Evaluation Results ===")
    print(f"Total samples: {total_samples}")
    print(f"Correct predictions: {correct_count}")
    print(f"Accuracy: {accuracy:.2f}%")
    
    # Analyze by relation type
    relation_stats = {}
    for result in results:
        relation = result["expected_relation"]
        if relation not in relation_stats:
            relation_stats[relation] = {"total": 0, "correct": 0}
        
        relation_stats[relation]["total"] += 1
        if result["is_correct"]:
            relation_stats[relation]["correct"] += 1
    
    print(f"\n=== Analysis by Relation Type ===")
    for relation, stats in relation_stats.items():
        rel_accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{relation}: {stats['correct']}/{stats['total']} ({rel_accuracy:.2f}%)")
    
    # Save detailed results
    output_file = "evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_samples": total_samples,
                "correct_predictions": correct_count,
                "accuracy": accuracy
            },
            "relation_stats": relation_stats,
            "detailed_results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python evaluate_model.py <model_path> <test_file>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    test_file = sys.argv[2]
    
    evaluate_model(model_path, test_file) 