import random
import json
import math
import os
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, Point

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


# Create directories for saving results
def ensure_directory(directory):
    """Ensure the directory exists, create it if not"""
    full_path = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

# Create visualization directory
vis_dir = ensure_directory('line_polygon_visualizations')

# ———— Original generation functions ————
def generate_polygon():
    x0, y0 = random.uniform(-50, 0), random.uniform(-50, 0)
    size = random.uniform(10, 20)
    # Round to one decimal place
    x0, y0 = round(x0, 1), round(y0, 1)
    size = round(size, 1)
    return Polygon([
        (x0, y0),
        (x0 + size, y0),
        (x0 + size, y0 + size),
        (x0, y0 + size),
        (x0, y0)
    ])

def generate_within():
    poly = generate_polygon()
    minx, miny, maxx, maxy = [round(coord, 1) for coord in poly.bounds]
    while True:
        x1 = round(random.uniform(minx + 1, maxx - 1), 1)
        y1 = round(random.uniform(miny + 1, maxy - 1), 1)
        x2 = round(random.uniform(minx + 1, maxx - 1), 1)
        y2 = round(random.uniform(miny + 1, maxy - 1), 1)
        line = LineString([(x1, y1), (x2, y2)])
        if line.within(poly):
            return line, poly, "Within"

def generate_touches():
    while True:
        poly = generate_polygon()
        minx, miny, maxx, maxy = [round(coord, 1) for coord in poly.bounds]
        side = random.choice(['top','bottom','left','right'])
        if side=='top':
            tx, ty = round(random.uniform(minx, maxx), 1), round(maxy, 1)
            lx, ly = round(tx, 1), round(ty + random.uniform(1, 5), 1)
        elif side=='bottom':
            tx, ty = round(random.uniform(minx, maxx), 1), round(miny, 1)
            lx, ly = round(tx, 1), round(ty - random.uniform(1, 5), 1)
        elif side=='left':
            tx, ty = round(minx, 1), round(random.uniform(miny, maxy), 1)
            lx, ly = round(tx - random.uniform(1, 5), 1), round(ty, 1)
        else:
            tx, ty = round(maxx, 1), round(random.uniform(miny, maxy), 1)
            lx, ly = round(tx + random.uniform(1, 5), 1), round(ty, 1)
        line = LineString([(tx, ty), (lx, ly)])
        if line.touches(poly) and not line.crosses(poly):
            return line, poly, "Touches"

def generate_disjoint():
    poly = generate_polygon()
    minx, miny, maxx, maxy = [round(coord, 1) for coord in poly.bounds]
    off = round(random.uniform(10, 20), 1)
    # Generate a line outside the polygon
    x1 = round(random.uniform(minx, maxx), 1)
    y1 = round(maxy + off, 1)
    x2 = round(x1 + random.uniform(-5, 5), 1)
    y2 = round(y1 + random.uniform(1, 5), 1)
    line = LineString([(x1, y1), (x2, y2)])
    return line, poly, "Disjoint"

def generate_crosses():
    while True:
        poly = generate_polygon()
        minx, miny, maxx, maxy = [round(coord, 1) for coord in poly.bounds]
        # Horizontal crossing
        y = round(random.uniform(miny, maxy), 1)
        length = round((maxx-minx)*1.5, 1)
        x1, x2 = round(minx - length, 1), round(maxx + length, 1)
        line = LineString([(x1, y), (x2, y)])
        if line.crosses(poly):
            return line, poly, "Crosses"

# Visualization function
def visualize_relation(line, poly, relation, index):
    """Visualize the spatial relationship between a line and polygon"""
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw polygon
    x, y = poly.exterior.xy
    # Round coordinates for display
    x = [round(val, 1) for val in x]
    y = [round(val, 1) for val in y]
    ax.fill(x, y, alpha=0.5, fc='blue', ec='black')
    
    # Draw line segment
    x, y = line.xy
    # Round coordinates for display
    x = [round(val, 1) for val in x]
    y = [round(val, 1) for val in y]
    ax.plot(x, y, 'red', linewidth=2)
    
    # Draw line endpoints
    ax.plot(x[0], y[0], 'ro', markersize=6)  # Start point
    ax.plot(x[1], y[1], 'ro', markersize=6)  # End point
    
    # Set title
    ax.set_title(f'Spatial Relation: {relation}')
    
    # Set axis labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save image
    plt.savefig(os.path.join(vis_dir, f'relation_{index}.png'))
    plt.close()

