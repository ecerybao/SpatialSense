import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon as MplPolygon

def plot_relationship(poly1_coords, poly2_coords, relation, ax):
    # 绘制第一个多边形
    poly1 = MplPolygon(poly1_coords, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(poly1)
    
    # 绘制第二个多边形
    poly2 = MplPolygon(poly2_coords, fill=False, edgecolor='red', linewidth=2)
    ax.add_patch(poly2)
    
    # 设置标题
    ax.set_title(f'Relation: {relation}')
    
    # 设置坐标轴范围
    all_x = [x for x, _ in poly1_coords + poly2_coords]
    all_y = [y for _, y in poly1_coords + poly2_coords]
    margin = 5
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    
    # 设置网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 设置坐标轴标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

def visualize_dataset(json_file, n_samples=3):
    # 读取数据集
    with open(json_file, 'r') as f:
        dataset = json.load(f)
    
    # 按关系类型分组
    relations = {}
    for item in dataset:
        relation = item['spatial_relation']
        if relation not in relations:
            relations[relation] = []
        relations[relation].append(item)
    
    # 为每种关系创建子图
    n_relations = len(relations)
    fig, axes = plt.subplots(n_relations, n_samples, figsize=(15, 5*n_relations))
    if n_relations == 1:
        axes = axes.reshape(1, -1)
    
    # 绘制每种关系的样本
    for i, (relation, samples) in enumerate(relations.items()):
        for j in range(n_samples):
            if j < len(samples):
                sample = samples[j]
                poly1_coords = sample['entity1']['coordinates']
                poly2_coords = sample['entity2']['coordinates']
                plot_relationship(poly1_coords, poly2_coords, relation, axes[i, j])
            else:
                axes[i, j].axis('off')
    
    plt.tight_layout()
    plt.savefig('polygon_polygon_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    visualize_dataset('polygon_polygon_dataset.json')
    print("✅ 可视化完成，结果已保存为 polygon_polygon_visualization.png") 