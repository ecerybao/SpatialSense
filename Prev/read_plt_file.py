import pandas as pd
import os
import argparse
import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import folium
from folium.plugins import HeatMap

def read_plt_file(file_path, n_rows=None, skip_header=6):
    """
    读取GPS轨迹PLT文件
    
    参数:
        file_path: PLT文件路径
        n_rows: 要读取的行数，None表示读取全部
        skip_header: 要跳过的头部行数，默认为6行
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return None
        
        # 获取文件大小
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        print(f"文件大小: {file_size:.2f} MB")
        
        # 读取文件头部
        header_lines = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i in range(skip_header):
                try:
                    line = f.readline()
                    header_lines.append(line.strip())
                except:
                    break
        
        print("文件头部内容:")
        for line in header_lines:
            print(f"  {line}")
        
        # 读取数据部分
        # PLT文件通常包含经度,纬度,0,高度,日期,时间
        # 例如: 39.906631,116.391549,0,492,40097.5864583333,2009-10-11,02:04:30
        
        try:
            # 尝试不同的分隔符和编码方式
            try:
                # 尝试逗号分隔
                df = pd.read_csv(file_path, skiprows=skip_header, header=None, nrows=n_rows)
            except:
                # 尝试制表符分隔
                df = pd.read_csv(file_path, skiprows=skip_header, header=None, sep='\t', nrows=n_rows)
            
            # 检查列数并尝试识别格式
            if len(df.columns) >= 4:
                # 根据列数猜测格式并添加列名
                if len(df.columns) == 7:
                    df.columns = ['latitude', 'longitude', 'zero', 'altitude', 'date_num', 'date', 'time']
                elif len(df.columns) == 6:
                    df.columns = ['latitude', 'longitude', 'zero', 'altitude', 'date_num', 'date_time']
                elif len(df.columns) == 5:
                    df.columns = ['latitude', 'longitude', 'zero', 'altitude', 'date_time']
                elif len(df.columns) == 4:
                    df.columns = ['latitude', 'longitude', 'zero', 'altitude']
                else:
                    # 给超过7列的数据添加泛化列名
                    base_cols = ['latitude', 'longitude', 'zero', 'altitude', 'date_num', 'date', 'time']
                    extra_cols = [f'extra_{i+1}' for i in range(len(df.columns) - 7)]
                    df.columns = base_cols + extra_cols
                
            else:
                # 如果列数太少，可能不是标准PLT格式
                print("警告: 文件格式可能不是标准GPS轨迹PLT格式")
                # 添加通用列名
                df.columns = [f'column_{i+1}' for i in range(len(df.columns))]
        
        except Exception as e:
            print(f"尝试解析PLT数据时出错: {str(e)}")
            # 尝试基本的文本文件读取
            lines = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 跳过头部
                for _ in range(skip_header):
                    f.readline()
                
                # 读取指定行数或全部
                if n_rows is not None:
                    for i in range(n_rows):
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line.strip())
                else:
                    lines = [line.strip() for line in f]
            
            print(f"读取了{len(lines)}行原始数据")
            if lines:
                print("数据示例:")
                for i, line in enumerate(lines[:5]):
                    print(f"  行 {i+1}: {line}")
                
                # 尝试创建数据框
                try:
                    # 检测分隔符
                    if ',' in lines[0]:
                        sep = ','
                    elif '\t' in lines[0]:
                        sep = '\t'
                    else:
                        sep = None
                    
                    if sep:
                        # 如果可以检测到分隔符，尝试解析
                        data = [line.split(sep) for line in lines]
                        df = pd.DataFrame(data)
                    else:
                        return None
                except:
                    return None
        
        # 显示基本信息
        print("\n=== 文件基本信息 ===")
        print(f"读取行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {df.columns.tolist()}")
        
        # 显示数据类型
        print("\n=== 数据类型 ===")
        print(df.dtypes)
        
        # 显示数据预览
        preview_rows = min(10, len(df))
        print(f"\n=== 数据预览 (前{preview_rows}行) ===")
        print(df.head(preview_rows))
        
        # 尝试转换数据类型
        try:
            # 转换经纬度和高度为float
            if 'latitude' in df.columns and 'longitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            if 'altitude' in df.columns:
                df['altitude'] = pd.to_numeric(df['altitude'], errors='coerce')
            
            # 如果存在日期和时间列，尝试转换为datetime
            if 'date' in df.columns and 'time' in df.columns:
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], errors='coerce')
            elif 'date_time' in df.columns:
                df['datetime'] = pd.to_datetime(df['date_time'], errors='coerce')
        except Exception as e:
            print(f"转换数据类型时出错: {str(e)}")
        
        # 显示数据统计
        if any(col in df.columns for col in ['latitude', 'longitude', 'altitude']):
            print("\n=== 位置数据统计 ===")
            stats_cols = [col for col in ['latitude', 'longitude', 'altitude'] if col in df.columns]
            print(df[stats_cols].describe())
        
        return df
        
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def plot_gps_track(df):
    """绘制GPS轨迹图"""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print("警告: 数据中没有经纬度信息，无法绘图")
        return
    
    try:
        plt.figure(figsize=(10, 8))
        plt.plot(df['longitude'], df['latitude'], 'b-', linewidth=1, alpha=0.7)
        plt.plot(df['longitude'].iloc[0], df['latitude'].iloc[0], 'go', markersize=8, label='起点')
        plt.plot(df['longitude'].iloc[-1], df['latitude'].iloc[-1], 'ro', markersize=8, label='终点')
        
        plt.title('GPS轨迹')
        plt.xlabel('经度')
        plt.ylabel('纬度')
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        
        # 如果有高度数据，绘制3D图
        if 'altitude' in df.columns and df['altitude'].notna().any():
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(df['longitude'], df['latitude'], df['altitude'], 'b-', linewidth=1, alpha=0.7)
            ax.set_xlabel('经度')
            ax.set_ylabel('纬度')
            ax.set_zlabel('高度 (m)')
            ax.set_title('3D GPS轨迹')
        
        plt.show()
    except Exception as e:
        print(f"绘图时出错: {str(e)}")

def create_interactive_map(df, output_file='gps_track_map.html'):
    """
    创建交互式地图并保存
    
    参数:
        df: 包含经纬度数据的DataFrame
        output_file: 输出HTML文件的路径
    """
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        print("警告: 数据中没有经纬度信息，无法创建地图")
        return
    
    try:
        # 计算地图中心点
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # 创建地图对象
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
        
        # 创建轨迹线
        coordinates = [[row['latitude'], row['longitude']] 
                      for idx, row in df.iterrows()]
        
        # 添加轨迹线到地图
        folium.PolyLine(
            coordinates,
            weight=2.5,
            color='blue',
            opacity=0.8
        ).add_to(m)
        
        # 添加起点标记（绿色）
        folium.Marker(
            coordinates[0],
            popup='起点',
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        # 添加终点标记（红色）
        folium.Marker(
            coordinates[-1],
            popup='终点',
            icon=folium.Icon(color='red')
        ).add_to(m)
        
        # 添加热力图
        HeatMap(coordinates).add_to(m)
        
        # 保存地图
        m.save(output_file)
        print(f"交互式地图已保存为: {output_file}")
        
    except Exception as e:
        print(f"创建交互式地图时出错: {str(e)}")

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='读取GPS轨迹PLT文件')
    parser.add_argument('file_path', nargs='?', help='PLT文件路径')
    parser.add_argument('-n', '--rows', type=int, help='要读取的行数，默认全部读取')
    parser.add_argument('-s', '--skip', type=int, default=6, help='要跳过的头部行数 (默认: 6)')
    parser.add_argument('-p', '--plot', action='store_true', help='绘制GPS轨迹图')
    parser.add_argument('-m', '--map', action='store_true', help='创建交互式地图')
    parser.add_argument('-o', '--output', help='输出CSV文件的路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 获取文件路径
    file_path = args.file_path
    if not file_path:
        file_path = input("请输入PLT文件路径: ")
    
    # 读取数据
    df = read_plt_file(file_path, args.rows, args.skip)
    
    if df is not None:
        print(f"\n成功读取PLT文件: {file_path}")
        
        # 绘制GPS轨迹
        if args.plot:
            plot_gps_track(df)
        
        # 创建交互式地图
        if args.map:
            output_map = os.path.splitext(file_path)[0] + '_map.html'
            create_interactive_map(df, output_map)
        
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