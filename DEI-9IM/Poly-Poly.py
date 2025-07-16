import random
import json
from shapely.geometry import Polygon

# 创建矩形多边形
def create_rectangle(x0, y0, w, h):
    return Polygon([
        (x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)
    ])

def generate_random_polygon(min_size=5, max_size=20):
    # 随机生成矩形的位置和大小
    x0 = random.uniform(-50, 50)
    y0 = random.uniform(-50, 50)
    w = random.uniform(min_size, max_size)
    h = random.uniform(min_size, max_size)
    return create_rectangle(x0, y0, w, h)

def generate_equals():
    # 生成一个随机多边形，然后复制它
    poly = generate_random_polygon()
    return poly, Polygon(poly.exterior.coords), "Equals"

def generate_disjoint():
    while True:
        poly1 = generate_random_polygon()
        minx, miny, maxx, maxy = poly1.bounds
        
        # 在多边形外部随机位置生成第二个多边形
        offset = random.uniform(10, 20)
        position = random.choice(['top', 'bottom', 'left', 'right', 'top_left', 'top_right', 'bottom_left', 'bottom_right'])
        
        if position == 'top':
            x0 = random.uniform(minx - 5, maxx + 5)
            y0 = maxy + offset
        elif position == 'bottom':
            x0 = random.uniform(minx - 5, maxx + 5)
            y0 = miny - offset - random.uniform(5, 10)
        elif position == 'left':
            x0 = minx - offset - random.uniform(5, 10)
            y0 = random.uniform(miny - 5, maxy + 5)
        elif position == 'right':
            x0 = maxx + offset
            y0 = random.uniform(miny - 5, maxy + 5)
        elif position == 'top_left':
            x0 = minx - offset - random.uniform(5, 10)
            y0 = maxy + offset
        elif position == 'top_right':
            x0 = maxx + offset
            y0 = maxy + offset
        elif position == 'bottom_left':
            x0 = minx - offset - random.uniform(5, 10)
            y0 = miny - offset - random.uniform(5, 10)
        else:  # bottom_right
            x0 = maxx + offset
            y0 = miny - offset - random.uniform(5, 10)
        
        w = random.uniform(5, 15)
        h = random.uniform(5, 15)
        poly2 = create_rectangle(x0, y0, w, h)
        
        if poly1.disjoint(poly2):
            return poly1, poly2, "Disjoint"

def generate_touches():
    while True:
        poly1 = generate_random_polygon()
        minx, miny, maxx, maxy = poly1.bounds
        
        # 随机选择接触的边
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x0 = random.uniform(minx, maxx - 5)  # 确保有足够的空间放置第二个多边形
            y0 = maxy
            w = random.uniform(5, min(maxx - x0, 10))  # 宽度不超过剩余空间
        elif side == 'bottom':
            x0 = random.uniform(minx, maxx - 5)
            y0 = miny - random.uniform(5, 10)
            w = random.uniform(5, min(maxx - x0, 10))
        elif side == 'left':
            x0 = minx - random.uniform(5, 10)
            y0 = random.uniform(miny, maxy - 5)
            h = random.uniform(5, min(maxy - y0, 10))
            w = random.uniform(5, 10)
            poly2 = create_rectangle(x0, y0, w, h)
            if poly1.touches(poly2):
                return poly1, poly2, "Touches"
            continue
        else:  # right
            x0 = maxx
            y0 = random.uniform(miny, maxy - 5)
            w = random.uniform(5, 10)
        
        h = random.uniform(5, 10)
        poly2 = create_rectangle(x0, y0, w, h)
        
        if poly1.touches(poly2):
            return poly1, poly2, "Touches"

def generate_overlaps():
    while True:
        poly1 = generate_random_polygon()
        minx, miny, maxx, maxy = poly1.bounds
        
        # 在第一个多边形内部随机选择一个点作为第二个多边形的起点
        x0 = random.uniform(minx + 2, maxx - 2)
        y0 = random.uniform(miny + 2, maxy - 2)
        
        # 随机生成第二个多边形的大小
        w = random.uniform(5, min(maxx - x0 + 5, 15))
        h = random.uniform(5, min(maxy - y0 + 5, 15))
        
        poly2 = create_rectangle(x0, y0, w, h)
        
        if poly1.overlaps(poly2):
            return poly1, poly2, "Overlaps"

def generate_contains():
    while True:
        # 生成一个较大的多边形
        outer = generate_random_polygon(min_size=15, max_size=25)
        minx, miny, maxx, maxy = outer.bounds
        
        # 在内部生成一个较小的多边形
        margin = 5  # 确保内部多边形不会太靠近边界
        x0 = random.uniform(minx + margin, maxx - margin - 5)
        y0 = random.uniform(miny + margin, maxy - margin - 5)
        w = random.uniform(5, min(maxx - x0 - margin, 10))
        h = random.uniform(5, min(maxy - y0 - margin, 10))
        
        inner = create_rectangle(x0, y0, w, h)
        
        if outer.contains(inner):
            return outer, inner, "Contains"

def generate_within():
    # 反向的contains关系
    outer, inner, _ = generate_contains()
    return inner, outer, "Within"

def to_dict(poly1, poly2, relation):
    return {
        "entity1": {"type": "polygon", "coordinates": list(poly1.exterior.coords)},
        "entity2": {"type": "polygon", "coordinates": list(poly2.exterior.coords)},
        "spatial_relation": relation
    }

def generate_dataset(n_each=50):
    dataset = []
    for _ in range(n_each):
        dataset.append(to_dict(*generate_equals()))
        dataset.append(to_dict(*generate_disjoint()))
        dataset.append(to_dict(*generate_touches()))
        dataset.append(to_dict(*generate_overlaps()))
        dataset.append(to_dict(*generate_contains()))
        dataset.append(to_dict(*generate_within()))
    return dataset

# 生成并保存数据集
dataset = generate_dataset(n_each=50)

with open("polygon_polygon_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"✅ 数据集生成完毕，共 {len(dataset)} 条记录")