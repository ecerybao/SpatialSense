import random
import json
from shapely.geometry import LineString

def generate_random_line(min_x=-50, max_x=50, min_y=-50, max_y=50):
    x1 = random.uniform(min_x, max_x)
    y1 = random.uniform(min_y, max_y)
    x2 = random.uniform(min_x, max_x)
    y2 = random.uniform(min_y, max_y)
    return LineString([(x1, y1), (x2, y2)])

def generate_equals():
    line = generate_random_line()
    return line, LineString(line.coords), "Equals"

def generate_contains():
    # 首先生成一条随机线段
    x1 = random.uniform(-50, 50)
    y1 = random.uniform(-50, 50)
    x2 = random.uniform(-50, 50)
    y2 = random.uniform(-50, 50)
    full = LineString([(x1, y1), (x2, y2)])
    
    # 在完整线段内部生成一个较短的线段，保持相同斜率
    t1 = random.uniform(0.2, 0.4)  # 第一个点在20%-40%处
    t2 = random.uniform(0.6, 0.8)  # 第二个点在60%-80%处
    
    # 计算内部线段的端点，保持精确的斜率
    part_x1 = x1 + t1 * (x2 - x1)
    part_y1 = y1 + t1 * (y2 - y1)
    part_x2 = x1 + t2 * (x2 - x1)
    part_y2 = y1 + t2 * (y2 - y1)
    
    part = LineString([(part_x1, part_y1), (part_x2, part_y2)])
    return full, part, "Contains"

def generate_within():
    # 反向的contains关系
    full, part, _ = generate_contains()
    return part, full, "Within"

def generate_overlaps():
    # 首先生成一条随机线段
    x1 = random.uniform(-50, 50)
    y1 = random.uniform(-50, 50)
    x2 = random.uniform(-50, 50)
    y2 = random.uniform(-50, 50)
    line1 = LineString([(x1, y1), (x2, y2)])
    
    # 生成一个与line1部分重叠的线段，保持相同斜率
    t1 = random.uniform(0.3, 0.7)  # 重叠起点在30%-70%处
    t2 = random.uniform(0.8, 1.2)  # 重叠终点在80%-120%处
    
    # 计算重叠线段的两个端点，保持精确的斜率
    overlap_x1 = x1 + t1 * (x2 - x1)
    overlap_y1 = y1 + t1 * (y2 - y1)
    overlap_x2 = x1 + t2 * (x2 - x1)
    overlap_y2 = y1 + t2 * (y2 - y1)
    
    line2 = LineString([(overlap_x1, overlap_y1), (overlap_x2, overlap_y2)])
    return line1, line2, "Overlaps"

def generate_crosses():
    # 首先生成一条随机线段
    x1 = random.uniform(-50, 50)
    y1 = random.uniform(-50, 50)
    x2 = random.uniform(-50, 50)
    y2 = random.uniform(-50, 50)
    line1 = LineString([(x1, y1), (x2, y2)])
    
    # 计算中点
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    # 生成一个与line1相交的线段
    # 计算垂直方向
    dx = x2 - x1
    dy = y2 - y1
    length = random.uniform(5, 15)
    # 旋转90度
    line2 = LineString([
        (mid_x - dy * length, mid_y + dx * length),
        (mid_x + dy * length, mid_y - dx * length)
    ])
    return line1, line2, "Crosses"

def generate_touches():
    while True:
        # 首先生成一条随机线段
        x1 = random.uniform(-50, 50)
        y1 = random.uniform(-50, 50)
        x2 = random.uniform(-50, 50)
        y2 = random.uniform(-50, 50)
        line1 = LineString([(x1, y1), (x2, y2)])
        
        # 随机决定是使用端点还是中间点
        if random.random() < 0.5:
            # 使用端点
            if random.random() < 0.5:
                touch_point = (x1, y1)  # 使用起点
            else:
                touch_point = (x2, y2)  # 使用终点
        else:
            # 使用中间点
            t = random.uniform(0.1, 0.9)  # 避免太靠近端点
            touch_point = (
                x1 + t * (x2 - x1),
                y1 + t * (y2 - y1)
            )
        
        # 从接触点向随机方向延伸生成第二条线段
        angle = random.uniform(0, 2 * 3.14159)  # 随机角度
        length = random.uniform(5, 15)  # 随机长度
        dx = length * random.uniform(-1, 1)
        dy = length * random.uniform(-1, 1)
        
        line2 = LineString([
            touch_point,
            (touch_point[0] + dx, touch_point[1] + dy)
        ])
        
        # 验证是否满足touches关系
        if line1.touches(line2):
            return line1, line2, "Touches"

def generate_disjoint():
    # 首先生成一条随机线段
    x1 = random.uniform(-50, 50)
    y1 = random.uniform(-50, 50)
    x2 = random.uniform(-50, 50)
    y2 = random.uniform(-50, 50)
    line1 = LineString([(x1, y1), (x2, y2)])
    
    # 生成一个远离line1的线段
    offset = random.uniform(20, 30)
    line2 = LineString([
        (x1 + offset, y1 + offset),
        (x2 + offset, y2 + offset)
    ])
    return line1, line2, "Disjoint"

def to_dict(line1, line2, relation):
    # 所有关系都使用浮点数坐标以保持精度
    return {
        "entity1": {"type": "line", "coordinates": [[x, y] for x, y in line1.coords]},
        "entity2": {"type": "line", "coordinates": [[x, y] for x, y in line2.coords]},
        "spatial_relation": relation
    }

def generate_dataset(n_each=5):
    dataset = []
    for _ in range(n_each):
        dataset.append(to_dict(*generate_equals()))
        dataset.append(to_dict(*generate_contains()))
        dataset.append(to_dict(*generate_within()))
        dataset.append(to_dict(*generate_overlaps()))
        dataset.append(to_dict(*generate_crosses()))
        dataset.append(to_dict(*generate_touches()))
        dataset.append(to_dict(*generate_disjoint()))
    return dataset

# 保存数据集
dataset = generate_dataset(n_each=50)

with open("line_line_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"✅ 数据集生成完毕，共 {len(dataset)} 条记录")