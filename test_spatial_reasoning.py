#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间关系判断框架测试脚本
用于测试JSONL数据集的批量测试功能
"""

import json
import sys
import os
import random
from spatial_reasoning_framework import run_comprehensive_test

def create_sample_data():
    """创建示例测试数据"""
    sample_data = [
        {
            "input": "Point A is at (-81, -87). Point B is at (-81, -87). What is the spatial relation between Point A and Point B?",
            "output": "Step 1: Call calculate_distance tool with points (-81, -87) and (-81, -87)\n→ Tool returns: 0.00\nStep 2: Since distance = 0, the spatial relation is 'Equals'."
        },
        {
            "input": "Point A is at (-30, 47). Point B is at (-21, 21). What is the spatial relation between Point A and Point B?",
            "output": "Step 1: Call calculate_distance tool with points (-30, 47) and (-21, 21)\n→ Tool returns: 27.51\nStep 2: Since distance = 27.51 > 0, the spatial relation is 'Disjoint'."
        },
        {
            "input": "Given line L with endpoints [(5.3, -41.4), (1.0, -41.4)] and polygon P with vertices [(-7.6, -49.3), (8.1, -49.3), (8.1, -33.6), (-7.6, -33.6)], determine their spatial relation.",
            "output": "Line L endpoints: A(5.3, -41.4), B(1.0, -41.4).\nPolygon P vertices: [(-7.6, -49.3), (8.1, -49.3), (8.1, -33.6), (-7.6, -33.6)].\n\nStep 1: Determine if the line endpoints are inside the polygon using direction angle tools\n→ Using angle sum method: For a point inside a polygon, the sum of direction angle changes equals ±360°\n\nChecking if point A(5.3, -41.4) is inside the polygon:\n→ Call calculate_direction_angle tool with points (5.3, -41.4) and (-7.6, -49.3)\n→ Tool returns: 211.5°\n→ Call calculate_direction_angle tool with points (5.3, -41.4) and (8.1, -49.3)\n→ Tool returns: 289.5°\n→ Angle change: 78.0°\n→ Call calculate_direction_angle tool with points (5.3, -41.4) and (8.1, -33.6)\n→ Tool returns: 70.3°\n→ Angle change: 140.7°\n→ Call calculate_direction_angle tool with points (5.3, -41.4) and (-7.6, -33.6)\n→ Tool returns: 148.8°\n→ Angle change: 78.6°\n→ Call calculate_direction_angle tool with points (5.3, -41.4) and (-7.6, -49.3)\n→ Tool returns: 211.5°\n→ Final angle change: 62.6°\n→ Total angle change for A: 360.0°\n→ Point A is inside polygon\n\nChecking if point B(1.0, -41.4) is inside the polygon:\n→ Call calculate_direction_angle tool with points (1.0, -41.4) and (-7.6, -49.3)\n→ Tool returns: 222.6°\n→ Call calculate_direction_angle tool with points (1.0, -41.4) and (8.1, -49.3)\n→ Tool returns: 311.9°\n→ Angle change: 89.4°\n→ Call calculate_direction_angle tool with points (1.0, -41.4) and (8.1, -33.6)\n→ Tool returns: 47.7°\n→ Angle change: 95.7°\n→ Call calculate_direction_angle tool with points (1.0, -41.4) and (-7.6, -33.6)\n→ Tool returns: 137.8°\n→ Angle change: 90.1°\n→ Call calculate_direction_angle tool with points (1.0, -41.4) and (-7.6, -49.3)\n→ Tool returns: 222.6°\n→ Final angle change: 84.8°\n→ Total angle change for B: 360.0°\n→ Point B is inside polygon\n\nStep 2: Both endpoints A and B are inside the polygon\n→ Spatial relation: 'Within'"
        }
    ]
    
    # 保存示例数据
    with open("sample_test_data.jsonl", "w", encoding="utf-8") as f:
        for data in sample_data:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    print("已创建示例测试数据文件: sample_test_data.jsonl")
    return "sample_test_data.jsonl"

def load_and_sample_data(jsonl_file_path: str, sample_size: int = None, random_seed: int = None) -> list:
    """加载JSONL文件并随机选取数据"""
    if random_seed is not None:
        random.seed(random_seed)
    
    # 加载所有数据
    all_data = []
    try:
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    all_data.append(data)
        print(f"成功加载 {len(all_data)} 条数据")
    except Exception as e:
        print(f"加载数据失败: {e}")
        return []
    
    # 随机选取数据
    if sample_size is None or sample_size >= len(all_data):
        selected_data = all_data
        print(f"使用全部 {len(all_data)} 条数据")
    else:
        selected_data = random.sample(all_data, sample_size)
        print(f"随机选取 {sample_size} 条数据进行测试")
    
    return selected_data

def save_sampled_data(data: list, output_file: str = "sampled_test_data.jsonl"):
    """保存选取的数据到新文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"选取的数据已保存到: {output_file}")
        return output_file
    except Exception as e:
        print(f"保存数据失败: {e}")
        return None

def main():
    """主函数"""
    print("空间关系判断框架测试脚本")
    print("="*50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        jsonl_file = sys.argv[1]
        sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
        api_key = sys.argv[3] if len(sys.argv) > 3 else None
        random_seed = int(sys.argv[4]) if len(sys.argv) > 4 else None
        
        print(f"使用参数:")
        print(f"  文件: {jsonl_file}")
        print(f"  采样数量: {sample_size}")
        print(f"  API密钥: {'已设置' if api_key else '未设置'}")
        print(f"  随机种子: {random_seed if random_seed else '无'}")
        
        # 检查文件是否存在
        if not os.path.exists(jsonl_file):
            print(f"错误: 文件 {jsonl_file} 不存在")
            return
        
        # 加载并采样数据
        sampled_data = load_and_sample_data(jsonl_file, sample_size, random_seed)
        if not sampled_data:
            print("数据加载失败，测试终止")
            return
        
        # 保存采样的数据
        temp_file = save_sampled_data(sampled_data)
        if not temp_file:
            print("保存采样数据失败，测试终止")
            return
        
        # 运行测试
        # 如果没有提供API密钥，使用默认的API密钥
        if not api_key:
            api_key = "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"
            print("使用默认API密钥")
        
        results = run_comprehensive_test(temp_file, api_key, len(sampled_data))
        
        if results:
            print(f"\n测试完成！准确率: {results['accuracy']:.2%}")
        else:
            print("测试失败")
    
    else:
        print("未提供JSONL文件路径，创建示例数据并运行测试...")
        
        # 创建示例数据
        sample_file = create_sample_data()
        
        # 运行测试（使用示例数据）
        print(f"\n使用示例数据运行测试: {sample_file}")
        # 直接传入API密钥
        api_key = "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"
        results = run_comprehensive_test(sample_file, api_key=api_key, max_tests=5)
        
        if results:
            print(f"\n示例测试完成！准确率: {results['accuracy']:.2%}")
        else:
            print("示例测试失败")
        
        print("\n使用方法:")
        print("python test_spatial_reasoning.py <jsonl_file> [sample_size] [api_key] [random_seed]")
        print("例如: python test_spatial_reasoning.py test_data.jsonl 10 your-api-key 42")
        print("参数说明:")
        print("  jsonl_file: JSONL文件路径")
        print("  sample_size: 随机采样的数据数量（可选，默认使用全部数据）")
        print("  api_key: OpenAI API密钥（可选）")
        print("  random_seed: 随机种子（可选，用于结果可重现）")

if __name__ == "__main__":
    main() 