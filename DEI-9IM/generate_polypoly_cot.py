import random
import json
import math
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import os

# ———— Polygon generation functions ————
def create_rectangle(x0, y0, w, h):
    # 将所有坐标值四舍五入到一位小数
    x0 = round(x0, 1)
    y0 = round(y0, 1)
    w = round(w, 1)
    h = round(h, 1)
    return Polygon([
        (x0, y0),
        (x0 + w, y0),
        (x0 + w, y0 + h),
        (x0, y0 + h),
        (x0, y0)
    ])

def generate_random_polygon(min_size=5, max_size=20):
    x0 = round(random.uniform(-50, 50), 1)
    y0 = round(random.uniform(-50, 50), 1)
    w = round(random.uniform(min_size, max_size), 1)
    h = round(random.uniform(min_size, max_size), 1)
    return create_rectangle(x0, y0, w, h)

def generate_equals():
    poly = generate_random_polygon()
    return poly, Polygon(poly.exterior.coords), "Equals"

def generate_disjoint():
    while True:
        poly1 = generate_random_polygon()
        minx, miny, maxx, maxy = poly1.bounds
        # Generate outside the first polygon
        offset = round(random.uniform(10, 20), 1)
        x0 = round(random.uniform(minx, maxx), 1)
        y0 = round(maxy + offset, 1)
        poly2 = create_rectangle(x0, y0, round(random.uniform(5,15), 1), round(random.uniform(5,15), 1))
        if poly1.disjoint(poly2):
            return poly1, poly2, "Disjoint"

def generate_overlaps():
    while True:
        poly1 = generate_random_polygon()
        minx, miny, maxx, maxy = poly1.bounds
        # Start at a random point inside
        x0 = round(random.uniform(minx+2, maxx-2), 1)
        y0 = round(random.uniform(miny+2, maxy-2), 1)
        poly2 = create_rectangle(x0, y0, round(random.uniform(5,15), 1), round(random.uniform(5,15), 1))
        if poly1.overlaps(poly2):
            return poly1, poly2, "Overlaps"

def generate_contains():
    while True:
        outer = generate_random_polygon(min_size=15, max_size=25)
        minx, miny, maxx, maxy = outer.bounds
        x0 = round(random.uniform(minx+5, maxx-10), 1)
        y0 = round(random.uniform(miny+5, maxy-10), 1)
        inner = create_rectangle(x0, y0,
                               round(random.uniform(5, min(maxx-x0-5,15)), 1),
                               round(random.uniform(5, min(maxy-y0-5,15)), 1))
        if outer.contains(inner):
            return outer, inner, "Contains"

def generate_within():
    outer, inner, _ = generate_contains()
    return inner, outer, "Within"

# ———— Helper functions for spatial relation determination ————
def calculate_angle(point, vertex1, vertex2):
    """计算∠vertex1-point-vertex2的角度（度数）"""
    # 计算向量
    vector1 = (vertex1[0] - point[0], vertex1[1] - point[1])
    vector2 = (vertex2[0] - point[0], vertex2[1] - point[1])
    
    # 计算向量的点积
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    
    # 计算向量的模
    magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
    magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)
    
    # 计算夹角的余弦值
    cos_angle = dot_product / (magnitude1 * magnitude2)
    
    # 防止由于浮点数精度问题导致的错误
    if cos_angle > 1:
        cos_angle = 1
    elif cos_angle < -1:
        cos_angle = -1
    
    # 计算角度（度数）
    angle = math.degrees(math.acos(cos_angle))
    
    return round(angle, 1)

def is_point_in_polygon(point, polygon_vertices):
    """使用角度和方法判断点是否在多边形内部"""
    angles = []  # 存储每对相邻顶点形成的角度
    total_angle = 0
    
    # 按顺序计算每个角度
    for i in range(len(polygon_vertices)):
        vertex1 = polygon_vertices[i]
        vertex2 = polygon_vertices[(i+1) % len(polygon_vertices)]
        angle = calculate_angle(point, vertex1, vertex2)
        angles.append((i, vertex1, vertex2, angle))
        total_angle += angle
    
    # 如果角度和接近360度，则点在多边形内部
    is_inside = abs(total_angle - 360) < 5  # 允许5度的误差
    return is_inside, round(total_angle, 1), angles

