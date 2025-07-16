import random
import json
import os
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import math

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

def round_coords(coords, decimals=1):
    """Round coordinates to specified decimal places"""
    return [(round(x, decimals), round(y, decimals)) for x, y in coords]

def generate_random_line(min_x=-50, max_x=50, min_y=-50, max_y=50):
    x1 = round(random.uniform(min_x, max_x), 1)
    y1 = round(random.uniform(min_y, max_y), 1)
    x2 = round(random.uniform(min_x, max_x), 1)
    y2 = round(random.uniform(min_y, max_y), 1)
    return LineString([(x1, y1), (x2, y2)])

def visualize_relation(line1, line2, relation, index):
    """Visualize the spatial relation between two lines and save to file"""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot lines
    x1, y1 = line1.xy
    x2, y2 = line2.xy
    ax.plot(x1, y1, 'b-', linewidth=2, label='Line A')
    ax.plot(x2, y2, 'r-', linewidth=2, label='Line B')
    
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
    os.makedirs(os.path.join(os.path.dirname(__file__), 'line_line_visualizations'), exist_ok=True)
    
    # Save figure
    plt.savefig(os.path.join(os.path.dirname(__file__), 'line_line_visualizations', f'relation_{index}.png'))
    plt.close()

# --- 按照之前的方法生成各类关系的线对 ---
def generate_equals():
    line = generate_random_line()
    return line, LineString(line.coords), "Equals"

def generate_contains():
    # 先生成一条随机线，再在其内部取子段
    full = generate_random_line()
    (x1, y1), (x2, y2) = full.coords
    t1, t2 = sorted([round(random.uniform(0.2, 0.4), 1), round(random.uniform(0.6, 0.8), 1)])
    part = LineString([
        (round(x1 + t1*(x2-x1), 1), round(y1 + t1*(y2-y1), 1)),
        (round(x1 + t2*(x2-x1), 1), round(y1 + t2*(y2-y1), 1))
    ])
    return full, part, "Contains"

def generate_within():
    full, part, _ = generate_contains()
    return part, full, "Within"

def generate_overlaps():
    """Generate lines that overlap"""
    line1 = generate_random_line()
    (x1, y1), (x2, y2) = line1.coords
    
    # 计算线段中点以及长度的一半
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    half_len = calculate_distance((x1, y1), (x2, y2)) / 2
    
    # 计算线段方向的单位向量
    dx = (x2 - x1) / (2 * half_len)
    dy = (y2 - y1) / (2 * half_len)
    
    # 创建一条与原线段部分重叠的线段
    overlap_fraction = round(random.uniform(0.3, 0.7), 1)  # 重叠部分占原线段的比例
    extension = round(random.uniform(0.5, 1.5), 1)  # 延伸部分长度系数
    
    # 计算新的端点（确保有部分重叠，有部分延伸）
    start_x = round(mid_x - overlap_fraction * half_len * dx, 1)
    start_y = round(mid_y - overlap_fraction * half_len * dy, 1)
    end_x = round(mid_x + half_len * dx + extension * half_len * dx, 1)
    end_y = round(mid_y + half_len * dy + extension * half_len * dy, 1)
    
    line2 = LineString([(start_x, start_y), (end_x, end_y)])
    
    # 验证确实是重叠关系
    if check_overlaps((x1, y1), (x2, y2), (start_x, start_y), (end_x, end_y)):
        return line1, line2, "Overlaps"
    else:
        # 如果生成失败，递归重试
        return generate_overlaps()

def generate_crosses():
    line1 = generate_random_line()
    (x1, y1), (x2, y2) = line1.coords
    # 垂直于 line1，且中点处穿过
    mid = (round((x1+x2)/2, 1), round((y1+y2)/2, 1))
    dx, dy = x2-x1, y2-y1
    length = round(random.uniform(5,15), 1)
    line2 = LineString([
        (round(mid[0] - dy/((dx**2+dy**2)**0.5)*length, 1),
         round(mid[1] + dx/((dx**2+dy**2)**0.5)*length, 1)),
        (round(mid[0] + dy/((dx**2+dy**2)**0.5)*length, 1),
         round(mid[1] - dx/((dx**2+dy**2)**0.5)*length, 1))
    ])
    return line1, line2, "Crosses"

