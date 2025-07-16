import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

def plot_relation(point, polygon_coords, relation, ax):
    # 绘制多边形
    polygon = MplPolygon(polygon_coords, fill=False, edgecolor='blue', linewidth=2)
    ax.add_patch(polygon)
    
    # 绘制点
    ax.plot(point[0], point[1], 'ro', markersize=8, label='Point')
    
    # 添加关系标签
    ax.text(point[0], point[1], f' {relation}', fontsize=10)
    
    # 设置坐标轴范围
    ax.set_xlim(-70, 70)
    ax.set_ylim(-70, 70)
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 添加标题
    ax.set_title(f'Point-Polygon Relation: {relation}')
    
    # 设置相等的坐标轴比例
    ax.set_aspect('equal')

def visualize_dataset():
    # 读取数据集
    with open('point_polygon_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    # 创建子图
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.flatten()
    
    # 为每种关系选择3个样本进行可视化
    relations = ['Within', 'Touches', 'Disjoint']
    for i, relation in enumerate(relations):
        samples = [item for item in dataset if item['spatial_relation'] == relation][:3]
        for j, sample in enumerate(samples):
            point = sample['entity1']['coordinates']
            polygon = sample['entity2']['coordinates']
            plot_relation(point, polygon, relation, axes[i*3 + j])
    
    # 调整布局
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    visualize_dataset() 