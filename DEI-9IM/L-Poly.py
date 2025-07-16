import random
import json
from shapely.geometry import LineString, Polygon, Point

# 固定创建一个矩形多边形
def generate_polygon():
    x0, y0 = random.uniform(-50, 0), random.uniform(-50, 0)
    size = random.uniform(10, 20)
    return Polygon([
        (x0, y0), (x0 + size, y0),
        (x0 + size, y0 + size), (x0, y0 + size),
        (x0, y0)
    ])

def generate_within():
    poly = generate_polygon()
    minx, miny, maxx, maxy = poly.bounds
    # 保证线段完全在内部
    while True:
        x1 = random.uniform(minx + 1, maxx - 1)
        y1 = random.uniform(miny + 1, maxy - 1)
        x2 = random.uniform(minx + 1, maxx - 1)
        y2 = random.uniform(miny + 1, maxy - 1)
        line = LineString([(x1, y1), (x2, y2)])
        if line.within(poly):
            return line, poly, "Within"

def generate_touches():
    while True:
        poly = generate_polygon()
        minx, miny, maxx, maxy = poly.bounds
        
        # 随机选择一条边
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            # 在上边界上随机选择一个点
            touch_x = random.uniform(minx, maxx)
            touch_y = maxy
            # 向上延伸
            line_x = touch_x
            line_y = touch_y + random.uniform(1, 5)
        elif side == 'bottom':
            touch_x = random.uniform(minx, maxx)
            touch_y = miny
            line_x = touch_x
            line_y = touch_y - random.uniform(1, 5)
        elif side == 'left':
            touch_x = minx
            touch_y = random.uniform(miny, maxy)
            line_x = touch_x - random.uniform(1, 5)
            line_y = touch_y
        else:  # right
            touch_x = maxx
            touch_y = random.uniform(miny, maxy)
            line_x = touch_x + random.uniform(1, 5)
            line_y = touch_y
        
        line = LineString([(touch_x, touch_y), (line_x, line_y)])
        
        # 验证是否满足touches关系
        if line.touches(poly) and not line.crosses(poly):
            return line, poly, "Touches"

def generate_disjoint():
    poly = generate_polygon()
    minx, miny, maxx, maxy = poly.bounds
    
    # 随机选择位置：上、下、左、右、左上、右上、左下、右下
    position = random.choice(['top', 'bottom', 'left', 'right', 'top_left', 'top_right', 'bottom_left', 'bottom_right'])
    offset = random.uniform(10, 20)
    
    # 随机线段长度
    length = random.uniform(5, 30)
    # 随机角度
    angle = random.uniform(0, 360)
    
    if position == 'top':
        x1 = random.uniform(minx - 5, maxx + 5)
        y1 = maxy + offset
        x2 = x1 + length * random.uniform(-1, 1)
        y2 = y1 + length * random.uniform(0.5, 1)
    elif position == 'bottom':
        x1 = random.uniform(minx - 5, maxx + 5)
        y1 = miny - offset
        x2 = x1 + length * random.uniform(-1, 1)
        y2 = y1 - length * random.uniform(0.5, 1)
    elif position == 'left':
        x1 = minx - offset
        y1 = random.uniform(miny - 5, maxy + 5)
        x2 = x1 - length * random.uniform(0.5, 1)
        y2 = y1 + length * random.uniform(-1, 1)
    elif position == 'right':
        x1 = maxx + offset
        y1 = random.uniform(miny - 5, maxy + 5)
        x2 = x1 + length * random.uniform(0.5, 1)
        y2 = y1 + length * random.uniform(-1, 1)
    elif position == 'top_left':
        x1 = minx - offset
        y1 = maxy + offset
        x2 = x1 - length * random.uniform(0.5, 1)
        y2 = y1 + length * random.uniform(0.5, 1)
    elif position == 'top_right':
        x1 = maxx + offset
        y1 = maxy + offset
        x2 = x1 + length * random.uniform(0.5, 1)
        y2 = y1 + length * random.uniform(0.5, 1)
    elif position == 'bottom_left':
        x1 = minx - offset
        y1 = miny - offset
        x2 = x1 - length * random.uniform(0.5, 1)
        y2 = y1 - length * random.uniform(0.5, 1)
    else:  # bottom_right
        x1 = maxx + offset
        y1 = miny - offset
        x2 = x1 + length * random.uniform(0.5, 1)
        y2 = y1 - length * random.uniform(0.5, 1)
    
    line = LineString([(x1, y1), (x2, y2)])
    return line, poly, "Disjoint"