def generate_touches():
    # 随机取一条线，再在它的任意一点"断开"生成第二条线
    line1 = generate_random_line()
    (x1, y1), (x2, y2) = line1.coords
    t = round(random.uniform(0,1), 1)
    # 取点 P
    px, py = round(x1 + t*(x2-x1), 1), round(y1 + t*(y2-y1), 1)
    # 计算line1的方向向量并旋转90度
    dx, dy = x2-x1, y2-y1
    length = ((dx**2+dy**2)**0.5)
    rot_dx, rot_dy = -dy/length, dx/length  # 旋转90度
    
    # 让第二条线从 P 向旋转后的方向延伸
    L = round(random.uniform(5,15), 1)
    line2 = LineString([
        (px, py),
        (round(px + rot_dx*L, 1), round(py + rot_dy*L, 1))
    ])
    return line1, line2, "Touches"

def generate_disjoint():
    # 一条线上，平移生成另一条线
    line1 = generate_random_line()
    dx, dy = round(random.uniform(20,30), 1), round(random.uniform(20,30), 1)
    line2 = LineString([
        (round(line1.coords[0][0]+dx, 1), round(line1.coords[0][1]+dy, 1)),
        (round(line1.coords[1][0]+dx, 1), round(line1.coords[1][1]+dy, 1))
    ])
    return line1, line2, "Disjoint"

def is_point_on_line(point, line_start, line_end):
    """Check if a point lies on a line segment"""
    # 计算点到线段两端点的距离
    d1 = calculate_distance(point, line_start)
    d2 = calculate_distance(point, line_end)
    d_total = calculate_distance(line_start, line_end)
    # 如果点到两端点的距离和等于线段长度，则点在线段上（容错0.1）
    return abs((d1 + d2) - d_total) < 0.1

def is_point_outside_line(point, line_start, line_end):
    """Check if a point is outside a line segment"""
    # 计算点到线段两端点的距离
    d1 = calculate_distance(point, line_start)
    d2 = calculate_distance(point, line_end)
    d_total = calculate_distance(line_start, line_end)
    # 如果点到两端点的距离和大于线段长度，则点在线段外部（容错0.1）
    return (d1 + d2) > d_total + 0.1

def check_contains(line1_start, line1_end, line2_start, line2_end):
    """Check if line1 contains line2 according to given logic"""
    # 在判断Contains关系时，需要确保两线段共线（斜率相同）且另一线段的两个端点都在这条线上
    
    # 首先检查斜率是否相同
    slope1 = calculate_slope(line1_start, line1_end)
    slope2 = calculate_slope(line2_start, line2_end)
    if abs(slope1 - slope2) > 0.1:  # 斜率不同，不可能包含
        return False
    
    # 然后检查B的端点是否都在A上
    b1_on_a = is_point_on_line(line2_start, line1_start, line1_end)
    b2_on_a = is_point_on_line(line2_end, line1_start, line1_end)
    
    # 必须两个端点都在线上，且不是Equals关系
    return b1_on_a and b2_on_a and (line2_start != line1_start or line2_end != line1_end)

def check_touches(line1_start, line1_end, line2_start, line2_end):
    """Check if lines touch according to given logic"""
    # 计算斜率
    slope1 = calculate_slope(line1_start, line1_end)
    slope2 = calculate_slope(line2_start, line2_end)
    
    # 斜率必须不同（容错0.1）
    if abs(slope1 - slope2) < 0.1:
        return False
    
    # 检查A的一个端点是否在B上，另一个端点在B外
    a1_on_b = is_point_on_line(line1_start, line2_start, line2_end)
    a1_outside_b = is_point_outside_line(line1_start, line2_start, line2_end)
    a2_on_b = is_point_on_line(line1_end, line2_start, line2_end)
    a2_outside_b = is_point_outside_line(line1_end, line2_start, line2_end)
    
    # 检查B的一个端点是否在A上，另一个端点在A外
    b1_on_a = is_point_on_line(line2_start, line1_start, line1_end)
    b1_outside_a = is_point_outside_line(line2_start, line1_start, line1_end)
    b2_on_a = is_point_on_line(line2_end, line1_start, line1_end)
    b2_outside_a = is_point_outside_line(line2_end, line1_start, line1_end)
    
    # 任何一种情况都满足触摸条件
    return ((a1_on_b and a2_outside_b) or 
            (a2_on_b and a1_outside_b) or 
            (b1_on_a and b2_outside_a) or 
            (b2_on_a and b1_outside_a))

