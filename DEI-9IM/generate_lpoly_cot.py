import random
import json
import math
import os
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Polygon, Point


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
def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return round(math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2), 1)

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

# ———— Chain-of-Thought reasoning template ————
def generate_cot_reasoning(line, poly, relation):
    coords = list(line.coords)
    A, B = [tuple(round(c, 1) for c in point) for point in coords]
    polygon_vertices = list(poly.exterior.coords)
    polygon_vertices = [tuple(round(c, 1) for c in vertex) for vertex in polygon_vertices]
    
    cot = []
    cot.append(f"Line L endpoints: A{A}, B{B}.")
    cot.append(f"Polygon P vertices: {polygon_vertices[:-1]}.")
    
    cot.append("\nStep 1: Determine if the line endpoints are inside the polygon")
    cot.append("  Using angle sum method: For a point inside a polygon, the sum of angles formed with consecutive vertices equals 2π")
    
    # Analyze point A
    A_in_poly = check_point_in_polygon(A, polygon_vertices)
    angles_A = []
    
    cot.append(f"  Checking if point A{A} is inside the polygon:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        angle = calculate_angle(A, v1) - calculate_angle(A, v2)
        while angle > math.pi: angle -= 2*math.pi
        while angle < -math.pi: angle += 2*math.pi
        angles_A.append(round(angle, 1))
        cot.append(f"    Edge {i+1}: {v1}-{v2}, angle: {round(angle, 1)} radians")
    
    angle_sum_A = abs(sum(angles_A))
    cot.append(f"    Total angle sum: {round(angle_sum_A, 1)} radians")
    cot.append(f"    Difference from 2π ({round(2*math.pi, 1)}): {round(abs(angle_sum_A - 2*math.pi), 1)}")
    cot.append(f"    Point A is inside polygon: {A_in_poly}")
    
    # Analyze point B
    B_in_poly = check_point_in_polygon(B, polygon_vertices)
    angles_B = []
    
    cot.append(f"  Checking if point B{B} is inside the polygon:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        angle = calculate_angle(B, v1) - calculate_angle(B, v2)
        while angle > math.pi: angle -= 2*math.pi
        while angle < -math.pi: angle += 2*math.pi
        angles_B.append(round(angle, 1))
    
    angle_sum_B = abs(sum(angles_B))
    cot.append(f"    Total angle sum: {round(angle_sum_B, 1)} radians")
    cot.append(f"    Difference from 2π ({round(2*math.pi, 1)}): {round(abs(angle_sum_B - 2*math.pi), 1)}")
    cot.append(f"    Point B is inside polygon: {B_in_poly}")
    
    # CASE 1: Within relationship - both endpoints inside polygon
    if A_in_poly and B_in_poly:
        cot.append("\nRelationship Analysis: Both endpoints A and B are inside the polygon → Relation = 'Within'")
        return "\n".join(cot)
    
    # Step 2: Check for crosses relationship
    cot.append("\nStep 2: Check if the line segment crosses any polygon edge")
    cot.append("  Using the angle method to detect line intersections:")
    cot.append("  Two line segments AB and CD intersect if both:")
    cot.append("    • Points C and D are on opposite sides of line AB")
    cot.append("    • Points A and B are on opposite sides of line CD")
    
    has_intersection = False
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        
        cot.append(f"\n  Testing intersection with edge {i+1}: {v1}-{v2}")
        
        # Calculate line direction angles
        theta_AB = calculate_angle(A, B)
        theta_v1v2 = calculate_angle(v1, v2)
        cot.append(f"    Line AB direction angle: {round(theta_AB, 1)} radians")
        cot.append(f"    Edge direction angle: {round(theta_v1v2, 1)} radians")
        
        # Test 1: Are polygon vertices on opposite sides of line AB?
        theta_Av1 = calculate_angle(A, v1)
        theta_Av2 = calculate_angle(A, v2)
        delta1 = round(theta_Av1 - theta_AB, 1)
        delta2 = round(theta_Av2 - theta_AB, 1)
        
        # Normalize angles
        while delta1 > math.pi: delta1 -= 2*math.pi
        while delta1 < -math.pi: delta1 += 2*math.pi
        while delta2 > math.pi: delta2 -= 2*math.pi
        while delta2 < -math.pi: delta2 += 2*math.pi
        
        sin1 = round(math.sin(delta1), 1)
        sin2 = round(math.sin(delta2), 1)
        sin_product1 = round(sin1*sin2, 1)
        vertices_opposite_sides = sin_product1 < 0
        
        cot.append(f"    Test 1: Are polygon vertices on opposite sides of line AB?")
        cot.append(f"      Angle A→v1: {round(theta_Av1, 1)}, difference: {delta1}, sin: {sin1}")
        cot.append(f"      Angle A→v2: {round(theta_Av2, 1)}, difference: {delta2}, sin: {sin2}")
        cot.append(f"      sin(diff1) × sin(diff2) = {sin1} × {sin2} = {sin_product1}")
        cot.append(f"      Result: {'Points are on OPPOSITE sides' if vertices_opposite_sides else 'Points are on SAME side'}")
        
        # Test 2: Are line endpoints on opposite sides of polygon edge?
        theta_v1A = calculate_angle(v1, A)
        theta_v1B = calculate_angle(v1, B)
        delta3 = round(theta_v1A - theta_v1v2, 1)
        delta4 = round(theta_v1B - theta_v1v2, 1)
        
        # Normalize angles
        while delta3 > math.pi: delta3 -= 2*math.pi
        while delta3 < -math.pi: delta3 += 2*math.pi
        while delta4 > math.pi: delta4 -= 2*math.pi
        while delta4 < -math.pi: delta4 += 2*math.pi
        
        sin3 = round(math.sin(delta3), 1)
        sin4 = round(math.sin(delta4), 1)
        sin_product2 = round(sin3*sin4, 1)
        endpoints_opposite_sides = sin_product2 < 0
        
        cot.append(f"    Test 2: Are line endpoints on opposite sides of polygon edge?")
        cot.append(f"      Angle v1→A: {round(theta_v1A, 1)}, difference: {delta3}, sin: {sin3}")
        cot.append(f"      Angle v1→B: {round(theta_v1B, 1)}, difference: {delta4}, sin: {sin4}")
        cot.append(f"      sin(diff3) × sin(diff4) = {sin3} × {sin4} = {sin_product2}")
        cot.append(f"      Result: {'Points are on OPPOSITE sides' if endpoints_opposite_sides else 'Points are on SAME side'}")
        
        # Check if both tests indicate intersection
        if vertices_opposite_sides and endpoints_opposite_sides:
            has_intersection = True
            cot.append(f"    ✓ Intersection detected: Both tests passed")
            
            # Calculate intersection point for visualization
            x1, y1 = A
            x2, y2 = B
            x3, y3 = v1
            x4, y4 = v2
            
            dx1 = x2 - x1
            dy1 = y2 - y1
            dx2 = x4 - x3
            dy2 = y4 - y3
            
            D = dx1 * dy2 - dy1 * dx2
            if abs(D) > 0.0001:
                t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / D
                intersection_x = round(x1 + t * dx1, 1)
                intersection_y = round(y1 + t * dy1, 1)
                intersection_point = (intersection_x, intersection_y)
                cot.append(f"    Intersection point: {intersection_point}")
            
            break
        else:
            cot.append(f"    ✗ No intersection: At least one test failed")
    
    # CASE 2: Crosses relationship - has intersection with polygon edge
    if has_intersection:
        cot.append("\nRelationship Analysis: Line segment crosses at least one polygon edge → Relation = 'Crosses'")
        return "\n".join(cot)
    
    # Step 3: Check for touches relationship
    cot.append("\nStep 3: Check if one endpoint is on the polygon boundary")
    cot.append("  Using distance method: A point P is on line segment AB if |PA| + |PB| = |AB|")
    
    A_on_boundary = False
    B_on_boundary = False
    edge_with_A = None
    edge_with_B = None
    
    # Check if point A is on any polygon edge
    cot.append(f"  Testing if point A{A} is on any polygon edge:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        edge_length = calculate_distance(v1, v2)
        dist_A_v1 = calculate_distance(A, v1)
        dist_A_v2 = calculate_distance(A, v2)
        sum_of_distances = round(dist_A_v1 + dist_A_v2, 1)
        diff_A = abs(sum_of_distances - edge_length)
        
        cot.append(f"    Edge {i+1}: {v1}-{v2}")
        cot.append(f"      |v1-v2| = {edge_length}, |A-v1| = {dist_A_v1}, |A-v2| = {dist_A_v2}")
        cot.append(f"      |A-v1| + |A-v2| = {sum_of_distances}, Difference: {round(diff_A, 1)}")
        
        if diff_A < 0.1:
            A_on_boundary = True
            edge_with_A = (v1, v2)
            cot.append(f"      ✓ Point A is on this edge! (difference < 0.1)")
            break
        else:
            cot.append(f"      ✗ Point A is not on this edge")
    
    # Check if point B is on any polygon edge
    cot.append(f"  Testing if point B{B} is on any polygon edge:")
    for i in range(len(polygon_vertices)-1):
        v1, v2 = polygon_vertices[i], polygon_vertices[i+1]
        edge_length = calculate_distance(v1, v2)
        dist_B_v1 = calculate_distance(B, v1)
        dist_B_v2 = calculate_distance(B, v2)
        sum_of_distances = round(dist_B_v1 + dist_B_v2, 1)
        diff_B = abs(sum_of_distances - edge_length)
        
        cot.append(f"    Edge {i+1}: {v1}-{v2}")
        cot.append(f"      |v1-v2| = {edge_length}, |B-v1| = {dist_B_v1}, |B-v2| = {dist_B_v2}")
        cot.append(f"      |B-v1| + |B-v2| = {sum_of_distances}, Difference: {round(diff_B, 1)}")
        
        if diff_B < 0.1:
            B_on_boundary = True
            edge_with_B = (v1, v2)
            cot.append(f"      ✓ Point B is on this edge! (difference < 0.1)")
            break
        else:
            cot.append(f"      ✗ Point B is not on this edge")
    
    # CASE 3: Touches relationship - one point on boundary, other outside
    if (A_on_boundary and not B_in_poly) or (B_on_boundary and not A_in_poly):
        cot.append("\nRelationship Analysis: ")
        if A_on_boundary:
            cot.append(f"  • Point A is on polygon boundary (on edge {edge_with_A})")
            cot.append(f"  • Point B is outside the polygon")
        else:
            cot.append(f"  • Point B is on polygon boundary (on edge {edge_with_B})")
            cot.append(f"  • Point A is outside the polygon")
        cot.append("  → Relation = 'Touches'")
        return "\n".join(cot)
    
    # CASE 4: Default is Disjoint
    cot.append("\nRelationship Analysis: ")
    cot.append("  • Both endpoints are outside the polygon")
    cot.append("  • No endpoint is on the polygon boundary")
    cot.append("  • No intersection with polygon edges")
    cot.append("  → Relation = 'Disjoint'")
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