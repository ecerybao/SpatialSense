import pandas as pd
import os
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import gpxpy
import gpxpy.gpx
import datetime
from dateutil import parser as date_parser

def read_gpx_file(file_path):
    """
    读取GPX文件并解析其内容
    
    参数:
        file_path: GPX文件路径
    
    返回:
        包含轨迹点数据的DataFrame和GPX对象
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return None, None
        
        # 获取文件大小
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        print(f"文件大小: {file_size:.2f} MB")
        
        # 打开GPX文件
        with open(file_path, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        
        # 提取基本信息
        print("\n=== GPX文件基本信息 ===")
        print(f"轨迹数量: {len(gpx.tracks)}")
        print(f"路线数量: {len(gpx.routes)}")
        print(f"航点数量: {len(gpx.waypoints)}")
        
        # 创建用于存储所有轨迹点的列表
        track_points = []
        
        # 处理轨迹
        for track_idx, track in enumerate(gpx.tracks):
            print(f"\n轨迹 {track_idx+1}: {track.name if track.name else '未命名'}")
            print(f"  段数: {len(track.segments)}")
            
            for segment_idx, segment in enumerate(track.segments):
                segment_points = []
                for point_idx, point in enumerate(segment.points):
                    point_data = {
                        'track_idx': track_idx,
                        'segment_idx': segment_idx,
                        'point_idx': point_idx,
                        'latitude': point.latitude,
                        'longitude': point.longitude,
                        'elevation': point.elevation,
                        'time': point.time,
                        'type': 'track_point'
                    }
                    
                    # 添加扩展数据（如心率、温度等）
                    if hasattr(point, 'extensions') and point.extensions:
                        for ext in point.extensions:
                            for child in ext:
                                point_data[f'ext_{child.tag.split("}")[-1]}'] = child.text
                    
                    segment_points.append(point_data)
                
                print(f"  段 {segment_idx+1} 包含 {len(segment_points)} 个点")
                track_points.extend(segment_points)
        
        # 处理路线
        for route_idx, route in enumerate(gpx.routes):
            print(f"\n路线 {route_idx+1}: {route.name if route.name else '未命名'}")
            print(f"  点数: {len(route.points)}")
            
            for point_idx, point in enumerate(route.points):
                point_data = {
                    'route_idx': route_idx,
                    'point_idx': point_idx,
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time,
                    'type': 'route_point'
                }
                track_points.append(point_data)
        
        # 处理航点
        for wpt_idx, waypoint in enumerate(gpx.waypoints):
            print(f"\n航点 {wpt_idx+1}: {waypoint.name if waypoint.name else '未命名'}")
            
            point_data = {
                'wpt_idx': wpt_idx,
                'latitude': waypoint.latitude,
                'longitude': waypoint.longitude,
                'elevation': waypoint.elevation,
                'time': waypoint.time,
                'name': waypoint.name,
                'description': waypoint.description,
                'symbol': waypoint.symbol,
                'type': 'waypoint'
            }
            track_points.append(point_data)
        
        # 如果没有点数据，返回None
        if not track_points:
            print("警告: GPX文件不包含任何轨迹点、路线点或航点")
            return None, gpx
        
        # 创建DataFrame
        df = pd.DataFrame(track_points)
        
        # 转换时间格式
        if 'time' in df.columns:
            # 将时间对象转换为字符串，再转换为datetime
            df['time'] = df['time'].apply(lambda x: pd.to_datetime(x) if x else None)
        
        # 计算附加数据（如果有时间信息）
        if 'time' in df.columns and df['time'].notna().any():
            # 按轨迹和段进行分组
            if all(col in df.columns for col in ['track_idx', 'segment_idx']):
                df = df.sort_values(['track_idx', 'segment_idx', 'point_idx'])
                
                # 计算时间差
                df['time_diff'] = df.groupby(['track_idx', 'segment_idx'])['time'].diff()
                df['time_diff_seconds'] = df['time_diff'].dt.total_seconds()
                
                # 计算点间距离
                df['distance'] = df.groupby(['track_idx', 'segment_idx']).apply(
                    lambda x: calculate_distances(x)
                ).reset_index(level=[0, 1], drop=True)
                
                # 计算速度 (m/s)
                mask = (df['time_diff_seconds'] > 0) & (df['distance'].notna())
                df.loc[mask, 'speed'] = df.loc[mask, 'distance'] / df.loc[mask, 'time_diff_seconds']
                
                # 计算累计距离
                df['cumulative_distance'] = df.groupby(['track_idx', 'segment_idx'])['distance'].cumsum()
        
        # 显示数据预览
        print("\n=== 数据预览 ===")
        print(f"总点数: {len(df)}")
        print(f"列名: {df.columns.tolist()}")
        
        # 显示数据头部
        print("\n前5行数据:")
        preview_df = df.head(5)
        print(preview_df)
        
        # 显示数据统计
        print("\n=== 数据统计 ===")
        num_cols = ['latitude', 'longitude']
        if 'elevation' in df.columns and df['elevation'].notna().any():
            num_cols.append('elevation')
        if 'speed' in df.columns and df['speed'].notna().any():
            num_cols.append('speed')
        if 'distance' in df.columns and df['distance'].notna().any():
            num_cols.append('distance')
        
        print(df[num_cols].describe())
        
        # 检测时间范围
        if 'time' in df.columns and df['time'].notna().any():
            start_time = df['time'].min()
            end_time = df['time'].max()
            duration = end_time - start_time
            
            print(f"\n时间范围: {start_time} 至 {end_time}")
            print(f"持续时间: {duration}")
        
        return df, gpx
        
    except Exception as e:
        print(f"读取GPX文件时发生错误: {str(e)}")
        return None, None

def calculate_distances(group):
    """计算两点之间的距离 (haversine公式)"""
    import numpy as np
    
    # 地球半径（米）
    R = 6371000
    
    # 将经纬度转换为弧度
    lat1 = np.radians(group['latitude'].shift(1))
    lon1 = np.radians(group['longitude'].shift(1))
    lat2 = np.radians(group['latitude'])
    lon2 = np.radians(group['longitude'])
    
    # 计算差值
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine公式
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = R * c
    
    return distance

def plot_gpx_track(df, title="GPX轨迹"):
    """绘制GPX轨迹图"""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print("警告: 数据中没有经纬度信息，无法绘图")
        return
    
    try:
        plt.figure(figsize=(12, 8))
        
        # 确定是否按轨迹和段分组绘图
        if 'type' in df.columns:
            # 绘制轨迹点
            track_points = df[df['type'] == 'track_point']
            if not track_points.empty:
                # 按轨迹和段进行分组
                if all(col in track_points.columns for col in ['track_idx', 'segment_idx']):
                    for (track_idx, segment_idx), group in track_points.groupby(['track_idx', 'segment_idx']):
                        label = f"轨迹 {track_idx+1}, 段 {segment_idx+1}"
                        plt.plot(group['longitude'], group['latitude'], '-', linewidth=1.5, label=label)
                else:
                    plt.plot(track_points['longitude'], track_points['latitude'], 'b-', linewidth=1.5, label='轨迹点')
            
            # 绘制路线点
            route_points = df[df['type'] == 'route_point']
            if not route_points.empty:
                if 'route_idx' in route_points.columns:
                    for route_idx, group in route_points.groupby('route_idx'):
                        plt.plot(group['longitude'], group['latitude'], '--', linewidth=1.5, label=f"路线 {route_idx+1}")
                else:
                    plt.plot(route_points['longitude'], route_points['latitude'], 'g--', linewidth=1.5, label='路线点')
            
            # 绘制航点
            waypoints = df[df['type'] == 'waypoint']
            if not waypoints.empty:
                plt.scatter(waypoints['longitude'], waypoints['latitude'], c='red', s=50, marker='^', label='航点')
                
                # 如果航点有名称，添加标签
                if 'name' in waypoints.columns:
                    for _, wpt in waypoints.iterrows():
                        if wpt['name']:
                            plt.annotate(wpt['name'], 
                                        xy=(wpt['longitude'], wpt['latitude']),
                                        xytext=(5, 5),
                                        textcoords='offset points')
        else:
            # 简单绘图（不区分类型）
            plt.plot(df['longitude'], df['latitude'], 'b-', linewidth=1.5)
            plt.plot(df['longitude'].iloc[0], df['latitude'].iloc[0], 'go', markersize=8, label='起点')
            plt.plot(df['longitude'].iloc[-1], df['latitude'].iloc[-1], 'ro', markersize=8, label='终点')
        
        plt.title(title)
        plt.xlabel('经度')
        plt.ylabel('纬度')
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        
        # 如果有高度数据，绘制3D图
        if 'elevation' in df.columns and df['elevation'].notna().any():
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            if 'type' in df.columns:
                # 按类型分组绘制3D图
                for point_type, group in df.groupby('type'):
                    if point_type == 'track_point':
                        if all(col in group.columns for col in ['track_idx', 'segment_idx']):
                            for (track_idx, segment_idx), subgroup in group.groupby(['track_idx', 'segment_idx']):
                                label = f"轨迹 {track_idx+1}, 段 {segment_idx+1}"
                                ax.plot(subgroup['longitude'], subgroup['latitude'], subgroup['elevation'], 
                                       '-', linewidth=1.5, label=label)
                        else:
                            ax.plot(group['longitude'], group['latitude'], group['elevation'], 
                                   'b-', linewidth=1.5, label='轨迹点')
                    elif point_type == 'route_point':
                        ax.plot(group['longitude'], group['latitude'], group['elevation'], 
                               'g--', linewidth=1.5, label='路线点')
                    elif point_type == 'waypoint':
                        ax.scatter(group['longitude'], group['latitude'], group['elevation'], 
                                  c='red', s=50, marker='^', label='航点')
            else:
                # 简单3D绘图
                ax.plot(df['longitude'], df['latitude'], df['elevation'], 'b-', linewidth=1.5)
            
            ax.set_xlabel('经度')
            ax.set_ylabel('纬度')
            ax.set_zlabel('高度 (m)')
            ax.set_title('3D GPX轨迹')
            ax.legend()
        
        # 如果有时间和速度数据，绘制速度-时间图
        if all(col in df.columns for col in ['time', 'speed']) and df['speed'].notna().any():
            plt.figure(figsize=(12, 6))
            
            if 'type' in df.columns and 'track_idx' in df.columns and 'segment_idx' in df.columns:
                track_points = df[df['type'] == 'track_point']
                for (track_idx, segment_idx), group in track_points.groupby(['track_idx', 'segment_idx']):
                    label = f"轨迹 {track_idx+1}, 段 {segment_idx+1}"
                    plt.plot(group['time'], group['speed'], '-', label=label)
            else:
                plt.plot(df['time'], df['speed'], 'b-')
            
            plt.title('速度变化图')
            plt.xlabel('时间')
            plt.ylabel('速度 (m/s)')
            plt.grid(True)
            if 'track_idx' in df.columns:
                plt.legend()
        
        # 如果有高度和距离数据，绘制高度剖面图
        if all(col in df.columns for col in ['elevation', 'cumulative_distance']) and df['elevation'].notna().any():
            plt.figure(figsize=(12, 6))
            
            if 'type' in df.columns and 'track_idx' in df.columns and 'segment_idx' in df.columns:
                track_points = df[df['type'] == 'track_point']
                for (track_idx, segment_idx), group in track_points.groupby(['track_idx', 'segment_idx']):
                    label = f"轨迹 {track_idx+1}, 段 {segment_idx+1}"
                    plt.plot(group['cumulative_distance']/1000, group['elevation'], '-', label=label)
            else:
                plt.plot(df['cumulative_distance']/1000, df['elevation'], 'b-')
            
            plt.title('高度剖面图')
            plt.xlabel('距离 (km)')
            plt.ylabel('高度 (m)')
            plt.grid(True)
            if 'track_idx' in df.columns:
                plt.legend()
        
        plt.show()
    except Exception as e:
        print(f"绘图时出错: {str(e)}")

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='读取GPX文件')
    parser.add_argument('file_path', nargs='?', help='GPX文件路径')
    parser.add_argument('-p', '--plot', action='store_true', help='绘制轨迹图')
    parser.add_argument('-o', '--output', help='输出CSV文件的路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 获取文件路径
    file_path = args.file_path
    if not file_path:
        file_path = input("请输入GPX文件路径: ")
    
    # 读取数据
    df, gpx = read_gpx_file(file_path)
    
    if df is not None:
        print(f"\n成功读取GPX文件: {file_path}")
        
        # 绘制轨迹
        if args.plot:
            plot_gpx_track(df)
        
        # 保存为CSV
        if args.output:
            output_path = args.output
            df.to_csv(output_path, index=False)
            print(f"数据已保存为CSV文件: {output_path}")
        else:
            save_option = input("\n是否需要将数据保存为CSV文件? (y/n): ")
            if save_option.lower() == 'y':
                output_path = os.path.splitext(file_path)[0] + '.csv'
                df.to_csv(output_path, index=False)
                print(f"数据已保存为CSV文件: {output_path}")

if __name__ == "__main__":
    main() 