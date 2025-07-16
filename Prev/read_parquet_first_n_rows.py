import pandas as pd
import os
import sys
import argparse
import pyarrow as pa
import pyarrow.parquet as pq

def read_first_n_rows(file_path, n_rows=50):
    """
    读取Parquet文件的前n行并显示详细信息
    
    参数:
        file_path: Parquet文件的路径
        n_rows: 要读取的行数，默认为50
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 不存在")
            return None
        
        # 获取文件大小
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        print(f"文件大小: {file_size:.2f} MB")
        
        # 读取parquet文件元数据
        parquet_file = pq.ParquetFile(file_path)
        num_row_groups = parquet_file.num_row_groups
        total_rows = parquet_file.metadata.num_rows
        
        print(f"Parquet文件信息: 共{total_rows}行，{num_row_groups}个行组")
        
        # 读取Parquet文件的前n行
        print(f"正在读取文件: {file_path} 的前{n_rows}行...")
        df = pd.read_parquet(file_path, engine='pyarrow')
        
        # 只保留前n行
        df = df.head(n_rows)
        
        # 显示基本信息
        print("\n=== 文件基本信息 ===")
        print(f"读取行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {df.columns.tolist()}")
        
        # 显示数据类型
        print("\n=== 数据类型 ===")
        print(df.dtypes)
        
        # 显示数据预览（最多显示前10行）
        preview_rows = min(10, len(df))
        print(f"\n=== 数据预览 (前{preview_rows}行) ===")
        print(df.head(preview_rows))
        
        # 显示基本统计
        if df.select_dtypes(include=['number']).columns.any():
            print("\n=== 数值列统计 ===")
            print(df.describe())
        
        # 显示缺失值信息
        print("\n=== 缺失值信息 ===")
        missing_data = df.isnull().sum()
        print(missing_data[missing_data > 0] if missing_data.any() else "没有缺失值")
        
        # 显示Parquet文件的schema
        print("\n=== Parquet Schema ===")
        print(parquet_file.schema)
        
        # 返回DataFrame以便进一步处理
        return df
        
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='读取Parquet文件的前n行')
    parser.add_argument('file_path', nargs='?', help='Parquet文件的路径')
    parser.add_argument('-n', '--rows', type=int, default=50, help='要读取的行数 (默认: 50)')
    parser.add_argument('-s', '--save', action='store_true', help='自动保存读取的数据到新文件，不询问')
    parser.add_argument('-o', '--output', help='保存输出的文件路径 (默认: 原文件名_firstN.parquet)')
    parser.add_argument('--csv', action='store_true', help='将结果保存为CSV格式而不是Parquet格式')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 获取文件路径
    file_path = args.file_path
    if not file_path:
        file_path = input("请输入Parquet文件的路径: ")
    
    # 读取并显示数据
    df = read_first_n_rows(file_path, args.rows)
    
    if df is not None:
        # 处理保存选项
        if args.save:
            save_option = 'y'
        else:
            save_option = input(f"\n是否需要将前{args.rows}行保存为新文件? (y/n): ")
        
        if save_option.lower() == 'y':
            if args.output:
                output_path = args.output
            else:
                base_name = file_path.rsplit('.', 1)[0]
                if args.csv:
                    output_path = f"{base_name}_first{args.rows}.csv"
                else:
                    output_path = f"{base_name}_first{args.rows}.parquet"
            
            if args.csv:
                df.to_csv(output_path, index=False)
                print(f"已将前{args.rows}行保存为CSV文件: {output_path}")
            else:
                df.to_parquet(output_path, index=False)
                print(f"已将前{args.rows}行保存为Parquet文件: {output_path}")

if __name__ == "__main__":
    main() 