def check_overlaps(line1_start, line1_end, line2_start, line2_end):
    """Check if lines overlap according to given logic"""
    # 计算斜率
    slope1 = calculate_slope(line1_start, line1_end)
    slope2 = calculate_slope(line2_start, line2_end)
    
    # 斜率必须相同
    if abs(slope1 - slope2) > 0.1:
        return False
    
    # 检查是否有端点在另一线段上（不包括端点完全重合的情况）
    # 首先检查线段A的端点
    a1_on_b = is_point_on_line(line1_start, line2_start, line2_end)
    a2_on_b = is_point_on_line(line1_end, line2_start, line2_end)
    
    # 检查线段B的端点
    b1_on_a = is_point_on_line(line2_start, line1_start, line1_end)
    b2_on_a = is_point_on_line(line2_end, line1_start, line1_end)
    
    # 判断是否为部分重叠：至少有一个端点在另一线段上，但不是所有端点都在（否则就是Contains或Within）
    has_common_point = a1_on_b or a2_on_b or b1_on_a or b2_on_a
    
    # 不是完全包含关系
    not_contains = not (b1_on_a and b2_on_a)
    not_within = not (a1_on_b and a2_on_b)
    
    return has_common_point and not_contains and not_within

def calculate_slope(p1, p2):
    """Calculate slope of a line segment"""
    if abs(p2[0] - p1[0]) < 0.01:
        return float('inf')
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    return round(slope, 1)  # 斜率保留一位小数

def calculate_angle(p1, p2):
    """Calculate angle of a line segment in degrees"""
    return math.degrees(math.atan2(p2[1]-p1[1], p2[0]-p1[0]))

def check_crosses(line1_start, line1_end, line2_start, line2_end):
    """Check if two line segments cross using angle method"""
    # Calculate line angles
    theta1 = calculate_angle(line1_start, line1_end)
    theta2 = calculate_angle(line2_start, line2_end)
    
    # Calculate endpoint angles for line1
    theta1_start = calculate_angle(line1_start, line2_start)
    theta1_end = calculate_angle(line1_start, line2_end)
    delta1 = theta1_start - theta1
    delta2 = theta1_end - theta1
    
    # Calculate endpoint angles for line2
    theta2_start = calculate_angle(line2_start, line1_start)
    theta2_end = calculate_angle(line2_start, line1_end)
    delta3 = theta2_start - theta2
    delta4 = theta2_end - theta2
    
    # Check if endpoints are on opposite sides
    sin1 = math.sin(math.radians(delta1))
    sin2 = math.sin(math.radians(delta2))
    sin3 = math.sin(math.radians(delta3))
    sin4 = math.sin(math.radians(delta4))
    
    # 增加容错率
    return sin1 * sin2 < -0.01 and sin3 * sin4 < -0.01

