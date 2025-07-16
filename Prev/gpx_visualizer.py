import gpxpy
import folium
from folium.plugins import HeatMap
import os

def parse_gpx(gpx_file_path):
    """
    解析GPX文件并提取轨迹点
    """
    with open(gpx_file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append([point.latitude, point.longitude])
    
    return points

def create_map(points, output_file='trajectory_map.html'):
    """
    创建交互式地图并保存
    """
    # 使用第一个点作为地图中心
    if points:
        center = points[0]
    else:
        center = [0, 0]  # 默认中心点
    
    # 创建地图
    m = folium.Map(location=center, zoom_start=13)
    
    # 添加轨迹线
    folium.PolyLine(points, color='blue', weight=2.5, opacity=1).add_to(m)
    
    # 添加热力图
    HeatMap(points).add_to(m)
    
    # 保存地图
    m.save(output_file)
    print(f"地图已保存为: {output_file}")

def main():
    # 获取当前目录下的GPX文件
    gpx_files = [f for f in os.listdir('.') if f.endswith('.gpx')]
    
    if not gpx_files:
        print("当前目录下没有找到GPX文件！")
        return
    
    # 处理每个GPX文件
    for gpx_file in gpx_files:
        print(f"正在处理文件: {gpx_file}")
        points = parse_gpx(gpx_file)
        output_file = f"{os.path.splitext(gpx_file)[0]}_map.html"
        create_map(points, output_file)

if __name__ == "__main__":
    main() 