def check_vertices_position(poly1_vertices, poly2_vertices):
    """检查多边形1的顶点相对于多边形2的位置"""
    inside_count = 0
    outside_count = 0
    vertex_positions = []
    
    for i, vertex in enumerate(poly1_vertices):
        is_inside, total_angle, angles = is_point_in_polygon(vertex, poly2_vertices)
        position = "inside" if is_inside else "outside"
        vertex_positions.append((i, vertex, position, total_angle, angles))
        if is_inside:
            inside_count += 1
        else:
            outside_count += 1
    
    return vertex_positions, inside_count, outside_count

# ———— Chain-of-Thought reasoning template ————
def generate_cot_reasoning(p1: Polygon, p2: Polygon, relation: str) -> str:
    # Extract polygon vertices (without the closing point) and round coordinates
    poly1_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p1.exterior.coords)[:-1]]
    poly2_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p2.exterior.coords)[:-1]]
    
    cot = []
    cot.append("Definitions of Spatial Relations:")
    cot.append("1. Equals: Two polygons have identical vertices (position and order may differ)")
    cot.append("2. Contains: Polygon A contains polygon B if all vertices of B are inside A")
    cot.append("3. Within: Polygon A is within polygon B if all vertices of A are inside B")
    cot.append("4. Overlaps: Two polygons partially overlap - at least one vertex is inside while at least one vertex is outside")
    cot.append("5. Disjoint: Two polygons are completely separate - all vertices are outside of each other")
    cot.append("\nMethod to determine if a point is inside a polygon:")
    cot.append("For point P and polygon ABCD, calculate ∠APB + ∠BPC + ∠CPD + ∠DPA")
    cot.append("If the sum equals 360°, P is inside the polygon; if not, P is outside")
    cot.append("\nAnalysis:")
    cot.append(f"Polygon P₁ vertices: {poly1_vertices}")
    cot.append(f"Polygon P₂ vertices: {poly2_vertices}")
    
    # Step 1: Check for Equals relation
    cot.append("\nStep 1: Check if the two polygons have identical vertices (Equals relation)")
    
    # Compare sorted vertices
    sorted_poly1 = sorted(poly1_vertices)
    sorted_poly2 = sorted(poly2_vertices)
    
    if sorted_poly1 == sorted_poly2:
        cot.append("→ The two polygons have the exact same set of vertices")
        cot.append("→ Relation: Equals")
        return "\n".join(cot)
    
    # Step 2: Check vertex positions for both polygons
    cot.append("\nStep 2: Check positions of vertices for both polygons")
    
    # Check positions of P₁ vertices relative to P₂
    p1_positions, p1_inside_p2_count, p1_outside_p2_count = check_vertices_position(poly1_vertices, poly2_vertices)
    
    cot.append(f"\nExamining vertices of P₁ relative to P₂:")
    for i, vertex, position, total_angle, angles in p1_positions:
        cot.append(f"\n  Vertex P{vertex}:")
        # 显示每对相邻顶点形成的角度
        for j, v1, v2, angle in angles:
            cot.append(f"    ∠{chr(65+j)}P{chr(65+((j+1)%4))} = {angle}°")
        cot.append(f"    Total angle sum = {total_angle}°")
        cot.append(f"    → {position} P₂ (angle sum {'≈' if abs(total_angle - 360) < 5 else '≠'} 360°)")
    
    cot.append(f"\n  Summary: {p1_inside_p2_count} vertices inside, {p1_outside_p2_count} vertices outside")
    
    # Check positions of P₂ vertices relative to P₁
    p2_positions, p2_inside_p1_count, p2_outside_p1_count = check_vertices_position(poly2_vertices, poly1_vertices)
    
    cot.append(f"\nExamining vertices of P₂ relative to P₁:")
    for i, vertex, position, total_angle, angles in p2_positions:
        cot.append(f"\n  Vertex P{vertex}:")
        # 显示每对相邻顶点形成的角度
        for j, v1, v2, angle in angles:
            cot.append(f"    ∠{chr(65+j)}P{chr(65+((j+1)%4))} = {angle}°")
        cot.append(f"    Total angle sum = {total_angle}°")
        cot.append(f"    → {position} P₁ (angle sum {'≈' if abs(total_angle - 360) < 5 else '≠'} 360°)")
    
    cot.append(f"\n  Summary: {p2_inside_p1_count} vertices inside, {p2_outside_p1_count} vertices outside")
    
    # Step 3: Determine spatial relation based on vertex positions
    cot.append("\nStep 3: Determine spatial relation based on vertex positions")
    
    # Check for Disjoint
    if p1_outside_p2_count == len(poly1_vertices) and p2_outside_p1_count == len(poly2_vertices):
        cot.append("→ All vertices of both polygons are outside of each other")
        cot.append("→ Relation: Disjoint")
        return "\n".join(cot)
    
    # Check for Contains (P₁ contains P₂)
    if p2_inside_p1_count == len(poly2_vertices):
        cot.append("→ All vertices of P₂ are inside P₁")
        cot.append("→ Relation: Contains")
        return "\n".join(cot)
    
    # Check for Within (P₁ within P₂)
    if p1_inside_p2_count == len(poly1_vertices):
        cot.append("→ All vertices of P₁ are inside P₂")
        cot.append("→ Relation: Within")
        return "\n".join(cot)
    
    # If none of the above, must be Overlaps
    if (p1_inside_p2_count > 0 and p1_outside_p2_count > 0) or (p2_inside_p1_count > 0 and p2_outside_p1_count > 0):
        cot.append("→ Some vertices are inside while others are outside")
        cot.append("→ Relation: Overlaps")
        return "\n".join(cot)
    
    return "\n".join(cot)

