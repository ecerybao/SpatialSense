import pickle
import numpy as np
import pandas as pd
import pprint

def read_pickle_file(file_path):
    """
    读取pickle文件并返回其中的数据
    
    参数:
        file_path (str): pickle文件的路径
    
    返回:
        读取的数据对象
    """
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        print("数据读取成功！")
        return data
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{str(e)}")
        return None

def display_data_content(data, max_items=5, max_depth=3, current_depth=0):
    """
    递归显示数据内容，适用于复杂的嵌套结构
    
    参数:
        data: 要显示的数据对象
        max_items: 每个列表/字典显示的最大项目数
        max_depth: 最大递归深度
        current_depth: 当前递归深度
    """
    if current_depth >= max_depth:
        return "... (达到最大递归深度)"
    
    # 处理不同类型的数据
    if isinstance(data, (list, tuple)):
        if len(data) == 0:
            return "[]"
        
        result = "[\n"
        for i, item in enumerate(data[:max_items]):
            result += f"  {'  ' * current_depth}[{i}]: "
            result += str(display_data_content(item, max_items, max_depth, current_depth + 1))
            result += ",\n"
        
        if len(data) > max_items:
            result += f"  {'  ' * current_depth}... (还有{len(data) - max_items}项未显示)\n"
        
        result += f"{'  ' * current_depth}]"
        return result
    
    elif isinstance(data, dict):
        if len(data) == 0:
            return "{}"
        
        result = "{\n"
        for i, (key, value) in enumerate(list(data.items())[:max_items]):
            result += f"  {'  ' * current_depth}{key}: "
            result += str(display_data_content(value, max_items, max_depth, current_depth + 1))
            result += ",\n"
        
        if len(data) > max_items:
            result += f"  {'  ' * current_depth}... (还有{len(data) - max_items}项未显示)\n"
        
        result += f"{'  ' * current_depth}}}"
        return result
    
    elif isinstance(data, np.ndarray):
        return f"numpy.ndarray(shape={data.shape}, dtype={data.dtype})"
    
    elif isinstance(data, pd.DataFrame):
        return f"pandas.DataFrame(shape={data.shape})\n{data.head(max_items).to_string()}"
    
    else:
        return str(data)

def main():
    # 指定要读取的pickle文件路径
    pickle_file_path = "/Users/bob/Downloads/SpatialSense/LLMob-main/database/2019/67.pkl"  # 替换为你的文件路径
    
    # 读取数据
    data = read_pickle_file(pickle_file_path)
    
    # 如果成功读取数据，则打印数据的基本信息
    if data is not None:
        print("\n数据类型:", type(data))
        
        # 根据数据类型显示不同的信息
        if isinstance(data, dict):
            print("字典键:", list(data.keys()))
            print("数据包含", len(data), "个键值对")
        elif isinstance(data, list):
            print("列表长度:", len(data))
            if len(data) > 0:
                print("第一个元素类型:", type(data[0]))
                
                # 如果是列表的列表，显示第一个子列表的长度
                if isinstance(data[0], list):
                    print("第一个子列表长度:", len(data[0]))
                    if len(data[0]) > 0:
                        print("第一个子列表的第一个元素类型:", type(data[0][0]))
        elif hasattr(data, 'shape'):  # 对于numpy数组或pandas DataFrame
            print("数据形状:", data.shape)
        
        # 显示详细内容
        print("\n=== 数据内容摘要 ===")
        print(display_data_content(data))
        
        # 对于列表类型，尝试显示所有元素的长度
        if isinstance(data, list):
            print("\n=== 列表元素长度 ===")
            for i, item in enumerate(data):
                print(f"元素[{i}]长度: {len(item) if hasattr(item, '__len__') else '不可测量'}")
        
        # 保存为文本文件以便详细查看
        output_file = pickle_file_path.replace('.pkl', '_content.txt')
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"数据类型: {type(data)}\n\n")
                f.write(display_data_content(data, max_items=20, max_depth=5))
            print(f"\n详细内容已保存到: {output_file}")
        except Exception as e:
            print(f"保存内容到文件时出错: {str(e)}")

if __name__ == "__main__":
    main()