def generate_crosses():
    while True:
        poly = generate_polygon()
        minx, miny, maxx, maxy = poly.bounds
        
        # 随机选择穿过的方向：水平、垂直、对角线
        direction = random.choice(['horizontal', 'vertical', 'diagonal'])
        
        # 随机线段长度（确保足够长以穿过多边形）
        min_length = max(maxx - minx, maxy - miny) * 1.5
        max_length = min_length * 2
        length = random.uniform(min_length, max_length)
        
        if direction == 'horizontal':
            # 水平穿过
            y = random.uniform(miny, maxy)
            # 确保线段足够长以穿过多边形
            x1 = minx - length * random.uniform(0.3, 0.5)
            x2 = maxx + length * random.uniform(0.3, 0.5)
            line = LineString([(x1, y), (x2, y)])
        elif direction == 'vertical':
            # 垂直穿过
            x = random.uniform(minx, maxx)
            # 确保线段足够长以穿过多边形
            y1 = miny - length * random.uniform(0.3, 0.5)
            y2 = maxy + length * random.uniform(0.3, 0.5)
            line = LineString([(x, y1), (x, y2)])
        else:  # diagonal
            # 对角线穿过
            angle = random.uniform(0, 360)
            # 计算起点和终点，确保线段足够长
            if angle < 45 or angle >= 315:
                x1 = minx - length * random.uniform(0.3, 0.5)
                y1 = miny - length * random.uniform(0.3, 0.5)
                x2 = maxx + length * random.uniform(0.3, 0.5)
                y2 = maxy + length * random.uniform(0.3, 0.5)
            elif angle < 135:
                x1 = maxx + length * random.uniform(0.3, 0.5)
                y1 = miny - length * random.uniform(0.3, 0.5)
                x2 = minx - length * random.uniform(0.3, 0.5)
                y2 = maxy + length * random.uniform(0.3, 0.5)
            elif angle < 225:
                x1 = maxx + length * random.uniform(0.3, 0.5)
                y1 = maxy + length * random.uniform(0.3, 0.5)
                x2 = minx - length * random.uniform(0.3, 0.5)
                y2 = miny - length * random.uniform(0.3, 0.5)
            else:
                x1 = minx - length * random.uniform(0.3, 0.5)
                y1 = maxy + length * random.uniform(0.3, 0.5)
                x2 = maxx + length * random.uniform(0.3, 0.5)
                y2 = miny - length * random.uniform(0.3, 0.5)
            line = LineString([(x1, y1), (x2, y2)])
        
        # 验证是否真的穿过多边形
        if line.crosses(poly):
            return line, poly, "Crosses"

def to_dict(line, poly, relation):
    return {
        "entity1": {"type": "line", "coordinates": list(line.coords)},
        "entity2": {"type": "polygon", "coordinates": list(poly.exterior.coords)},
        "spatial_relation": relation
    }

def generate_dataset(n_each=100):
    dataset = []
    for _ in range(n_each):
        dataset.append(to_dict(*generate_within()))
        dataset.append(to_dict(*generate_touches()))
        dataset.append(to_dict(*generate_disjoint()))
        dataset.append(to_dict(*generate_crosses()))
    return dataset

# 保存为 JSON 文件
dataset = generate_dataset(n_each=100)

with open("line_polygon_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"✅ 数据集生成完毕，共 {len(dataset)} 条记录")