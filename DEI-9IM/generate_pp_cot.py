import random
import json
import os
import matplotlib.pyplot as plt

# CoT推理生成函数
def generate_cot_reasoning(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    reasoning = []

    reasoning.append(f"Step 1: Compare the x-coordinates: {x1} vs {x2}")
    if x1 == x2:
        reasoning.append("→ they are equal.")
    else:
        reasoning.append("→ they are different.")

    reasoning.append(f"Step 2: Compare the y-coordinates: {y1} vs {y2}")
    if y1 == y2:
        reasoning.append("→ they are equal.")
    else:
        reasoning.append("→ they are different.")

    if x1 == x2 and y1 == y2:
        conclusion = "Conclusion: Since both coordinates match, the spatial relation is 'Equals'."
    else:
        conclusion = "Conclusion: Since at least one coordinate differs, the spatial relation is 'Disjoint'."

    reasoning.append(conclusion)
    return "\n".join(reasoning)

# 等于关系
def generate_point_equals():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return ([x, y], [x, y], "Equals")

# 不相交关系
def generate_point_disjoint():
    x1 = random.randint(-100, 100)
    y1 = random.randint(-100, 100)
    while True:
        x2 = random.randint(-100, 100)
        y2 = random.randint(-100, 100)
        if x1 != x2 or y1 != y2:
            break
    return ([x1, y1], [x2, y2], "Disjoint")

def visualize_points(p1, p2, relation, index):
    """Visualize the spatial relation between two points and save to file"""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot points
    ax.plot(p1[0], p1[1], 'ro', markersize=8, label='Point A')
    ax.plot(p2[0], p2[1], 'bo', markersize=8, label='Point B')
    
    # Set title and labels
    ax.set_title(f'Spatial Relation: {relation}')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'point_point_visualizations'), exist_ok=True)
    
    # Save figure
    plt.savefig(os.path.join(os.path.dirname(__file__), 'point_point_visualizations', f'relation_{index}.png'))
    plt.close()

# 构造含推理的数据集
def generate_point_point_cot_dataset(n_equals=50, n_disjoint=50):
    dataset = []
    index = 0

    for _ in range(n_equals):
        p1, p2, relation = generate_point_equals()
        input_text = f"Point A is at ({p1[0]}, {p1[1]}). Point B is at ({p2[0]}, {p2[1]}). What is the spatial relation between Point A and Point B?"
        output_text = generate_cot_reasoning(p1, p2)
        dataset.append({"input": input_text, "output": output_text})
        visualize_points(p1, p2, relation, index)
        index += 1

    for _ in range(n_disjoint):
        p1, p2, relation = generate_point_disjoint()
        input_text = f"Point A is at ({p1[0]}, {p1[1]}). Point B is at ({p2[0]}, {p2[1]}). What is the spatial relation between Point A and Point B?"
        output_text = generate_cot_reasoning(p1, p2)
        dataset.append({"input": input_text, "output": output_text})
        visualize_points(p1, p2, relation, index)
        index += 1

    return dataset

# 保存为 JSONL 文件（每行一条，适合SFT微调）
dataset = generate_point_point_cot_dataset(100, 100)

# 保存到代码所在目录
output_file = os.path.join(os.path.dirname(__file__), 'point_point_cot_dataset.jsonl')
with open(output_file, "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")

print(f"✅ 带推理数据集生成完毕，共 {len(dataset)} 条记录")
print(f"✅ 可视化结果已保存到 '{os.path.join(os.path.dirname(__file__), 'point_point_visualizations')}' 文件夹中")
print(f"✅ 数据集已保存到 '{output_file}'")