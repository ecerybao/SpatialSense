import random
import json
from shapely.geometry import Point, Polygon

# 创建一个固定或随机多边形（正方形）
def generate_polygon():
    x0 = random.randint(-50, 50)
    y0 = random.randint(-50, 50)
    size = random.randint(5, 15)
    return Polygon([
        (x0, y0), (x0 + size, y0), (x0 + size, y0 + size),
        (x0, y0 + size), (x0, y0)  # 闭合多边形
    ])

def generate_within():
    poly = generate_polygon()
    minx, miny, maxx, maxy = poly.bounds
    while True:
        px = random.randint(int(minx + 1), int(maxx - 1))
        py = random.randint(int(miny + 1), int(maxy - 1))
        point = Point(px, py)
        if point.within(poly):
            return point, poly, "Within"

def generate_touches():
    poly = generate_polygon()
    minx, miny, maxx, maxy = poly.bounds
    
    while True:
        # 随机决定是生成边界点还是与边界相交的点
        if random.random() < 0.5:
            # 生成边界点
            boundary_coords = list(poly.exterior.coords)
            pt = random.choice(boundary_coords)
            point = Point(int(pt[0]), int(pt[1]))
        else:
            # 生成与边界相交的点
            # 随机选择一条边
            boundary_coords = list(poly.exterior.coords)
            i = random.randint(0, len(boundary_coords)-2)
            x1, y1 = boundary_coords[i]
            x2, y2 = boundary_coords[i+1]
            
            # 在边的附近生成点
            t = random.uniform(0.1, 0.9)  # 避免端点
            px = int(x1 + t * (x2 - x1))
            py = int(y1 + t * (y2 - y1))
            point = Point(px, py)
        
        # 验证点是否真的与多边形接触
        if point.touches(poly):
            return point, poly, "Touches"

def generate_disjoint():
    poly = generate_polygon()
    minx, miny, maxx, maxy = poly.bounds
    offset = random.randint(10, 20)
    px = int(maxx + offset)
    py = int(maxy + offset)
    point = Point(px, py)
    return point, poly, "Disjoint"

def to_dict(point, poly, relation):
    return {
        "entity1": {"type": "point", "coordinates": [int(point.x), int(point.y)]},
        "entity2": {"type": "polygon", "coordinates": [[int(x), int(y)] for x, y in poly.exterior.coords]},
        "spatial_relation": relation
    }

def generate_dataset(n_each=30):
    dataset = []
    for _ in range(n_each):
        dataset.append(to_dict(*generate_within()))
        dataset.append(to_dict(*generate_touches()))
        dataset.append(to_dict(*generate_disjoint()))
    return dataset

# 生成数据集并保存
dataset = generate_dataset(n_each=50)

with open("point_polygon_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"✅ 数据集生成完毕，共 {len(dataset)} 条记录")