import random
import json
from shapely.geometry import Point, LineString

def generate_touches():
    x1 = random.randint(-50, 50)
    y1 = random.randint(-50, 50)
    x2 = random.randint(-50, 50)
    y2 = random.randint(-50, 50)
    line = LineString([(x1, y1), (x2, y2)])
    point = Point((x1, y1))  # 选择线段起点
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
        px = int(x1 + t * dx)
        py = int(y1 + t * dy)
        point = Point((px, py))
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
        py = random.randint(20, 50)  # 明显远离线段
        point = Point((px, py))
        if point.disjoint(line):
            return point, line, "Disjoint"

def to_dict(point, line, relation):
    return {
        "entity1": {"type": "point", "coordinates": [point.x, point.y]},
        "entity2": {"type": "line", "coordinates": list(line.coords)},
        "spatial_relation": relation
    }

def generate_dataset(n_each=100):
    dataset = []
    for _ in range(n_each):
        dataset.append(to_dict(*generate_touches()))
        dataset.append(to_dict(*generate_within()))
        dataset.append(to_dict(*generate_disjoint()))
    return dataset

# 生成并保存数据集
dataset = generate_dataset(n_each=50)

with open("point_line_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"✅ 数据集生成完毕，共 {len(dataset)} 条记录")