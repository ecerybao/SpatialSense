import random
import json
import os
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import math

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

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

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
    """Generate Chain-of-Thought reasoning for line-line spatial relations"""
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
    
    # Step 2: Calculate slopes to determine if lines are collinear
    slope1 = round(calculate_slope(coords1[0], coords1[1]), 1)
    slope2 = round(calculate_slope(coords2[0], coords2[1]), 1)
    cot.append("\nStep 2: Calculate slopes of both lines")
    cot.append(f"  Slope of A: {slope1}")
    cot.append(f"  Slope of B: {slope2}")
    cot.append(f"  Slopes are {'equal' if abs(slope1 - slope2) < 0.1 else 'different'}")
    
    # 如果斜率不同，直接跳到触摸和交叉判断
    if abs(slope1 - slope2) > 0.1:
        cot.append("  → Slopes are different, skipping contains/within/overlaps checks")
    else:
        # Step 3: Check if A contains B
        cot.append("\nStep 3: Check if A contains B")
        # 检查线段B的端点是否都在线段A上
        b1_on_a = is_point_on_line(coords2[0], coords1[0], coords1[1])
        b2_on_a = is_point_on_line(coords2[1], coords1[0], coords1[1])
        cot.append(f"  B1 on line A: {b1_on_a}")
        cot.append(f"  B2 on line A: {b2_on_a}")
        
        if b1_on_a and b2_on_a:
            cot.append("→ Both endpoints of B lie on A and slopes are equal → Relation = 'Contains'")
            return "\n".join(cot)
        cot.append("→ A does not contain B, continue")
        
        # Step 4: Check if A is within B
        cot.append("\nStep 4: Check if A is within B")
        # 检查线段A的端点是否都在线段B上
        a1_on_b = is_point_on_line(coords1[0], coords2[0], coords2[1])
        a2_on_b = is_point_on_line(coords1[1], coords2[0], coords2[1])
        cot.append(f"  A1 on line B: {a1_on_b}")
        cot.append(f"  A2 on line B: {a2_on_b}")
        
        if a1_on_b and a2_on_b:
            cot.append("→ Both endpoints of A lie on B and slopes are equal → Relation = 'Within'")
            return "\n".join(cot)
        cot.append("→ A is not within B, continue")
        
        # Step 5: Check if lines overlap
        cot.append("\nStep 5: Check if lines overlap")
        # 检查是否有端点在另一线段上
        has_common_point = a1_on_b or a2_on_b or b1_on_a or b2_on_a
        cot.append(f"  A1 on B: {a1_on_b}")
        cot.append(f"  A2 on B: {a2_on_b}")
        cot.append(f"  B1 on A: {b1_on_a}")
        cot.append(f"  B2 on A: {b2_on_a}")
        cot.append(f"  At least one endpoint is on the other line: {has_common_point}")
        
        if has_common_point and not (a1_on_b and a2_on_b) and not (b1_on_a and b2_on_a):
            cot.append("→ Lines have same slope, at least one endpoint on other line, but not all endpoints → Relation = 'Overlaps'")
            return "\n".join(cot)
        cot.append("→ Lines do not overlap, continue")
    
    # Step 6: Check if lines touch
    cot.append("\nStep 6: Check if lines touch")
    is_touches = check_touches(coords1[0], coords1[1], coords2[0], coords2[1])
    
    # 判断端点是否在另一条线上或在线外
    a1_on_b = is_point_on_line(coords1[0], coords2[0], coords2[1])
    a1_outside_b = is_point_outside_line(coords1[0], coords2[0], coords2[1])
    a2_on_b = is_point_on_line(coords1[1], coords2[0], coords2[1])
    a2_outside_b = is_point_outside_line(coords1[1], coords2[0], coords2[1])
    b1_on_a = is_point_on_line(coords2[0], coords1[0], coords1[1])
    b1_outside_a = is_point_outside_line(coords2[0], coords1[0], coords1[1])
    b2_on_a = is_point_on_line(coords2[1], coords1[0], coords1[1])
    b2_outside_a = is_point_outside_line(coords2[1], coords1[0], coords1[1])
    
    cot.append(f"  A1 on B: {a1_on_b}, A1 outside B: {a1_outside_b}")
    cot.append(f"  A2 on B: {a2_on_b}, A2 outside B: {a2_outside_b}")
    cot.append(f"  B1 on A: {b1_on_a}, B1 outside A: {b1_outside_a}")
    cot.append(f"  B2 on A: {b2_on_a}, B2 outside A: {b2_outside_a}")
    
    if is_touches:
        cot.append("→ One endpoint of a line is on the other line, another endpoint is outside, and slopes are different → Relation = 'Touches'")
        return "\n".join(cot)
    cot.append("→ Lines do not touch, continue")
    
    # Step 7: Check if lines cross
    cot.append("\nStep 7: Check if lines cross")
    is_crosses = check_crosses(coords1[0], coords1[1], coords2[0], coords2[1])
    
    # 计算角度说明交叉判断过程
    theta_ab = round(calculate_angle(coords1[0], coords1[1]), 1)
    theta_cd = round(calculate_angle(coords2[0], coords2[1]), 1)
    
    # 计算端点方向角
    theta_ac = round(calculate_angle(coords1[0], coords2[0]), 1)
    theta_ad = round(calculate_angle(coords1[0], coords2[1]), 1)
    
    # 计算角度差
    delta1 = round(theta_ac - theta_ab, 1)
    delta2 = round(theta_ad - theta_ab, 1)
    
    # 计算端点方向角
    theta_ca = round(calculate_angle(coords2[0], coords1[0]), 1)
    theta_cb = round(calculate_angle(coords2[0], coords1[1]), 1)
    
    # 计算角度差
    delta3 = round(theta_ca - theta_cd, 1)
    delta4 = round(theta_cb - theta_cd, 1)
    
    cot.append(f"  Line A angle: {theta_ab}°")
    cot.append(f"  Line B angle: {theta_cd}°")
    cot.append(f"  Angle from A1 to B1: {theta_ac}°, delta1: {delta1}°")
    cot.append(f"  Angle from A1 to B2: {theta_ad}°, delta2: {delta2}°")
    cot.append(f"  Angle from B1 to A1: {theta_ca}°, delta3: {delta3}°")
    cot.append(f"  Angle from B1 to A2: {theta_cb}°, delta4: {delta4}°")
    
    sin1 = round(math.sin(math.radians(delta1)), 2)
    sin2 = round(math.sin(math.radians(delta2)), 2)
    sin3 = round(math.sin(math.radians(delta3)), 2)
    sin4 = round(math.sin(math.radians(delta4)), 2)
    
    cot.append(f"  sin(delta1) * sin(delta2) = {round(sin1 * sin2, 2)}")
    cot.append(f"  sin(delta3) * sin(delta4) = {round(sin3 * sin4, 2)}")
    
    if is_crosses:
        cot.append("→ A and B cross each other (endpoints of each line are on opposite sides of the other line) → Relation = 'Crosses'")
        return "\n".join(cot)
    cot.append("→ Lines do not cross, continue")
    
    # Step 8: If none of the above, lines are disjoint
    cot.append("\nStep 8: No other relation found")
    cot.append("→ Lines are 'Disjoint'")
    
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