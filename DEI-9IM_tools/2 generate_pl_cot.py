import random
import json
import math
import os
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString

# 工具函数定义
def calculate_distance(p1, p2):
    """计算两点之间的欧几里得距离"""
    x1, y1 = p1
    x2, y2 = p2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def calculate_direction_angle(p1, p2):
    """计算从点1到点2的方向角度（以度为单位，相对于正x轴）"""
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 == y2:
        return None  # 相同点没有方向
    angle_radians = math.atan2(y2 - y1, x2 - x1)
    angle_degrees = math.degrees(angle_radians)
    # 将角度标准化到 [0, 360) 范围
    if angle_degrees < 0:
        angle_degrees += 360
    return angle_degrees

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def generate_cot_reasoning(point, line, relation):
    p = (point.x, point.y)
    a = line.coords[0]
    b = line.coords[1]

    reasoning = []
    reasoning.append(f"Point P is at {p}, line segment AB goes from {a} to {b}.")
    
    # Step 1: 检查是否与端点相等
    reasoning.append(f"Step 1: Check if point P equals endpoint A or B.")
    
    if p == a or p == b:
        endpoint = 'A' if p == a else 'B'
        reasoning.append(f"→ Point P equals endpoint {endpoint}")
        reasoning.append(f"Step 2: Since point equals an endpoint, the spatial relation is 'Touches'.")
    else:
        reasoning.append(f"→ Point P does not equal either endpoint")
        
        # Step 2: 调用距离计算工具
        reasoning.append(f"Step 2: Call calculate_distance tool to check if point lies on line segment.")
        
        # 计算点到两端点的距离
        dist_AP = calculate_distance(a, p)
        dist_PB = calculate_distance(p, b)
        dist_AB = calculate_distance(a, b)
        
        reasoning.append(f"→ Call calculate_distance tool with points {a} and {p}")
        reasoning.append(f"→ Tool returns: {dist_AP:.2f}")
        reasoning.append(f"→ Call calculate_distance tool with points {p} and {b}")
        reasoning.append(f"→ Tool returns: {dist_PB:.2f}")
        reasoning.append(f"→ Call calculate_distance tool with points {a} and {b}")
        reasoning.append(f"→ Tool returns: {dist_AB:.2f}")
        
        # Step 3: 判断点是否在线段上
        reasoning.append(f"Step 3: Check if distance(A,P) + distance(P,B) = distance(A,B)")
        reasoning.append(f"→ {dist_AP:.2f} + {dist_PB:.2f} = {(dist_AP + dist_PB):.2f}")
        
        if abs((dist_AP + dist_PB) - dist_AB) < 1e-6:
            reasoning.append(f"→ Sum equals line segment length, so point lies on line segment")
            reasoning.append(f"Step 4: Since point lies on line segment (not at endpoints), the spatial relation is 'Within'.")
        else:
            reasoning.append(f"→ Sum is greater than line segment length, so point is not on line segment")
            reasoning.append(f"Step 4: Since point is not on line segment, the spatial relation is 'Disjoint'.")

    return "\n".join(reasoning)

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