def generate_cot_reasoning(line1, line2, relation):
    """Generate Chain-of-Thought reasoning for line-line spatial relations using tool calls"""
    coords1 = list(line1.coords)
    coords2 = list(line2.coords)
    cot = []
    
    # 格式化坐标，保留一位小数
    formatted_coords1 = [tuple(round(coord, 1) for coord in point) for point in coords1]
    formatted_coords2 = [tuple(round(coord, 1) for coord in point) for point in coords2]
    cot.append(f"Line A endpoints: {formatted_coords1}")
    cot.append(f"Line B endpoints: {formatted_coords2}")
    
    # Step 1: Check if lines are equal
    cot.append("\nStep 1: Check if lines are equal")
    if line1.equals(line2):
        cot.append("→ Lines have identical endpoints → Relation = 'Equals'")
        return "\n".join(cot)
    cot.append("→ Lines are not equal, continue")
    
    # Step 2: Use tools to calculate line properties
    cot.append("\nStep 2: Calculate line properties using tools")
    
    # Calculate line lengths using distance tool
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords1[0]} and {formatted_coords1[1]}")
    length_a = calculate_distance(coords1[0], coords1[1])
    cot.append(f"→ Tool returns: {length_a:.2f} (Length of Line A)")
    
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords2[0]} and {formatted_coords2[1]}")
    length_b = calculate_distance(coords2[0], coords2[1])
    cot.append(f"→ Tool returns: {length_b:.2f} (Length of Line B)")
    
    # Calculate line directions using direction angle tool
    cot.append(f"→ Call calculate_direction_angle tool with points {formatted_coords1[0]} and {formatted_coords1[1]}")
    angle_a = calculate_direction_angle(coords1[0], coords1[1])
    cot.append(f"→ Tool returns: {angle_a:.1f}° (Direction of Line A)")
    
    cot.append(f"→ Call calculate_direction_angle tool with points {formatted_coords2[0]} and {formatted_coords2[1]}")
    angle_b = calculate_direction_angle(coords2[0], coords2[1])
    cot.append(f"→ Tool returns: {angle_b:.1f}° (Direction of Line B)")
    
    # Determine if lines are parallel (similar directions)
    angle_diff = abs(angle_a - angle_b)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    is_parallel = angle_diff < 1 or angle_diff > 179  # Allow 1-degree tolerance
    cot.append(f"→ Angle difference = {angle_diff:.1f}°")
    cot.append(f"→ Lines are {'parallel' if is_parallel else 'not parallel'}")
    
    # Step 3: Check endpoint relationships using distance tools
    cot.append("\nStep 3: Check endpoint relationships using distance tools")
    
    # Check if any endpoints of B are on line A
    points_on_line = []
    
    # Check B1 on line A
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords2[0]} and {formatted_coords1[0]}")
    d_b1_a1 = calculate_distance(coords2[0], coords1[0])
    cot.append(f"→ Tool returns: {d_b1_a1:.2f}")
    
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords2[0]} and {formatted_coords1[1]}")
    d_b1_a2 = calculate_distance(coords2[0], coords1[1])
    cot.append(f"→ Tool returns: {d_b1_a2:.2f}")
    
    b1_on_a = abs((d_b1_a1 + d_b1_a2) - length_a) < 0.1
    cot.append(f"→ Check if B1 on Line A: {d_b1_a1:.2f} + {d_b1_a2:.2f} = {d_b1_a1 + d_b1_a2:.2f} vs {length_a:.2f}")
    cot.append(f"→ B1 is {'on' if b1_on_a else 'not on'} Line A")
    if b1_on_a:
        points_on_line.append("B1 on A")
    
    # Check B2 on line A
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords2[1]} and {formatted_coords1[0]}")
    d_b2_a1 = calculate_distance(coords2[1], coords1[0])
    cot.append(f"→ Tool returns: {d_b2_a1:.2f}")
    
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords2[1]} and {formatted_coords1[1]}")
    d_b2_a2 = calculate_distance(coords2[1], coords1[1])
    cot.append(f"→ Tool returns: {d_b2_a2:.2f}")
    
    b2_on_a = abs((d_b2_a1 + d_b2_a2) - length_a) < 0.1
    cot.append(f"→ Check if B2 on Line A: {d_b2_a1:.2f} + {d_b2_a2:.2f} = {d_b2_a1 + d_b2_a2:.2f} vs {length_a:.2f}")
    cot.append(f"→ B2 is {'on' if b2_on_a else 'not on'} Line A")
    if b2_on_a:
        points_on_line.append("B2 on A")
    
    # Check A1 on line B
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords1[0]} and {formatted_coords2[0]}")
    d_a1_b1 = calculate_distance(coords1[0], coords2[0])
    cot.append(f"→ Tool returns: {d_a1_b1:.2f}")
    
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords1[0]} and {formatted_coords2[1]}")
    d_a1_b2 = calculate_distance(coords1[0], coords2[1])
    cot.append(f"→ Tool returns: {d_a1_b2:.2f}")
    
    a1_on_b = abs((d_a1_b1 + d_a1_b2) - length_b) < 0.1
    cot.append(f"→ Check if A1 on Line B: {d_a1_b1:.2f} + {d_a1_b2:.2f} = {d_a1_b1 + d_a1_b2:.2f} vs {length_b:.2f}")
    cot.append(f"→ A1 is {'on' if a1_on_b else 'not on'} Line B")
    if a1_on_b:
        points_on_line.append("A1 on B")
    
    # Check A2 on line B
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords1[1]} and {formatted_coords2[0]}")
    d_a2_b1 = calculate_distance(coords1[1], coords2[0])
    cot.append(f"→ Tool returns: {d_a2_b1:.2f}")
    
    cot.append(f"→ Call calculate_distance tool with points {formatted_coords1[1]} and {formatted_coords2[1]}")
    d_a2_b2 = calculate_distance(coords1[1], coords2[1])
    cot.append(f"→ Tool returns: {d_a2_b2:.2f}")
    
    a2_on_b = abs((d_a2_b1 + d_a2_b2) - length_b) < 0.1
    cot.append(f"→ Check if A2 on Line B: {d_a2_b1:.2f} + {d_a2_b2:.2f} = {d_a2_b1 + d_a2_b2:.2f} vs {length_b:.2f}")
    cot.append(f"→ A2 is {'on' if a2_on_b else 'not on'} Line B")
    if a2_on_b:
        points_on_line.append("A2 on B")
    
    # Step 4: Determine spatial relation based on analysis
    cot.append("\nStep 4: Determine spatial relation based on tool analysis")
    cot.append(f"→ Points on other lines: {points_on_line if points_on_line else 'None'}")
    cot.append(f"→ Lines are parallel: {is_parallel}")
    
    # Logic for determining relationship
    if is_parallel and len(points_on_line) > 0:
        if b1_on_a and b2_on_a:
            cot.append("→ Both endpoints of B are on A, and lines are parallel")
            cot.append("→ Spatial relation: 'Contains' (A contains B)")
        elif a1_on_b and a2_on_b:
            cot.append("→ Both endpoints of A are on B, and lines are parallel")
            cot.append("→ Spatial relation: 'Within' (A within B)")
        elif len(points_on_line) >= 1:
            cot.append("→ Some endpoints are on the other line, and lines are parallel")
            cot.append("→ Spatial relation: 'Overlaps'")
    elif not is_parallel and len(points_on_line) == 1:
        cot.append("→ Exactly one endpoint is on the other line, and lines are not parallel")
        cot.append("→ Spatial relation: 'Touches'")
    elif not is_parallel and len(points_on_line) == 0:
        # Check if lines might cross by using direction angles
        cot.append("→ No endpoints on other lines, and lines are not parallel")
        cot.append("→ Lines might cross - checking intersection")
        cot.append("→ Spatial relation: 'Crosses'")
    else:
        cot.append("→ No significant relationship found")
        cot.append("→ Spatial relation: 'Disjoint'")
    
    return "\n".join(cot)

# --- 生成带 CoT 推理的数据集，并保存为 JSONL ---
def generate_line_line_cot_dataset(n_each=50):
    dataset = []
    index = 0
    gens = [
        generate_equals, generate_contains, generate_within,
        generate_overlaps, generate_crosses, generate_touches, generate_disjoint
    ]
    for gen in gens:
        for _ in range(n_each):
            a, b, rel = gen()
            inp = f"Line A: {list(a.coords)};  Line B: {list(b.coords)}.  What is their spatial relation?"
            out = generate_cot_reasoning(a, b, rel)
            dataset.append({"input": inp, "output": out})
            visualize_relation(a, b, rel, index)
            index += 1
    return dataset

# 保存
data = generate_line_line_cot_dataset(100)

# 保存到代码所在目录
output_file = os.path.join(os.path.dirname(__file__), 'line_line_cot_dataset.jsonl')
with open(output_file, "w") as f:
    for item in data:
        f.write(json.dumps(item) + "\n")

print(f"✅ 生成完毕，共 {len(data)} 条带 CoT 推理样本")
print(f"✅ 可视化结果已保存到 '{os.path.join(os.path.dirname(__file__), 'line_line_visualizations')}' 文件夹中")
print(f"✅ 数据集已保存到 '{output_file}'")