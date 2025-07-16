import random
import json

def generate_point_equals():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return ([x, y], [x, y], "Equals")

def generate_point_disjoint():
    x1 = random.randint(-100, 100)
    y1 = random.randint(-100, 100)
    while True:
        x2 = random.randint(-100, 100)
        y2 = random.randint(-100, 100)
        if x1 != x2 or y1 != y2:
            break
    return ([x1, y1], [x2, y2], "Disjoint")

def generate_point_point_dataset(n_equals=50, n_disjoint=50):
    dataset = []

    for _ in range(n_equals):
        p1, p2, relation = generate_point_equals()
        dataset.append({
            "entity1": {"type": "point", "coordinates": p1},
            "entity2": {"type": "point", "coordinates": p2},
            "spatial_relation": relation
        })

    for _ in range(n_disjoint):
        p1, p2, relation = generate_point_disjoint()
        dataset.append({
            "entity1": {"type": "point", "coordinates": p1},
            "entity2": {"type": "point", "coordinates": p2},
            "spatial_relation": relation
        })

    return dataset

# 生成数据并保存为 JSON 文件
dataset = generate_point_point_dataset(n_equals=50, n_disjoint=50)

with open("point_point_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print("✅ 数据集生成完毕，共 {} 条记录".format(len(dataset)))