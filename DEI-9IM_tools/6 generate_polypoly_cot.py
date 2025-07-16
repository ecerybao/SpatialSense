import random
import json
import math
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import os

# ———— Tool functions ————
def calculate_distance(p1, p2):
    """计算两点之间的欧几里得距离"""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def calculate_direction_angle(p1, p2):
    """计算从点p1到点p2的方向角度（以度为单位，相对于正x轴）"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    return math.degrees(angle) % 360

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

# ———— Chain-of-Thought reasoning template ————
def generate_cot_reasoning(p1: Polygon, p2: Polygon, relation: str) -> str:
    # Extract polygon vertices (without the closing point) and round coordinates
    poly1_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p1.exterior.coords)[:-1]]
    poly2_vertices = [(round(x, 1), round(y, 1)) for x, y in list(p2.exterior.coords)[:-1]]
    
    cot = []
    cot.append("Tools available:")
    cot.append("1. calculate_distance(p1, p2): Calculate Euclidean distance between two points")
    cot.append("2. calculate_direction_angle(p1, p2): Calculate direction angle from p1 to p2 (in degrees)")
    cot.append("\nDefinitions of Spatial Relations:")
    cot.append("1. Equals: Two polygons have identical vertices (position and order may differ)")
    cot.append("2. Contains: Polygon A contains polygon B if all vertices of B are inside A")
    cot.append("3. Within: Polygon A is within polygon B if all vertices of A are inside B")
    cot.append("4. Overlaps: Two polygons partially overlap - at least one vertex is inside while at least one vertex is outside")
    cot.append("5. Disjoint: Two polygons are completely separate - all vertices are outside of each other")
    cot.append("\nMethod to determine if a point is inside a polygon:")
    cot.append("For point P and polygon ABCD, calculate the direction angles from P to each vertex")
    cot.append("Sum up the angle changes around the polygon. If the sum is ±360°, P is inside; otherwise, P is outside")
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
    
    cot.append("→ The polygons have different vertices, not equal")
    
    # Step 2: Check vertex positions for both polygons
    cot.append("\nStep 2: Check positions of vertices using angle sum method")
    
    # Check positions of P₁ vertices relative to P₂
    cot.append(f"\nChecking vertices of P₁ relative to P₂:")
    poly1_inside_poly2 = 0
    poly1_outside_poly2 = 0
    
    for i, vertex in enumerate(poly1_vertices):
        cot.append(f"→ Checking vertex {i+1} of P₁: {vertex}")
        
        # Calculate direction angles from vertex to each vertex of P₂
        angles = []
        for j, poly2_vertex in enumerate(poly2_vertices):
            angle = calculate_direction_angle(vertex, poly2_vertex)
            angles.append(angle)
            cot.append(f"  → Call calculate_direction_angle tool with points {vertex} and {poly2_vertex}")
            cot.append(f"  → Tool returns: {angle:.1f}°")
        
        # Calculate angle sum using winding number method
        angle_sum = 0
        cot.append(f"  → Calculating angle changes around P₂:")
        for j in range(len(angles)):
            next_j = (j + 1) % len(angles)
            angle_diff = angles[next_j] - angles[j]
            # Normalize angle difference to [-180, 180]
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            angle_sum += angle_diff
            cot.append(f"    → Angle change from vertex {j+1} to {next_j+1}: {angle_diff:.1f}°")
        
        cot.append(f"  → Total angle sum: {angle_sum:.1f}°")
        
        # Check if point is inside (angle sum ≈ ±360°)
        if abs(abs(angle_sum) - 360) < 5:
            cot.append(f"  → Since |{angle_sum:.1f}°| ≈ 360°, vertex {vertex} is inside P₂")
            poly1_inside_poly2 += 1
        else:
            cot.append(f"  → Since |{angle_sum:.1f}°| ≠ 360°, vertex {vertex} is outside P₂")
            poly1_outside_poly2 += 1
    
    cot.append(f"\nVertices of P₁ inside P₂: {poly1_inside_poly2}")
    cot.append(f"Vertices of P₁ outside P₂: {poly1_outside_poly2}")
    
    # Check positions of P₂ vertices relative to P₁
    cot.append(f"\nChecking vertices of P₂ relative to P₁:")
    poly2_inside_poly1 = 0
    poly2_outside_poly1 = 0
    
    for i, vertex in enumerate(poly2_vertices):
        cot.append(f"→ Checking vertex {i+1} of P₂: {vertex}")
        
        # Calculate direction angles from vertex to each vertex of P₁
        angles = []
        for j, poly1_vertex in enumerate(poly1_vertices):
            angle = calculate_direction_angle(vertex, poly1_vertex)
            angles.append(angle)
            cot.append(f"  → Call calculate_direction_angle tool with points {vertex} and {poly1_vertex}")
            cot.append(f"  → Tool returns: {angle:.1f}°")
        
        # Calculate angle sum using winding number method
        angle_sum = 0
        cot.append(f"  → Calculating angle changes around P₁:")
        for j in range(len(angles)):
            next_j = (j + 1) % len(angles)
            angle_diff = angles[next_j] - angles[j]
            # Normalize angle difference to [-180, 180]
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            angle_sum += angle_diff
            cot.append(f"    → Angle change from vertex {j+1} to {next_j+1}: {angle_diff:.1f}°")
        
        cot.append(f"  → Total angle sum: {angle_sum:.1f}°")
        
        # Check if point is inside (angle sum ≈ ±360°)
        if abs(abs(angle_sum) - 360) < 5:
            cot.append(f"  → Since |{angle_sum:.1f}°| ≈ 360°, vertex {vertex} is inside P₁")
            poly2_inside_poly1 += 1
        else:
            cot.append(f"  → Since |{angle_sum:.1f}°| ≠ 360°, vertex {vertex} is outside P₁")
            poly2_outside_poly1 += 1
    
    cot.append(f"\nVertices of P₂ inside P₁: {poly2_inside_poly1}")
    cot.append(f"Vertices of P₂ outside P₁: {poly2_outside_poly1}")
    
    # Step 3: Determine spatial relation based on vertex positions
    cot.append("\nStep 3: Determine spatial relation based on vertex positions")
    
    # Check for Contains (P₁ contains P₂)
    if poly1_inside_poly2 == 0 and poly2_inside_poly1 == len(poly2_vertices):
        cot.append("→ All vertices of P₂ are inside P₁")
        cot.append("→ No vertices of P₁ are inside P₂")
        cot.append("→ Relation: Contains")
    
    # Check for Within (P₁ within P₂)
    elif poly1_inside_poly2 == len(poly1_vertices) and poly2_inside_poly1 == 0:
        cot.append("→ All vertices of P₁ are inside P₂")
        cot.append("→ No vertices of P₂ are inside P₁")
        cot.append("→ Relation: Within")
    
    # Check for Overlaps
    elif poly1_inside_poly2 > 0 and poly2_inside_poly1 > 0:
        cot.append("→ Some vertices of P₁ are inside P₂")
        cot.append("→ Some vertices of P₂ are inside P₁")
        cot.append("→ Relation: Overlaps")
    
    # Check for Disjoint
    else:
        cot.append("→ No vertices of either polygon are inside the other")
        cot.append("→ Relation: Disjoint")
    
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