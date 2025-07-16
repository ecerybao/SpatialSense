import pandas as pd
import folium
from folium import plugins

def visualize_trajectory(csv_file, start_row=0, end_row=None, sample_size=None):
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 选择数据
    if sample_size:
        # 随机采样
        df = df.sample(n=sample_size, random_state=42)
    else:
        # 按照行范围选择
        df = df.iloc[start_row:end_row]
    
    # 获取轨迹的中心点作为地图的初始中心
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # 创建地图对象
    trajectory_map = folium.Map(location=[center_lat, center_lon], 
                              zoom_start=12)
    
    # 创建轨迹线
    coordinates = [[row['latitude'], row['longitude']] 
                  for idx, row in df.iterrows()]
    
    # 添加轨迹线到地图
    folium.PolyLine(
        coordinates,
        weight=2,
        color='red',
        opacity=0.8
    ).add_to(trajectory_map)
    
    # 添加起点标记（绿色）
    folium.Marker(
        coordinates[0],
        popup='Start',
        icon=folium.Icon(color='green')
    ).add_to(trajectory_map)
    
    # 添加终点标记（红色）
    folium.Marker(
        coordinates[-1],
        popup='End',
        icon=folium.Icon(color='red')
    ).add_to(trajectory_map)
    
    # 保存地图为HTML文件
    trajectory_map.save('trajectory_visualization.html')

if __name__ == "__main__":
    csv_file = "/Users/bob/Downloads/SpatialSense/datasets/nyc/raw/NYC_test.csv"
    
    # 方式3：选择中间一段
    visualize_trajectory(csv_file, start_row=0, end_row=10)