# —— Helper functions ——
def is_point_on_line(point, line_start, line_end):
    """Check if a point lies on a line segment"""
    d1 = calculate_distance(point, line_start)
    d2 = calculate_distance(point, line_end)
    line_length = calculate_distance(line_start, line_end)
    return abs((d1 + d2) - line_length) < 0.1

def calculate_angle(origin, point):
    """Calculate angle (in radians) from origin to point"""
    return round(math.atan2(point[1] - origin[1], point[0] - origin[0]), 1)

def check_point_in_polygon(point, polygon_vertices):
    """Check if a point is inside a polygon (using angle sum method)"""
    # Calculate angles from point to polygon vertices
    angles = []
    for i in range(len(polygon_vertices)-1):
        angle = calculate_angle(point, polygon_vertices[i]) - calculate_angle(point, polygon_vertices[i+1])
        # Normalize angle
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        angles.append(round(angle, 1))
    
    # Calculate absolute value of angle sum
    angle_sum = abs(sum(angles))
    # If close to 2π, the point is inside the polygon
    return abs(angle_sum - 2*math.pi) < 0.1

def check_line_segment_intersection(line1_start, line1_end, line2_start, line2_end):
    """Check if two line segments intersect (using angle method)"""
    # Calculate line direction angles
    theta1 = calculate_angle(line1_start, line1_end)
    theta2 = calculate_angle(line2_start, line2_end)
    
    # Calculate endpoint direction angles and angle differences
    theta_ac = calculate_angle(line1_start, line2_start)
    theta_ad = calculate_angle(line1_start, line2_end)
    delta1 = round(theta_ac - theta1, 1)
    delta2 = round(theta_ad - theta1, 1)
    
    # Calculate another set of endpoint direction angles and differences
    theta_ca = calculate_angle(line2_start, line1_start)
    theta_cb = calculate_angle(line2_start, line1_end)
    delta3 = round(theta_ca - theta2, 1)
    delta4 = round(theta_cb - theta2, 1)
    
    # Normalize angle differences
    while delta1 > math.pi: delta1 -= 2*math.pi
    while delta1 < -math.pi: delta1 += 2*math.pi
    while delta2 > math.pi: delta2 -= 2*math.pi
    while delta2 < -math.pi: delta2 += 2*math.pi
    while delta3 > math.pi: delta3 -= 2*math.pi
    while delta3 < -math.pi: delta3 += 2*math.pi
    while delta4 > math.pi: delta4 -= 2*math.pi
    while delta4 < -math.pi: delta4 += 2*math.pi
    
    # Check if endpoints are on opposite sides of the other line
    return (round(math.sin(delta1), 1) * round(math.sin(delta2), 1) < 0) and (round(math.sin(delta3), 1) * round(math.sin(delta4), 1) < 0)

