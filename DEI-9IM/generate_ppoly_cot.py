import random
import json
import math
import os
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

def create_polygon():
    x0 = random.randint(-50, 0)
    y0 = random.randint(-50, 0)
    size = random.randint(10, 20)
    return Polygon([
        (x0, y0), (x0 + size, y0),
        (x0 + size, y0 + size), (x0, y0 + size),
        (x0, y0)  # close
    ])

def dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def is_on_segment(pt, seg_start, seg_end):
    d1 = dist(pt, seg_start)
    d2 = dist(pt, seg_end)
    d = dist(seg_start, seg_end)
    return abs((d1 + d2) - d) < 1e-6

def angle(a, b, c):
    """angle ABC in degrees"""
    ab = (a[0]-b[0], a[1]-b[1])
    cb = (c[0]-b[0], c[1]-b[1])
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    norm_ab = math.hypot(*ab)
    norm_cb = math.hypot(*cb)
    if norm_ab * norm_cb == 0:
        return 0
    cos_angle = max(min(dot / (norm_ab * norm_cb), 1), -1)
    return math.degrees(math.acos(cos_angle))

def generate_cot_reasoning(point, polygon, relation):
    coords = list(polygon.exterior.coords)[:-1]  # remove duplicate closing point
    pt = (point.x, point.y)
    named_points = ["A", "B", "C", "D"]
    
    reasoning = []
    reasoning.append(f"Given a polygon with vertices: " + ", ".join(f"{named_points[i]}{coords[i]}" for i in range(len(coords))) + ".")
    reasoning.append(f"And a query point P{pt}.")
    reasoning.append("\nLet's determine the spatial relation between point P and the polygon through the following steps:")
    
    # Step 1: Check if point touches any edge
    reasoning.append("\nStep 1: Check if point touches any edge")
    reasoning.append("For each edge, we check if the point lies exactly on it by verifying if the sum of distances from the point to the edge endpoints equals the edge length.")
    
    touches_found = False
    for i in range(len(coords)):
        a, b = coords[i], coords[(i + 1) % len(coords)]
        d1 = dist(pt, a)
        d2 = dist(pt, b)
        d = dist(a, b)
        reasoning.append(f"\nChecking edge {named_points[i]}{a}–{named_points[(i+1)%len(coords)]}{b}:")
        reasoning.append(f"  Distance from P to {named_points[i]}: {d1:.2f}")
        reasoning.append(f"  Distance from P to {named_points[(i+1)%len(coords)]}: {d2:.2f}")
        reasoning.append(f"  Edge length: {d:.2f}")
        reasoning.append(f"  Sum of distances: {d1 + d2:.2f}")
        
        if abs((d1 + d2) - d) < 1e-6:
            reasoning.append(f"  → Point P lies exactly on this edge!")
            reasoning.append("  Therefore, the spatial relation is 'Touches'")
            reasoning.append("\nFinal Answer: Touches")
            touches_found = True
            break
        else:
            reasoning.append("  → Point P does not lie on this edge")
    
    if touches_found:
        return "\n".join(reasoning)
    
    # Step 2: Check if point is within polygon using angle sum
    reasoning.append("\nStep 2: Check if point is within the polygon")
    reasoning.append("We calculate the sum of angles formed by the point and each pair of consecutive polygon vertices.")
    reasoning.append("If the sum is approximately 360°, the point is inside the polygon.")
    
    total_angle = 0
    for i in range(len(coords)):
        a = coords[i]
        b = pt
        c = coords[(i + 1) % len(coords)]
        ang = angle(a, b, c)
        reasoning.append(f"\nAngle at vertex {named_points[i]}:")
        reasoning.append(f"  ∠{named_points[i]}–P–{named_points[(i+1)%len(coords)]} = {ang:.2f}°")
        total_angle += ang
    
    reasoning.append(f"\nTotal angle sum = {total_angle:.2f}°")
    
    if abs(total_angle - 360) < 1e-1:
        reasoning.append("Since total angle ≈ 360°, point P is inside the polygon")
        reasoning.append("\nFinal Answer: Within")
    else:
        reasoning.append("Since total angle < 360°, point P is outside the polygon")
        reasoning.append("\nFinal Answer: Disjoint")
    
    return "\n".join(reasoning)

def generate_within():
    poly = create_polygon()
    minx, miny, maxx, maxy = poly.bounds
    while True:
        px = random.randint(int(minx)+1, int(maxx)-1)
        py = random.randint(int(miny)+1, int(maxy)-1)
        pt = Point(px, py)
        if pt.within(poly):
            return pt, poly, "Within"

def generate_disjoint():
    poly = create_polygon()
    minx, miny, maxx, maxy = poly.bounds
    offset = random.randint(10, 20)
    px = int(maxx + offset)
    py = int(maxy + offset)
    pt = Point(px, py)
    return pt, poly, "Disjoint"

def generate_touches():
    poly = create_polygon()
    coords = list(poly.exterior.coords)
    i = random.randint(0, len(coords)-2)
    a, b = coords[i], coords[i+1]
    t = random.uniform(0.2, 0.8)
    px = int(a[0] + t * (b[0] - a[0]))
    py = int(a[1] + t * (b[1] - a[1]))
    pt = Point(px, py)
    return pt, poly, "Touches"

def visualize_relation(point, polygon, relation, index):
    """Visualize the spatial relation and save to file"""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot polygon
    x, y = polygon.exterior.xy
    ax.plot(x, y, 'b-', linewidth=2, label='Polygon')
    
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
    os.makedirs(os.path.join(os.path.dirname(__file__), 'point_polygon_visualizations'), exist_ok=True)
    
    # Save figure
    plt.savefig(os.path.join(os.path.dirname(__file__), 'point_polygon_visualizations', f'relation_{index}.png'))
    plt.close()

def generate_dataset(n_each=30):
    dataset = []
    index = 0
    
    for _ in range(n_each):
        # Generate Within relation
        pt, poly, rel = generate_within()
        dataset.append({
            "input": f"What is the spatial relation between point {tuple(pt.coords)[0]} and polygon defined by {list(poly.exterior.coords)[:-1]}?",
            "output": generate_cot_reasoning(pt, poly, rel)
        })
        visualize_relation(pt, poly, rel, index)
        index += 1

        # Generate Touches relation
        pt, poly, rel = generate_touches()
        dataset.append({
            "input": f"What is the spatial relation between point {tuple(pt.coords)[0]} and polygon defined by {list(poly.exterior.coords)[:-1]}?",
            "output": generate_cot_reasoning(pt, poly, rel)
        })
        visualize_relation(pt, poly, rel, index)
        index += 1

        # Generate Disjoint relation
        pt, poly, rel = generate_disjoint()
        dataset.append({
            "input": f"What is the spatial relation between point {tuple(pt.coords)[0]} and polygon defined by {list(poly.exterior.coords)[:-1]}?",
            "output": generate_cot_reasoning(pt, poly, rel)
        })
        visualize_relation(pt, poly, rel, index)
        index += 1
        
    return dataset

# 保存数据
dataset = generate_dataset(n_each=100)

# 保存到代码所在目录
output_file = os.path.join(os.path.dirname(__file__), 'point_polygon_cot_dataset.jsonl')
with open(output_file, "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")

print(f"✅ 带推理的 point–polygon 数据集生成完毕，共 {len(dataset)} 条记录")
print(f"✅ 可视化结果已保存到 '{os.path.join(os.path.dirname(__file__), 'visualizations')}' 文件夹中")
print(f"✅ 数据集已保存到 '{output_file}'")