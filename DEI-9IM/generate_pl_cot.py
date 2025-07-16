import random
import json
import math
import os
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def generate_cot_reasoning(point, line, relation):
    p = (point.x, point.y)
    a = line.coords[0]
    b = line.coords[1]

    steps = [f"Point P is at {p}, line segment AB goes from {a} to {b}."]
    steps.append(f"Step 1: Check if point P equals endpoint A or B.")
    
    if p == a or p == b:
        steps.append(f"Point P equals {'A' if p == a else 'B'} → relation is 'Touches'.")
    else:
        d1 = distance(a, p)
        d2 = distance(p, b)
        d_total = distance(a, b)
        steps.append(f"Step 2: Compute distance: distance(A, P) = {d1:.2f}, distance(P, B) = {d2:.2f}, total distance = {d1 + d2:.2f}")
        steps.append(f"Step 3: Compare with distance(A, B) = {d_total:.2f}")
        if abs((d1 + d2) - d_total) < 1e-6:
            steps.append("Since sum of distances equals total, point lies on the line segment → relation is 'Within'.")
        else:
            steps.append("Sum of distances is greater than line segment → relation is 'Disjoint'.")

    steps.append(f"Final Answer: {relation}")
    return "\n".join(steps)

def generate_touches():
    x1 = random.randint(-50, 50)
    y1 = random.randint(-50, 50)
    x2 = random.randint(-50, 50)
    y2 = random.randint(-50, 50)
    line = LineString([(x1, y1), (x2, y2)])
    point = Point((x1, y1))  # 与端点重合
    return point, line, "Touches"

def generate_within():
    while True:
        x1 = random.randint(-50, 50)
        y1 = random.randint(-50, 50)
        dx = random.randint(-20, 20)
        dy = random.randint(-20, 20)
        x2 = x1 + dx
        y2 = y1 + dy
        line = LineString([(x1, y1), (x2, y2)])
        t = random.uniform(0.2, 0.8)  # 避免端点
        px = x1 + t * dx
        py = y1 + t * dy
        point = Point((round(px, 2), round(py, 2)))
        if point.within(line):
            return point, line, "Within"

def generate_disjoint():
    while True:
        x1 = random.randint(0, 10)
        y1 = random.randint(0, 10)
        x2 = x1 + 5
        y2 = y1 + 5
        line = LineString([(x1, y1), (x2, y2)])
        px = random.randint(20, 50)
        py = random.randint(20, 50)  # 明显远离
        point = Point((px, py))
        if point.disjoint(line):
            return point, line, "Disjoint"

def visualize_relation(point, line, relation, index):
    """Visualize the spatial relation between point and line and save to file"""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot line
    x, y = line.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Line')
    
    # Plot point
    ax.plot(point.x, point.y, 'ro', markersize=8, label='Point')
    
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
    os.makedirs(os.path.join(os.path.dirname(__file__), 'point_line_visualizations'), exist_ok=True)
    
    # Save figure
    plt.savefig(os.path.join(os.path.dirname(__file__), 'point_line_visualizations', f'relation_{index}.png'))
    plt.close()

def generate_dataset(n_each=50):
    dataset = []
    index = 0
    
    for _ in range(n_each):
        point, line, relation = generate_touches()
        input_text = f"What is the spatial relation between point {tuple(point.coords)[0]} and line {list(line.coords)}?"
        output_text = generate_cot_reasoning(point, line, relation)
        dataset.append({"input": input_text, "output": output_text})
        visualize_relation(point, line, relation, index)
        index += 1

        point, line, relation = generate_within()
        input_text = f"What is the spatial relation between point {tuple(point.coords)[0]} and line {list(line.coords)}?"
        output_text = generate_cot_reasoning(point, line, relation)
        dataset.append({"input": input_text, "output": output_text})
        visualize_relation(point, line, relation, index)
        index += 1

        point, line, relation = generate_disjoint()
        input_text = f"What is the spatial relation between point {tuple(point.coords)[0]} and line {list(line.coords)}?"
        output_text = generate_cot_reasoning(point, line, relation)
        dataset.append({"input": input_text, "output": output_text})
        visualize_relation(point, line, relation, index)
        index += 1
        
    return dataset

# 生成并保存为 JSONL 文件
dataset = generate_dataset(n_each=100)

# 保存到代码所在目录
output_file = os.path.join(os.path.dirname(__file__), 'point_line_cot_dataset.jsonl')
with open(output_file, "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")

print(f"✅ 带推理的 point-line 数据集生成完毕，共 {len(dataset)} 条记录")
print(f"✅ 可视化结果已保存到 '{os.path.join(os.path.dirname(__file__), 'point_line_visualizations')}' 文件夹中")
print(f"✅ 数据集已保存到 '{output_file}'")