# ———— Chain-of-Thought reasoning template using tool calls ————
def generate_cot_reasoning(line, poly, relation):
    coords = list(line.coords)
    A, B = [tuple(round(c, 1) for c in point) for point in coords]
    polygon_vertices = list(poly.exterior.coords)
    polygon_vertices = [tuple(round(c, 1) for c in vertex) for vertex in polygon_vertices]
    
    cot = []
    cot.append(f"Line L endpoints: A{A}, B{B}.")
    cot.append(f"Polygon P vertices: {polygon_vertices[:-1]}.")
    
    cot.append("\nStep 1: Determine if the line endpoints are inside the polygon using direction angle tools")
    cot.append("→ Using angle sum method: For a point inside a polygon, the sum of direction angle changes equals ±360°")
    
    # Analyze point A using tool calls
    cot.append(f"\nChecking if point A{A} is inside the polygon:")
    prev_angle_A = None
    total_angle_change_A = 0
    
    for i in range(len(polygon_vertices)-1):
        vertex = polygon_vertices[i]
        cot.append(f"→ Call calculate_direction_angle tool with points {A} and {vertex}")
        
        angle_to_vertex = calculate_direction_angle(A, vertex)
        cot.append(f"→ Tool returns: {angle_to_vertex:.1f}°")
        
        if prev_angle_A is not None:
            # Calculate angle change
            angle_diff = angle_to_vertex - prev_angle_A
            # Normalize to [-180, 180] range
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            
            cot.append(f"→ Angle change: {angle_diff:.1f}°")
            total_angle_change_A += angle_diff
        
        prev_angle_A = angle_to_vertex
    
    # Handle the wrap-around from last vertex back to first vertex
    first_vertex = polygon_vertices[0]
    cot.append(f"→ Call calculate_direction_angle tool with points {A} and {first_vertex}")
    first_angle_A = calculate_direction_angle(A, first_vertex)
    cot.append(f"→ Tool returns: {first_angle_A:.1f}°")
    
    final_angle_diff_A = first_angle_A - prev_angle_A
    if final_angle_diff_A > 180:
        final_angle_diff_A -= 360
    elif final_angle_diff_A < -180:
        final_angle_diff_A += 360
    
    cot.append(f"→ Final angle change: {final_angle_diff_A:.1f}°")
    total_angle_change_A += final_angle_diff_A
    
    cot.append(f"→ Total angle change for A: {total_angle_change_A:.1f}°")
    A_in_poly = abs(abs(total_angle_change_A) - 360) < 10
    cot.append(f"→ Point A is {'inside' if A_in_poly else 'outside'} polygon")
    
    # Analyze point B using tool calls
    cot.append(f"\nChecking if point B{B} is inside the polygon:")
    prev_angle_B = None
    total_angle_change_B = 0
    
    for i in range(len(polygon_vertices)-1):
        vertex = polygon_vertices[i]
        cot.append(f"→ Call calculate_direction_angle tool with points {B} and {vertex}")
        
        angle_to_vertex = calculate_direction_angle(B, vertex)
        cot.append(f"→ Tool returns: {angle_to_vertex:.1f}°")
        
        if prev_angle_B is not None:
            # Calculate angle change
            angle_diff = angle_to_vertex - prev_angle_B
            # Normalize to [-180, 180] range
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            
            cot.append(f"→ Angle change: {angle_diff:.1f}°")
            total_angle_change_B += angle_diff
        
        prev_angle_B = angle_to_vertex
    
    # Handle the wrap-around for point B
    cot.append(f"→ Call calculate_direction_angle tool with points {B} and {first_vertex}")
    first_angle_B = calculate_direction_angle(B, first_vertex)
    cot.append(f"→ Tool returns: {first_angle_B:.1f}°")
    
    final_angle_diff_B = first_angle_B - prev_angle_B
    if final_angle_diff_B > 180:
        final_angle_diff_B -= 360
    elif final_angle_diff_B < -180:
        final_angle_diff_B += 360
    
    cot.append(f"→ Final angle change: {final_angle_diff_B:.1f}°")
    total_angle_change_B += final_angle_diff_B
    
    cot.append(f"→ Total angle change for B: {total_angle_change_B:.1f}°")
    B_in_poly = abs(abs(total_angle_change_B) - 360) < 10
    cot.append(f"→ Point B is {'inside' if B_in_poly else 'outside'} polygon")
    
    # CASE 1: Within relationship - both endpoints inside polygon
    if A_in_poly and B_in_poly:
        cot.append("\nStep 2: Both endpoints A and B are inside the polygon")
        cot.append("→ Spatial relation: 'Within'")
        return "\n".join(cot)
    
    # Step 2: Check for edge intersections using distance and angle tools
    cot.append("\nStep 2: Check if the line segment intersects any polygon edge using tools")
    
    has_intersection = False
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        
        cot.append(f"\nChecking intersection with edge {i+1}: {v1}-{v2}")
        
        # Calculate line directions using direction angle tool
        cot.append(f"→ Call calculate_direction_angle tool with points {A} and {B}")
        line_angle = calculate_direction_angle(A, B)
        cot.append(f"→ Tool returns: {line_angle:.1f}° (Line AB direction)")
        
        cot.append(f"→ Call calculate_direction_angle tool with points {v1} and {v2}")
        edge_angle = calculate_direction_angle(v1, v2)
        cot.append(f"→ Tool returns: {edge_angle:.1f}° (Edge direction)")
        
        # Test if polygon vertices are on opposite sides of line AB
        cot.append(f"→ Call calculate_direction_angle tool with points {A} and {v1}")
        angle_av1 = calculate_direction_angle(A, v1)
        cot.append(f"→ Tool returns: {angle_av1:.1f}°")
        
        cot.append(f"→ Call calculate_direction_angle tool with points {A} and {v2}")
        angle_av2 = calculate_direction_angle(A, v2)
        cot.append(f"→ Tool returns: {angle_av2:.1f}°")
        
        # Calculate angle differences and check sides
        delta1 = angle_av1 - line_angle
        delta2 = angle_av2 - line_angle
        
        # Normalize angles
        if delta1 > 180: delta1 -= 360
        elif delta1 < -180: delta1 += 360
        if delta2 > 180: delta2 -= 360
        elif delta2 < -180: delta2 += 360
        
        sin1 = math.sin(math.radians(delta1))
        sin2 = math.sin(math.radians(delta2))
        vertices_opposite = sin1 * sin2 < 0
        
        cot.append(f"→ Angle differences: {delta1:.1f}°, {delta2:.1f}°")
        cot.append(f"→ sin({delta1:.1f}°) × sin({delta2:.1f}°) = {sin1:.2f} × {sin2:.2f} = {sin1*sin2:.2f}")
        cot.append(f"→ Polygon vertices are on {'opposite' if vertices_opposite else 'same'} sides")
        
        # Test if line endpoints are on opposite sides of polygon edge
        cot.append(f"→ Call calculate_direction_angle tool with points {v1} and {A}")
        angle_v1a = calculate_direction_angle(v1, A)
        cot.append(f"→ Tool returns: {angle_v1a:.1f}°")
        
        cot.append(f"→ Call calculate_direction_angle tool with points {v1} and {B}")
        angle_v1b = calculate_direction_angle(v1, B)
        cot.append(f"→ Tool returns: {angle_v1b:.1f}°")
        
        delta3 = angle_v1a - edge_angle
        delta4 = angle_v1b - edge_angle
        
        # Normalize angles
        if delta3 > 180: delta3 -= 360
        elif delta3 < -180: delta3 += 360
        if delta4 > 180: delta4 -= 360
        elif delta4 < -180: delta4 += 360
        
        sin3 = math.sin(math.radians(delta3))
        sin4 = math.sin(math.radians(delta4))
        endpoints_opposite = sin3 * sin4 < 0
        
        cot.append(f"→ Angle differences: {delta3:.1f}°, {delta4:.1f}°")
        cot.append(f"→ sin({delta3:.1f}°) × sin({delta4:.1f}°) = {sin3:.2f} × {sin4:.2f} = {sin3*sin4:.2f}")
        cot.append(f"→ Line endpoints are on {'opposite' if endpoints_opposite else 'same'} sides")
        
        if vertices_opposite and endpoints_opposite:
            has_intersection = True
            cot.append(f"→ ✓ Intersection detected: Both tests passed")
            break
        else:
            cot.append(f"→ ✗ No intersection: At least one test failed")
    
    # CASE 2: Crosses relationship
    if has_intersection:
        cot.append("\nStep 3: Line segment intersects at least one polygon edge")
        cot.append("→ Spatial relation: 'Crosses'")
        return "\n".join(cot)
    
    # Step 3: Check if endpoints are on polygon boundary using distance tools
    cot.append("\nStep 3: Check if endpoints are on polygon boundary using distance tools")
    
    A_on_boundary = False
    B_on_boundary = False
    
    # Check if point A is on any polygon edge
    cot.append(f"\nChecking if point A{A} is on any polygon edge:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        
        cot.append(f"→ Call calculate_distance tool with points {v1} and {v2}")
        edge_length = calculate_distance(v1, v2)
        cot.append(f"→ Tool returns: {edge_length:.2f} (Edge length)")
        
        cot.append(f"→ Call calculate_distance tool with points {A} and {v1}")
        dist_a_v1 = calculate_distance(A, v1)
        cot.append(f"→ Tool returns: {dist_a_v1:.2f}")
        
        cot.append(f"→ Call calculate_distance tool with points {A} and {v2}")
        dist_a_v2 = calculate_distance(A, v2)
        cot.append(f"→ Tool returns: {dist_a_v2:.2f}")
        
        sum_distances = dist_a_v1 + dist_a_v2
        diff = abs(sum_distances - edge_length)
        
        cot.append(f"→ Check: {dist_a_v1:.2f} + {dist_a_v2:.2f} = {sum_distances:.2f} vs {edge_length:.2f}")
        cot.append(f"→ Difference: {diff:.2f}")
        
        if diff < 0.1:
            A_on_boundary = True
            cot.append(f"→ ✓ Point A is on edge {i+1}")
            break
        else:
            cot.append(f"→ ✗ Point A is not on edge {i+1}")
    
    # Check if point B is on any polygon edge
    cot.append(f"\nChecking if point B{B} is on any polygon edge:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        
        cot.append(f"→ Call calculate_distance tool with points {v1} and {v2}")
        edge_length = calculate_distance(v1, v2)
        cot.append(f"→ Tool returns: {edge_length:.2f} (Edge length)")
        
        cot.append(f"→ Call calculate_distance tool with points {B} and {v1}")
        dist_b_v1 = calculate_distance(B, v1)
        cot.append(f"→ Tool returns: {dist_b_v1:.2f}")
        
        cot.append(f"→ Call calculate_distance tool with points {B} and {v2}")
        dist_b_v2 = calculate_distance(B, v2)
        cot.append(f"→ Tool returns: {dist_b_v2:.2f}")
        
        sum_distances = dist_b_v1 + dist_b_v2
        diff = abs(sum_distances - edge_length)
        
        cot.append(f"→ Check: {dist_b_v1:.2f} + {dist_b_v2:.2f} = {sum_distances:.2f} vs {edge_length:.2f}")
        cot.append(f"→ Difference: {diff:.2f}")
        
        if diff < 0.1:
            B_on_boundary = True
            cot.append(f"→ ✓ Point B is on edge {i+1}")
            break
        else:
            cot.append(f"→ ✗ Point B is not on edge {i+1}")
    
    # CASE 3: Touches relationship
    if (A_on_boundary and not B_in_poly) or (B_on_boundary and not A_in_poly):
        cot.append("\nStep 4: Analysis shows one endpoint on boundary, other outside")
        if A_on_boundary:
            cot.append("→ Point A is on polygon boundary, Point B is outside")
        else:
            cot.append("→ Point B is on polygon boundary, Point A is outside")
        cot.append("→ Spatial relation: 'Touches'")
        return "\n".join(cot)
    
    # CASE 4: Default is Disjoint
    cot.append("\nStep 4: No significant relationship found")
    cot.append("→ Both endpoints are outside the polygon")
    cot.append("→ No endpoint is on the polygon boundary")
    cot.append("→ No intersection with polygon edges")
    cot.append("→ Spatial relation: 'Disjoint'")
    
    return "\n".join(cot)

# ———— Generate JSONL dataset ————
def generate_line_polygon_cot_dataset(n_each=100):
    gens = [generate_within, generate_touches, generate_disjoint, generate_crosses]
    dataset = []
    index = 0
    for gen in gens:
        for _ in range(n_each):
            line, poly, rel = gen()
            # Ensure coordinates are rounded
            rounded_line_coords = [tuple(round(c, 1) for c in point) for point in line.coords]
            rounded_poly_coords = [tuple(round(c, 1) for c in point) for point in poly.exterior.coords]
            
            inp = (f"Given line L with endpoints {rounded_line_coords} "
                   f"and polygon P with vertices {rounded_poly_coords[:-1]}, "
                   "determine their spatial relation.")
            out = generate_cot_reasoning(line, poly, rel)
            dataset.append({"input": inp, "output": out})
            
            # Visualize and save image
            visualize_relation(line, poly, rel, index)
            index += 1
    return dataset

# Save as JSONL
data = generate_line_polygon_cot_dataset(100)
output_file = os.path.join(os.path.dirname(__file__), 'line_polygon_cot_dataset.jsonl')
with open(output_file, "w") as f:
    for item in data:
        f.write(json.dumps(item) + "\n")

print(f"✅ Completed, generated {len(data)} CoT samples")
print(f"✅ Visualizations saved to '{vis_dir}' folder")
print(f"✅ Dataset saved to '{output_file}'")