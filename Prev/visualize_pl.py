import json
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def plot_relation(point, line, relation, ax):
    # 绘制线段
    x_coords, y_coords = zip(*line)
    ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='Line')
    
    # 绘制点
    ax.plot(point[0], point[1], 'ro', markersize=8, label='Point')
    
    # 添加关系标签
    ax.text(point[0], point[1], f' {relation}', fontsize=10)
    
    # 设置坐标轴范围
    ax.set_xlim(-60, 60)
    ax.set_ylim(-60, 60)
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 添加标题
    ax.set_title(f'Point-Line Relation: {relation}')

def visualize_dataset():
    # 读取数据集
    with open('point_line_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    # 创建子图
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.flatten()
    
    # 为每种关系选择3个样本进行可视化
    relations = ['Touches', 'Within', 'Disjoint']
    for i, relation in enumerate(relations):
        samples = [item for item in dataset if item['spatial_relation'] == relation][:3]
        for j, sample in enumerate(samples):
            point = sample['entity1']['coordinates']
            line = sample['entity2']['coordinates']
            plot_relation(point, line, relation, axes[i*3 + j])
    
    # 调整布局
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    visualize_dataset() 