def visualize_polygons(p1, p2, relation, index):
    """可视化两个多边形并保存为图像"""
    plt.figure(figsize=(8, 8))
    
    # 绘制第一个多边形
    x1, y1 = p1.exterior.xy
    plt.plot(x1, y1, 'b-', label='P₁', linewidth=2)
    plt.fill(x1, y1, alpha=0.3, color='blue')
    
    # 绘制第二个多边形
    x2, y2 = p2.exterior.xy
    plt.plot(x2, y2, 'r-', label='P₂', linewidth=2)
    plt.fill(x2, y2, alpha=0.3, color='red')
    
    # 设置图形属性
    plt.title(f'Relation: {relation}')
    plt.legend()
    plt.grid(True)
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vis_dir = os.path.join(current_dir, 'polygon_visualizations')
    
    # 确保输出目录存在
    os.makedirs(vis_dir, exist_ok=True)
    
    # 保存图像
    plt.savefig(os.path.join(vis_dir, f'sample_{index}.png'))
    plt.close()

# ———— Generate dataset with CoT reasoning ————
def generate_polygon_polygon_cot_dataset(n_each=50):
    gens = [
        generate_equals, generate_disjoint, generate_overlaps,
        generate_contains, generate_within
    ]
    dataset = []
    sample_index = 0
    for gen in gens:
        for _ in range(n_each):
            p1, p2, rel = gen()
            
            # 对多边形顶点坐标进行精度控制
            p1_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p1.exterior.coords)[:-1]]
            p2_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p2.exterior.coords)[:-1]]
            
            inp = (f"Given Polygon P₁ with vertices {p1_vertices} "
                   f"and Polygon P₂ with vertices {p2_vertices}, "
                   "what is their topological relation?")
            out = generate_cot_reasoning(p1, p2, rel)
            dataset.append({"input": inp, "output": out})
            
            # 为每个样本生成可视化图像
            visualize_polygons(p1, p2, rel, sample_index)
            sample_index += 1
    return dataset

# ———— Save as JSONL ————
data = generate_polygon_polygon_cot_dataset(100)
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(current_dir, "polygon_polygon_cot_dataset.jsonl")

with open(output_file, "w") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"✅ Completed, generated {len(data)} CoT samples")
print(f"数据文件保存在: {output_file}")
print(f"可视化图像保存在: {os.path.join(current_dir, 'polygon_visualizations')} 目录下")