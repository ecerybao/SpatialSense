import json
import matplotlib.pyplot as plt
import os

def plot_relation(line1_coords, line2_coords, relation, ax):
    # 绘制第一条线段
    x1, y1 = zip(*line1_coords)
    ax.plot(x1, y1, 'b-', linewidth=2, label='Line 1')
    
    # 绘制第二条线段
    x2, y2 = zip(*line2_coords)
    ax.plot(x2, y2, 'r-', linewidth=2, label='Line 2')
    
    # 添加关系标签
    ax.text(0.5, 0.95, relation, 
            transform=ax.transAxes,
            horizontalalignment='center',
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.8))
    
    # 计算所有点的坐标范围
    all_x = x1 + x2
    all_y = y1 + y2
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # 添加边距
    margin = 5
    ax.set_xlim(min_x - margin, max_x + margin)
    ax.set_ylim(min_y - margin, max_y + margin)
    
    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例
    ax.legend(loc='upper right')
    
    # 设置相等的坐标轴比例
    ax.set_aspect('equal')

def visualize_dataset():
    # 创建保存图片的文件夹
    output_dir = 'line_line_visualizations'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取数据集
    with open('line_line_dataset.json', 'r') as f:
        dataset = json.load(f)
    
    # 定义所有关系类型
    relations = ['Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 'Disjoint']
    
    # 为每种关系创建单独的可视化
    for relation in relations:
        # 创建子图：1行3列
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f'Line-Line {relation} Relations', fontsize=16)
        
        # 获取该关系的3个样本
        samples = [item for item in dataset if item['spatial_relation'] == relation][:3]
        
        # 绘制每个样本
        for j, sample in enumerate(samples):
            line1 = sample['entity1']['coordinates']
            line2 = sample['entity2']['coordinates']
            plot_relation(line1, line2, relation, axes[j])
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(os.path.join(output_dir, f'line_line_{relation.lower()}.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"✅ 可视化图片已保存到 {output_dir} 文件夹")

if __name__ == '__main__':
    visualize_dataset() 