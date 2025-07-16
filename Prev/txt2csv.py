import pandas as pd
import csv

# 定义列名
columns = ['UserID', 'LocationID', 'CategoryID', 'CategoryName', 'Latitude', 
           'Longitude', 'UnknownValue', 'Timestamp']

# 从TXT文件读取数据
def format_tsv_data(input_file, output_file=None):
    # 读取为DataFrame
    df = pd.read_csv(input_file, sep='\t', header=None, names=columns)
    
    # 显示基本信息
    print(f"数据中共有 {len(df)} 条记录")
    print(f"涉及 {df['UserID'].nunique()} 个独立用户")
    print(f"包含 {df['CategoryName'].nunique()} 种不同类型的地点")
    
    # 展示前5行数据，格式美观
    print("\n前5行数据:")
    print(df.head().to_string())
    
    # 可选：保存为更易读的格式
    if output_file:
        if output_file.endswith('.csv'):
            df.to_csv(output_file, index=False)
            print(f"\n数据已保存为CSV文件: {output_file}")
        elif output_file.endswith('.xlsx'):
            df.to_excel(output_file, index=False)
            print(f"\n数据已保存为Excel文件: {output_file}")
        elif output_file.endswith('.html'):
            df.to_html(output_file)
            print(f"\n数据已保存为HTML文件: {output_file}")
    
    return df

# 使用示例
data = format_tsv_data("/Users/bob/Downloads/SpatialSense/datasets/tky/raw/dataset_TSMC2014_TKY.txt", "/Users/bob/Downloads/SpatialSense/datasets/tky/raw/tokyo_location_data.csv")