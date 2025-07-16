import json
import math
from typing import Dict, List, Tuple, Any, Optional
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI
import os
import re

class SpatialReasoningFramework:
    """
    基于LLM的空间关系判断工具调用框架
    支持点-点、点-线、点-多边形、线-线、线-多边形、多边形-多边形关系判断
    """
    
    def __init__(self):
        self.tools = {
            "point_point_relation": self.point_point_relation,
            "point_line_relation": self.point_line_relation,
            "point_polygon_relation": self.point_polygon_relation,
            "line_line_relation": self.line_line_relation,
            "line_polygon_relation": self.line_polygon_relation,
            "polygon_polygon_relation": self.polygon_polygon_relation,
            "visualize_spatial_relation": self.visualize_spatial_relation,
            "get_available_relations": self.get_available_relations
        }
    
    def get_tool_descriptions(self) -> Dict[str, Dict]:
        """获取所有工具的描述信息，用于LLM理解工具功能"""
        return {
            "point_point_relation": {
                "description": "判断两个点之间的空间关系",
                "parameters": {
                    "point1": {"type": "list", "description": "第一个点的坐标 [x, y]"},
                    "point2": {"type": "list", "description": "第二个点的坐标 [x, y]"}
                },
                "returns": "空间关系字符串：'Equals' 或 'Disjoint'"
            },
            "point_line_relation": {
                "description": "判断点和线段之间的空间关系",
                "parameters": {
                    "point": {"type": "list", "description": "点的坐标 [x, y]"},
                    "line": {"type": "list", "description": "线段的坐标 [[x1, y1], [x2, y2]]"}
                },
                "returns": "空间关系字符串：'Touches', 'Within', 或 'Disjoint'"
            },
            "point_polygon_relation": {
                "description": "判断点和多边形之间的空间关系",
                "parameters": {
                    "point": {"type": "list", "description": "点的坐标 [x, y]"},
                    "polygon": {"type": "list", "description": "多边形的坐标 [[x1, y1], [x2, y2], ...]"}
                },
                "returns": "空间关系字符串：'Within', 'Touches', 或 'Disjoint'"
            },
            "line_line_relation": {
                "description": "判断两条线段之间的空间关系",
                "parameters": {
                    "line1": {"type": "list", "description": "第一条线段的坐标 [[x1, y1], [x2, y2]]"},
                    "line2": {"type": "list", "description": "第二条线段的坐标 [[x1, y1], [x2, y2]]"}
                },
                "returns": "空间关系字符串：'Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 或 'Disjoint'"
            },
            "line_polygon_relation": {
                "description": "判断线段和多边形之间的空间关系",
                "parameters": {
                    "line": {"type": "list", "description": "线段的坐标 [[x1, y1], [x2, y2]]"},
                    "polygon": {"type": "list", "description": "多边形的坐标 [[x1, y1], [x2, y2], ...]"}
                },
                "returns": "空间关系字符串：'Within', 'Crosses', 'Touches', 或 'Disjoint'"
            },
            "polygon_polygon_relation": {
                "description": "判断两个多边形之间的空间关系",
                "parameters": {
                    "polygon1": {"type": "list", "description": "第一个多边形的坐标 [[x1, y1], [x2, y2], ...]"},
                    "polygon2": {"type": "list", "description": "第二个多边形的坐标 [[x1, y1], [x2, y2], ...]"}
                },
                "returns": "空间关系字符串：'Equals', 'Contains', 'Within', 'Overlaps', 或 'Disjoint'"
            },
            "visualize_spatial_relation": {
                "description": "可视化空间关系并保存图片",
                "parameters": {
                    "entity1": {"type": "dict", "description": "第一个几何对象 {'type': 'point/line/polygon', 'coordinates': [...]}"},
                    "entity2": {"type": "dict", "description": "第二个几何对象 {'type': 'point/line/polygon', 'coordinates': [...]}"},
                    "relation": {"type": "string", "description": "空间关系"},
                    "filename": {"type": "string", "description": "保存的文件名"}
                },
                "returns": "图片保存路径"
            },
            "get_available_relations": {
                "description": "获取所有支持的空间关系类型",
                "parameters": {},
                "returns": "所有支持的空间关系列表"
            }
        }
    
    def point_point_relation(self, point1: List[float], point2: List[float]) -> str:
        """判断两个点之间的空间关系"""
        p1 = Point(point1[0], point1[1])
        p2 = Point(point2[0], point2[1])
        
        if p1.equals(p2):
            return "Equals"
        else:
            return "Disjoint"
    
    def point_line_relation(self, point: List[float], line: List[List[float]]) -> str:
        """判断点和线段之间的空间关系"""
        p = Point(point[0], point[1])
        l = LineString(line)
        
        # 检查点是否在线段上
        if p.touches(l):
            return "Touches"
        elif p.within(l):
            return "Within"
        else:
            return "Disjoint"
    
    def point_polygon_relation(self, point: List[float], polygon: List[List[float]]) -> str:
        """判断点和多边形之间的空间关系"""
        p = Point(point[0], point[1])
        poly = Polygon(polygon)
        
        if p.within(poly):
            return "Within"
        elif p.touches(poly):
            return "Touches"
        else:
            return "Disjoint"
    
    def line_line_relation(self, line1: List[List[float]], line2: List[List[float]]) -> str:
        """判断两条线段之间的空间关系"""
        l1 = LineString(line1)
        l2 = LineString(line2)
        
        if l1.equals(l2):
            return "Equals"
        elif l1.contains(l2):
            return "Contains"
        elif l1.within(l2):
            return "Within"
        elif l1.overlaps(l2):
            return "Overlaps"
        elif l1.crosses(l2):
            return "Crosses"
        elif l1.touches(l2):
            return "Touches"
        else:
            return "Disjoint"
    
    def line_polygon_relation(self, line: List[List[float]], polygon: List[List[float]]) -> str:
        """判断线段和多边形之间的空间关系"""
        l = LineString(line)
        poly = Polygon(polygon)
        
        if l.within(poly):
            return "Within"
        elif l.crosses(poly):
            return "Crosses"
        elif l.touches(poly):
            return "Touches"
        else:
            return "Disjoint"
    
    def polygon_polygon_relation(self, polygon1: List[List[float]], polygon2: List[List[float]]) -> str:
        """判断两个多边形之间的空间关系"""
        poly1 = Polygon(polygon1)
        poly2 = Polygon(polygon2)
        
        if poly1.equals(poly2):
            return "Equals"
        elif poly1.contains(poly2):
            return "Contains"
        elif poly1.within(poly2):
            return "Within"
        elif poly1.overlaps(poly2):
            return "Overlaps"
        else:
            return "Disjoint"
    
    def visualize_spatial_relation(self, entity1: Dict, entity2: Dict, relation: str, filename: str = "spatial_relation.png") -> str:
        """可视化空间关系并保存图片"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制第一个几何对象
        self._plot_geometry(entity1, ax, 'blue', 'Entity 1')
        
        # 绘制第二个几何对象
        self._plot_geometry(entity2, ax, 'red', 'Entity 2')
        
        # 设置图形属性
        ax.set_title(f'Spatial Relation: {relation}', fontsize=14, fontweight='bold')
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        ax.set_aspect('equal')
        
        # 保存图片
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"图片已保存为: {filename}"
    
    def _plot_geometry(self, entity: Dict, ax, color: str, label: str):
        """绘制几何对象"""
        geom_type = entity['type']
        coords = entity['coordinates']
        
        if geom_type == 'point':
            ax.plot(coords[0], coords[1], 'o', color=color, markersize=8, label=label)
        elif geom_type == 'line':
            x_coords, y_coords = zip(*coords)
            ax.plot(x_coords, y_coords, color=color, linewidth=2, label=label)
        elif geom_type == 'polygon':
            # 确保多边形闭合
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            x_coords, y_coords = zip(*coords)
            ax.plot(x_coords, y_coords, color=color, linewidth=2, label=label)
            ax.fill(x_coords, y_coords, color=color, alpha=0.3)
    
    def get_available_relations(self) -> List[str]:
        """获取所有支持的空间关系类型"""
        return [
            "Equals", "Contains", "Within", "Overlaps", 
            "Crosses", "Touches", "Disjoint"
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """执行指定的工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知的工具: {tool_name}")
        
        return self.tools[tool_name](**kwargs)
    
    def get_system_prompt(self) -> str:
        """获取系统提示词，用于指导LLM使用工具"""
        return """你是一个空间关系判断助手。你的任务是使用提供的工具来判断几何对象之间的空间关系。

可用的工具包括：
1. point_point_relation - 判断两个点之间的关系
2. point_line_relation - 判断点和线段之间的关系  
3. point_polygon_relation - 判断点和多边形之间的关系
4. line_line_relation - 判断两条线段之间的关系
5. line_polygon_relation - 判断线段和多边形之间的关系
6. polygon_polygon_relation - 判断两个多边形之间的关系
7. visualize_spatial_relation - 可视化空间关系
8. get_available_relations - 获取所有支持的关系类型

当用户提供几何对象时，你需要：
1. 识别几何对象的类型（点、线段、多边形）
2. 选择合适的工具进行判断
3. 返回准确的空间关系结果
4. 可选择性地生成可视化图片

请始终使用工具来判断空间关系，不要依赖自己的推理能力。"""


class LLMSpatialReasoningAgent:
    """LLM空间推理代理，用于与LLM交互"""
    
    def __init__(self, framework: SpatialReasoningFramework, api_key: str = None, model: str = "gpt-4"):
        self.framework = framework
        self.system_prompt = framework.get_system_prompt()
        self.tool_descriptions = framework.get_tool_descriptions()
        self.model = model
        
        # 设置OpenAI API密钥
        if api_key:
            self.client = OpenAI(api_key=api_key)
        elif os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            print("警告: 未设置OpenAI API密钥，请设置OPENAI_API_KEY环境变量或传入api_key参数")
            self.client = None
    
    def create_tool_calling_prompt(self, user_input: str) -> str:
        """创建包含工具调用信息的提示词"""
        prompt = f"{self.system_prompt}\n\n"
        
        prompt += "可用工具详细说明：\n"
        for tool_name, description in self.tool_descriptions.items():
            prompt += f"\n🔧 {tool_name}:\n"
            prompt += f"   功能: {description['description']}\n"
            prompt += f"   参数: {description['parameters']}\n"
            prompt += f"   返回: {description['returns']}\n"
        
        prompt += f"\n\n📝 用户请求: {user_input}\n\n"
        
        prompt += "🎯 任务指导:\n"
        prompt += "1. 分析用户输入中的几何对象类型（点、线段、多边形）\n"
        prompt += "2. 根据对象类型选择合适的工具\n"
        prompt += "3. 从用户输入中提取坐标参数\n"
        prompt += "4. 按照严格格式输出工具调用\n\n"
        
        prompt += "⚠️ 输出格式要求（必须严格遵守）:\n"
        prompt += "TOOL_CALL: [工具名称]\n"
        prompt += "PARAMETERS: {\"参数名\": 参数值}\n"
        prompt += "END_TOOL_CALL\n\n"
        
        prompt += "📋 示例:\n"
        prompt += "用户输入: 判断点(1,2)和多边形[[0,0],[3,0],[3,3],[0,3]]的关系\n"
        prompt += "正确输出:\n"
        prompt += "TOOL_CALL: point_polygon_relation\n"
        prompt += "PARAMETERS: {\"point\": [1, 2], \"polygon\": [[0, 0], [3, 0], [3, 3], [0, 3]]}\n"
        prompt += "END_TOOL_CALL\n\n"
        
        prompt += "🚨 重要提醒:\n"
        prompt += "- 只输出工具调用格式，不要添加解释或其他文字\n"
        prompt += "- 参数必须是有效的JSON格式\n"
        prompt += "- 坐标必须是数字列表，不要使用字符串\n"
        prompt += "- 必须包含END_TOOL_CALL标记\n\n"
        
        prompt += "现在请为上述用户请求生成工具调用:"
        
        return prompt
    
    def parse_tool_call(self, llm_response: str) -> Tuple[str, Dict]:
        """解析LLM的工具调用响应"""
        try:
            # 首先尝试标准格式
            tool_call_start = llm_response.find("TOOL_CALL:")
            tool_call_end = llm_response.find("END_TOOL_CALL")
            
            if tool_call_start != -1 and tool_call_end != -1:
                tool_call_text = llm_response[tool_call_start:tool_call_end]
                
                # 解析工具名称
                tool_name_line = [line for line in tool_call_text.split('\n') if line.startswith('TOOL_CALL:')][0]
                tool_name = tool_name_line.replace('TOOL_CALL:', '').strip()
                
                # 解析参数
                parameters_line = [line for line in tool_call_text.split('\n') if line.startswith('PARAMETERS:')][0]
                parameters_text = parameters_line.replace('PARAMETERS:', '').strip()
                parameters = json.loads(parameters_text)
                
                return tool_name, parameters
            
            # 如果标准格式失败，尝试智能解析
            return self._smart_parse_tool_call(llm_response)
            
        except Exception as e:
            # 尝试智能解析作为备选方案
            try:
                return self._smart_parse_tool_call(llm_response)
            except Exception as e2:
                raise ValueError(f"解析工具调用失败: {e2}")
    
    def _smart_parse_tool_call(self, llm_response: str) -> Tuple[str, Dict]:
        """智能解析LLM响应，尝试从文本中提取工具调用信息"""
        print(f"尝试智能解析LLM响应: {llm_response[:200]}...")
        
        # 尝试从响应中提取工具名称
        tool_name = None
        for tool in self.tool_descriptions.keys():
            if tool in llm_response.lower():
                tool_name = tool
                break
        
        if not tool_name:
            raise ValueError(f"无法从响应中识别工具名称。响应内容: {llm_response}")
        
        print(f"识别到工具: {tool_name}")
        
        # 尝试从响应中提取JSON格式的参数
        json_match = re.search(r'\{[^}]+\}', llm_response)
        if json_match:
            try:
                parameters = json.loads(json_match.group())
                print(f"成功解析JSON参数: {parameters}")
                return tool_name, parameters
            except json.JSONDecodeError:
                print("JSON解析失败，尝试正则表达式提取")
        
        # 如果JSON解析失败，使用正则表达式提取坐标信息
        
        # 提取点坐标 - 支持多种格式
        point_patterns = [
            r'\[(\d+),\s*(\d+)\]',     # [x,y]
            r'\((\d+),\s*(\d+)\)',     # (x,y)
            r'点\((\d+),(\d+)\)',      # 点(x,y)
            r'(\d+),\s*(\d+)'          # x,y
        ]
        point_matches = []
        for pattern in point_patterns:
            matches = re.findall(pattern, llm_response)
            point_matches.extend(matches)
        
        # 提取多边形/线段的复合坐标
        complex_coord_patterns = [
            r'\[\[([^\]]+)\]\]',                    # [[...]]
            r'polygon.*?\[\[([^\]]+)\]\]',          # polygon[[...]]
            r'多边形\[\[([^\]]+)\]\]',              # 多边形[[...]]
            r'line.*?\[\[([^\]]+)\]\]',             # line[[...]]
            r'线段\[\[([^\]]+)\]\]'                 # 线段[[...]]
        ]
        
        complex_matches = []
        for pattern in complex_coord_patterns:
            matches = re.findall(pattern, llm_response)
            complex_matches.extend(matches)
        
        # 根据工具类型构建参数
        try:
            if "point_point" in tool_name:
                if len(point_matches) >= 2:
                    point1 = [int(point_matches[0][0]), int(point_matches[0][1])]
                    point2 = [int(point_matches[1][0]), int(point_matches[1][1])]
                    return tool_name, {"point1": point1, "point2": point2}
                else:
                    raise ValueError("需要至少2个点坐标")
            
            elif "point_polygon" in tool_name:
                if len(point_matches) >= 1 and len(complex_matches) >= 1:
                    point = [int(point_matches[0][0]), int(point_matches[0][1])]
                    
                    # 解析多边形坐标
                    polygon_str = complex_matches[0]
                    coord_pairs = re.findall(r'(\d+),\s*(\d+)', polygon_str)
                    polygon = [[int(pair[0]), int(pair[1])] for pair in coord_pairs]
                    
                    if len(polygon) < 3:
                        raise ValueError("多边形至少需要3个点")
                    
                    return tool_name, {"point": point, "polygon": polygon}
                else:
                    raise ValueError("需要1个点和1个多边形")
            
            elif "point_line" in tool_name:
                if len(point_matches) >= 1 and len(complex_matches) >= 1:
                    point = [int(point_matches[0][0]), int(point_matches[0][1])]
                    
                    # 解析线段坐标
                    line_str = complex_matches[0]
                    coord_pairs = re.findall(r'(\d+),\s*(\d+)', line_str)
                    line = [[int(pair[0]), int(pair[1])] for pair in coord_pairs]
                    
                    if len(line) < 2:
                        raise ValueError("线段需要至少2个点")
                    
                    return tool_name, {"point": point, "line": line}
                else:
                    raise ValueError("需要1个点和1条线段")
            
            elif "line_line" in tool_name:
                if len(complex_matches) >= 2:
                    # 解析两条线段
                    line1_str = complex_matches[0]
                    line2_str = complex_matches[1]
                    
                    coord_pairs1 = re.findall(r'(\d+),\s*(\d+)', line1_str)
                    coord_pairs2 = re.findall(r'(\d+),\s*(\d+)', line2_str)
                    
                    line1 = [[int(pair[0]), int(pair[1])] for pair in coord_pairs1]
                    line2 = [[int(pair[0]), int(pair[1])] for pair in coord_pairs2]
                    
                    if len(line1) < 2 or len(line2) < 2:
                        raise ValueError("每条线段都需要至少2个点")
                    
                    return tool_name, {"line1": line1, "line2": line2}
                else:
                    raise ValueError("需要2条线段")
            
            elif "line_polygon" in tool_name:
                if len(complex_matches) >= 2:
                    # 第一个是线段，第二个是多边形
                    line_str = complex_matches[0]
                    polygon_str = complex_matches[1]
                    
                    line_coords = re.findall(r'(\d+),\s*(\d+)', line_str)
                    polygon_coords = re.findall(r'(\d+),\s*(\d+)', polygon_str)
                    
                    line = [[int(pair[0]), int(pair[1])] for pair in line_coords]
                    polygon = [[int(pair[0]), int(pair[1])] for pair in polygon_coords]
                    
                    if len(line) < 2:
                        raise ValueError("线段需要至少2个点")
                    if len(polygon) < 3:
                        raise ValueError("多边形需要至少3个点")
                    
                    return tool_name, {"line": line, "polygon": polygon}
                else:
                    raise ValueError("需要1条线段和1个多边形")
            
            elif "polygon_polygon" in tool_name:
                if len(complex_matches) >= 2:
                    polygon1_str = complex_matches[0]
                    polygon2_str = complex_matches[1]
                    
                    coords1 = re.findall(r'(\d+),\s*(\d+)', polygon1_str)
                    coords2 = re.findall(r'(\d+),\s*(\d+)', polygon2_str)
                    
                    polygon1 = [[int(pair[0]), int(pair[1])] for pair in coords1]
                    polygon2 = [[int(pair[0]), int(pair[1])] for pair in coords2]
                    
                    if len(polygon1) < 3 or len(polygon2) < 3:
                        raise ValueError("每个多边形都需要至少3个点")
                    
                    return tool_name, {"polygon1": polygon1, "polygon2": polygon2}
                else:
                    raise ValueError("需要2个多边形")
            
            else:
                raise ValueError(f"未知的工具类型: {tool_name}")
        
        except Exception as e:
            raise ValueError(f"参数构建失败: {e}. 提取到的信息: 点={point_matches}, 复合坐标={complex_matches}")
    

    def execute_llm_request(self, user_input: str, llm_response: str) -> str:
        """执行LLM的请求并返回结果"""
        try:
            # 解析工具调用
            tool_name, parameters = self.parse_tool_call(llm_response)
            
            # 执行工具
            result = self.framework.execute_tool(tool_name, **parameters)
            
            return f"工具执行成功！\n工具: {tool_name}\n参数: {parameters}\n结果: {result}"
        
        except Exception as e:
            return f"工具执行失败: {e}"
    
    def call_llm_with_tools(self, user_input: str, visualize: bool = False) -> Dict:
        """
        调用LLM并使用工具完成空间关系判断
        
        Args:
            user_input: 用户输入的空间关系判断请求
            visualize: 是否生成可视化图片
        
        Returns:
            包含LLM响应和工具执行结果的字典
        """
        try:
            # 检查是否有可用的客户端
            if self.client is None:
                return {
                    "user_input": user_input,
                    "error": "OpenAI API密钥未设置，无法调用LLM",
                    "success": False
                }
            
            # 生成提示词
            prompt = self.create_tool_calling_prompt(user_input)
            
            # 调用LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 低温度确保一致性
                max_tokens=500
            )
            
            llm_response = response.choices[0].message.content
            print(f"LLM响应: {llm_response}")
            
            # 解析并执行工具调用
            tool_result = self.execute_llm_request(user_input, llm_response)
            
            # 如果需要可视化，尝试生成图片
            visualization_result = None
            if visualize:
                try:
                    # 解析工具调用以获取参数
                    tool_name, parameters = self.parse_tool_call(llm_response)
                    
                    # 根据工具类型生成可视化
                    if "point" in tool_name and "polygon" in tool_name:
                        entity1 = {"type": "point", "coordinates": parameters["point"]}
                        entity2 = {"type": "polygon", "coordinates": parameters["polygon"]}
                        relation = self.framework.execute_tool(tool_name, **parameters)
                        visualization_result = self.framework.visualize_spatial_relation(
                            entity1, entity2, relation, "llm_spatial_relation.png"
                        )
                    elif "line" in tool_name and "polygon" in tool_name:
                        entity1 = {"type": "line", "coordinates": parameters["line"]}
                        entity2 = {"type": "polygon", "coordinates": parameters["polygon"]}
                        relation = self.framework.execute_tool(tool_name, **parameters)
                        visualization_result = self.framework.visualize_spatial_relation(
                            entity1, entity2, relation, "llm_spatial_relation.png"
                        )
                    elif "line" in tool_name and "line" in tool_name:
                        entity1 = {"type": "line", "coordinates": parameters["line1"]}
                        entity2 = {"type": "line", "coordinates": parameters["line2"]}
                        relation = self.framework.execute_tool(tool_name, **parameters)
                        visualization_result = self.framework.visualize_spatial_relation(
                            entity1, entity2, relation, "llm_spatial_relation.png"
                        )
                    elif "polygon" in tool_name and "polygon" in tool_name:
                        entity1 = {"type": "polygon", "coordinates": parameters["polygon1"]}
                        entity2 = {"type": "polygon", "coordinates": parameters["polygon2"]}
                        relation = self.framework.execute_tool(tool_name, **parameters)
                        visualization_result = self.framework.visualize_spatial_relation(
                            entity1, entity2, relation, "llm_spatial_relation.png"
                        )
                except Exception as e:
                    visualization_result = f"可视化生成失败: {e}"
            
            return {
                "user_input": user_input,
                "llm_response": llm_response,
                "tool_result": tool_result,
                "visualization": visualization_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "user_input": user_input,
                "error": str(e),
                "success": False
            }


# 示例使用
if __name__ == "__main__":
    # 创建框架
    framework = SpatialReasoningFramework()
    
    # 创建LLM代理（需要设置OpenAI API密钥）
    # 方式1: 通过环境变量设置 OPENAI_API_KEY
    # 方式2: 直接传入api_key参数
    agent = LLMSpatialReasoningAgent(framework, api_key="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", model="gpt-4")
    
    # 示例1: 点-点关系
    print("=== 示例1: 点-点关系 ===")
    result = framework.point_point_relation([1, 2], [1, 2])
    print(f"点(1,2)和点(1,2)的关系: {result}")
    
    # 示例2: 点-多边形关系
    print("\n=== 示例2: 点-多边形关系 ===")
    polygon = [[0, 0], [4, 0], [4, 4], [0, 4]]
    result = framework.point_polygon_relation([2, 2], polygon)
    print(f"点(2,2)和多边形{polygon}的关系: {result}")
    
    # 示例3: 可视化
    print("\n=== 示例3: 可视化 ===")
    entity1 = {"type": "point", "coordinates": [2, 2]}
    entity2 = {"type": "polygon", "coordinates": polygon}
    result = framework.visualize_spatial_relation(entity1, entity2, "Within", "example.png")
    print(result)
    
    # 示例4: LLM工具调用（需要API密钥）
    print("\n=== 示例4: LLM工具调用 ===")
    try:
        llm_result = agent.call_llm_with_tools(
            "判断点(2,2)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系",
            visualize=True
        )
        
        if llm_result["success"]:
            print("LLM工具调用成功！")
            print(f"工具执行结果: {llm_result['tool_result']}")
            if llm_result['visualization']:
                print(f"可视化结果: {llm_result['visualization']}")
        else:
            print(f"LLM工具调用失败: {llm_result['error']}")
            
    except Exception as e:
        print(f"LLM调用失败，请检查API密钥设置: {e}")
        print("提示: 请设置OPENAI_API_KEY环境变量或传入api_key参数")
    
    # 示例5: 更多LLM调用示例
    print("\n=== 示例5: 更多LLM调用示例 ===")
    test_cases = [
        "判断点(3,3)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系",
        "判断线段[[1,1],[3,3]]和线段[[2,2],[4,4]]的空间关系",
        "判断线段[[1,1],[3,3]]和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n测试用例 {i+1}: {test_case}")
        try:
            result = agent.call_llm_with_tools(test_case)
            if result["success"]:
                print(f"结果: {result['tool_result']}")
            else:
                print(f"失败: {result['error']}")
        except Exception as e:
            print(f"调用失败: {e}")
    
    # 示例6: 演示如何设置API密钥
    print("\n=== 示例6: API密钥设置说明 ===")
    print("要使用LLM功能，请按以下方式之一设置API密钥：")
    print("1. 环境变量: export OPENAI_API_KEY='your-api-key-here'")
    print("2. 代码中设置: agent = LLMSpatialReasoningAgent(framework, api_key='your-api-key-here')")
    print("3. 或者使用模拟LLM响应进行测试")
    
    # 示例7: 模拟LLM响应测试（不需要API密钥）
    print("\n=== 示例7: 模拟LLM响应测试 ===")
    mock_llm_response = """TOOL_CALL: point_polygon_relation
PARAMETERS: {"point": [3, 3], "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}
END_TOOL_CALL"""
    
    try:
        tool_result = agent.execute_llm_request("判断点(3,3)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系", mock_llm_response)
        print(f"模拟测试结果: {tool_result}")
    except Exception as e:
        print(f"模拟测试失败: {e}")


def load_test_data(jsonl_file_path: str) -> List[Dict]:
    """加载JSONL测试数据"""
    test_data = []
    try:
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    test_data.append(data)
        print(f"成功加载 {len(test_data)} 条测试数据")
        return test_data
    except Exception as e:
        print(f"加载测试数据失败: {e}")
        return []


def extract_expected_relation(output_text: str) -> str:
    """从输出文本中提取预期的空间关系"""
    # 首先尝试从结尾部分提取单引号内的内容
    lines = output_text.strip().split('\n')
    
    # 从最后几行开始查找，重点关注结尾部分
    for line in reversed(lines[-10:]):  # 检查最后10行
        line = line.strip()
        if not line:
            continue
            
        # 查找单引号包围的空间关系
        # 匹配模式：'RelationName'
        single_quote_pattern = r"'([A-Za-z]+)'"
        matches = re.findall(single_quote_pattern, line)
        if matches:
            relation = matches[-1].strip()  # 取最后一个匹配项
            # 验证是否是有效的空间关系类型
            valid_relations = ['Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 'Disjoint']
            if relation in valid_relations:
                return relation
        
        # 查找双引号包围的空间关系
        # 匹配模式："RelationName"
        double_quote_pattern = r'"([A-Za-z]+)"'
        matches = re.findall(double_quote_pattern, line)
        if matches:
            relation = matches[-1].strip()
            valid_relations = ['Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 'Disjoint']
            if relation in valid_relations:
                return relation
    
    # 如果上述方法失败，尝试从整个文本中查找
    # 查找所有单引号包围的内容
    all_single_quotes = re.findall(r"'([A-Za-z]+)'", output_text)
    if all_single_quotes:
        # 取最后一个单引号内的内容
        last_relation = all_single_quotes[-1].strip()
        valid_relations = ['Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 'Disjoint']
        if last_relation in valid_relations:
            return last_relation
    
    # 查找所有双引号包围的内容
    all_double_quotes = re.findall(r'"([A-Za-z]+)"', output_text)
    if all_double_quotes:
        # 取最后一个双引号内的内容
        last_relation = all_double_quotes[-1].strip()
        valid_relations = ['Equals', 'Contains', 'Within', 'Overlaps', 'Crosses', 'Touches', 'Disjoint']
        if last_relation in valid_relations:
            return last_relation
    
    # 最后尝试从结尾部分查找关键词
    for line in reversed(lines[-5:]):
        line = line.strip()
        if line:
            for keyword in ['Within', 'Disjoint', 'Equals', 'Contains', 'Overlaps', 'Crosses', 'Touches']:
                if keyword in line:
                    return keyword
    
    return None


def run_batch_test(agent: LLMSpatialReasoningAgent, test_data: List[Dict], max_tests: int = None) -> Dict:
    """运行批量测试"""
    if max_tests:
        test_data = test_data[:max_tests]
    
    results = {
        "total": len(test_data),
        "successful": 0,
        "failed": 0,
        "correct": 0,
        "incorrect": 0,
        "details": []
    }
    
    print(f"开始批量测试，共 {len(test_data)} 条数据...")
    
    for i, data in enumerate(test_data):
        print(f"\n处理第 {i+1}/{len(test_data)} 条数据...")
        
        input_text = data["input"]
        expected_output = data["output"]
        
        # 提取预期关系
        expected_relation = extract_expected_relation(expected_output)
        if not expected_relation:
            print(f"警告: 无法从输出中提取预期关系: {expected_output[:100]}...")
            results["failed"] += 1
            results["details"].append({
                "index": i,
                "input": input_text,
                "expected": expected_relation,
                "actual": None,
                "success": False,
                "error": "无法提取预期关系"
            })
            continue
        
        try:
            # 调用LLM
            llm_result = agent.call_llm_with_tools(input_text)
            
            if llm_result["success"]:
                # 从工具执行结果中提取实际关系
                tool_result = llm_result["tool_result"]
                actual_relation = None
                
                # 尝试从工具结果中提取关系
                actual_relation = None
                
                # 方法1: 从"结果:"或"result:"后提取
                if "结果:" in tool_result:
                    actual_relation = tool_result.split("结果:")[-1].strip()
                elif "result:" in tool_result.lower():
                    actual_relation = tool_result.split("result:")[-1].strip()
                
                # 方法2: 从工具名称中推断关系类型
                if not actual_relation and "工具:" in tool_result:
                    tool_name = tool_result.split("工具:")[1].split("\n")[0].strip()
                    if "point_point" in tool_name:
                        # 点-点关系只有Equals和Disjoint
                        if "Equals" in tool_result or "equals" in tool_result.lower():
                            actual_relation = "Equals"
                        else:
                            actual_relation = "Disjoint"
                    elif "point_polygon" in tool_name:
                        # 点-多边形关系
                        for relation in ["Within", "Touches", "Disjoint"]:
                            if relation in tool_result or relation.lower() in tool_result.lower():
                                actual_relation = relation
                                break
                    elif "line_line" in tool_name:
                        # 线-线关系
                        for relation in ["Equals", "Contains", "Within", "Overlaps", "Crosses", "Touches", "Disjoint"]:
                            if relation in tool_result or relation.lower() in tool_result.lower():
                                actual_relation = relation
                                break
                    elif "line_polygon" in tool_name:
                        # 线-多边形关系
                        for relation in ["Within", "Crosses", "Touches", "Disjoint"]:
                            if relation in tool_result or relation.lower() in tool_result.lower():
                                actual_relation = relation
                                break
                    elif "polygon_polygon" in tool_name:
                        # 多边形-多边形关系
                        for relation in ["Equals", "Contains", "Within", "Overlaps", "Disjoint"]:
                            if relation in tool_result or relation.lower() in tool_result.lower():
                                actual_relation = relation
                                break
                
                # 方法3: 从整个结果中提取关系
                if not actual_relation:
                    relation_patterns = [
                        r"['\"]([A-Za-z]+)['\"]",
                        r"([A-Za-z]+)$"
                    ]
                    for pattern in relation_patterns:
                        matches = re.findall(pattern, tool_result, re.IGNORECASE)
                        if matches:
                            # 过滤出有效的关系类型
                            for match in reversed(matches):
                                relation = match.strip()
                                if relation.lower() in ['equals', 'contains', 'within', 'overlaps', 'crosses', 'touches', 'disjoint']:
                                    actual_relation = relation.capitalize()
                                    break
                            if actual_relation:
                                break
                
                if actual_relation:
                    # 比较结果
                    is_correct = actual_relation.lower() == expected_relation.lower()
                    
                    if is_correct:
                        results["correct"] += 1
                        print(f"✓ 正确: 预期 {expected_relation}, 实际 {actual_relation}")
                    else:
                        results["incorrect"] += 1
                        print(f"✗ 错误: 预期 {expected_relation}, 实际 {actual_relation}")
                    
                    results["successful"] += 1
                    results["details"].append({
                        "index": i,
                        "input": input_text,
                        "expected": expected_relation,
                        "actual": actual_relation,
                        "success": True,
                        "correct": is_correct
                    })
                else:
                    print(f"警告: 无法从工具结果中提取关系: {tool_result}")
                    results["failed"] += 1
                    results["details"].append({
                        "index": i,
                        "input": input_text,
                        "expected": expected_relation,
                        "actual": None,
                        "success": False,
                        "error": "无法提取实际关系"
                    })
            else:
                print(f"LLM调用失败: {llm_result['error']}")
                results["failed"] += 1
                results["details"].append({
                    "index": i,
                    "input": input_text,
                    "expected": expected_relation,
                    "actual": None,
                    "success": False,
                    "error": llm_result["error"]
                })
        
        except Exception as e:
            print(f"处理失败: {e}")
            results["failed"] += 1
            results["details"].append({
                "index": i,
                "input": input_text,
                "expected": expected_relation,
                "actual": None,
                "success": False,
                "error": str(e)
            })
    
    # 计算准确率
    if results["successful"] > 0:
        results["accuracy"] = results["correct"] / results["successful"]
    else:
        results["accuracy"] = 0.0
    
    return results


def print_test_results(results: Dict):
    """打印测试结果"""
    print("\n" + "="*50)
    print("批量测试结果")
    print("="*50)
    print(f"总数据量: {results['total']}")
    print(f"成功处理: {results['successful']}")
    print(f"处理失败: {results['failed']}")
    print(f"正确判断: {results['correct']}")
    print(f"错误判断: {results['incorrect']}")
    print(f"准确率: {results['accuracy']:.2%}")
    
    if results["successful"] > 0:
        print(f"\n详细结果:")
        for detail in results["details"]:
            if detail["success"]:
                status = "✓" if detail["correct"] else "✗"
                print(f"{status} 第{detail['index']+1}条: 预期 {detail['expected']}, 实际 {detail['actual']}")
            else:
                print(f"✗ 第{detail['index']+1}条: 失败 - {detail['error']}")


def save_test_results(results: Dict, output_file: str = "test_results.json"):
    """保存测试结果到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n测试结果已保存到: {output_file}")
    except Exception as e:
        print(f"保存测试结果失败: {e}")


# 批量测试功能
def run_comprehensive_test(jsonl_file_path: str, api_key: str = None, max_tests: int = None):
    """运行完整的批量测试"""
    print("开始空间关系判断批量测试...")
    
    # 创建框架和代理
    framework = SpatialReasoningFramework()
    agent = LLMSpatialReasoningAgent(framework, api_key=api_key)
    
    # 加载测试数据
    test_data = load_test_data(jsonl_file_path)
    if not test_data:
        print("没有加载到测试数据，测试终止")
        return
    
    # 运行批量测试
    results = run_batch_test(agent, test_data, max_tests)
    
    # 打印结果
    print_test_results(results)
    
    # 保存结果
    save_test_results(results)
    
    return results


# 如果直接运行此文件，执行批量测试
if __name__ == "__main__":
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        jsonl_file = sys.argv[1]
        max_tests = int(sys.argv[2]) if len(sys.argv) > 2 else None
        api_key = sys.argv[3] if len(sys.argv) > 3 else None
        
        print(f"使用参数: 文件={jsonl_file}, 最大测试数={max_tests}, API密钥={'已设置' if api_key else '未设置'}")
        run_comprehensive_test(jsonl_file, api_key, max_tests)
    else:
        # 默认测试
        print("未提供JSONL文件路径，使用默认示例...")
        
        # 创建框架
        framework = SpatialReasoningFramework()
        
        # 创建LLM代理（需要设置OpenAI API密钥）
        # 方式1: 通过环境变量设置 OPENAI_API_KEY
        # 方式2: 直接传入api_key参数
        agent = LLMSpatialReasoningAgent(framework, api_key="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", model="gpt-4")
        
        # 示例1: 点-点关系
        print("=== 示例1: 点-点关系 ===")
        result = framework.point_point_relation([1, 2], [1, 2])
        print(f"点(1,2)和点(1,2)的关系: {result}")
        
        # 示例2: 点-多边形关系
        print("\n=== 示例2: 点-多边形关系 ===")
        polygon = [[0, 0], [4, 0], [4, 4], [0, 4]]
        result = framework.point_polygon_relation([2, 2], polygon)
        print(f"点(2,2)和多边形{polygon}的关系: {result}")
        
        # 示例3: 可视化
        print("\n=== 示例3: 可视化 ===")
        entity1 = {"type": "point", "coordinates": [2, 2]}
        entity2 = {"type": "polygon", "coordinates": polygon}
        result = framework.visualize_spatial_relation(entity1, entity2, "Within", "example.png")
        print(result)
        
        # 示例4: LLM工具调用（需要API密钥）
        print("\n=== 示例4: LLM工具调用 ===")
        try:
            llm_result = agent.call_llm_with_tools(
                "判断点(2,2)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系",
                visualize=True
            )
            
            if llm_result["success"]:
                print("LLM工具调用成功！")
                print(f"工具执行结果: {llm_result['tool_result']}")
                if llm_result['visualization']:
                    print(f"可视化结果: {llm_result['visualization']}")
            else:
                print(f"LLM工具调用失败: {llm_result['error']}")
                
        except Exception as e:
            print(f"LLM调用失败，请检查API密钥设置: {e}")
            print("提示: 请设置OPENAI_API_KEY环境变量或传入api_key参数")
        
        # 示例5: 更多LLM调用示例
        print("\n=== 示例5: 更多LLM调用示例 ===")
        test_cases = [
            "判断点(3,3)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系",
            "判断线段[[1,1],[3,3]]和线段[[2,2],[4,4]]的空间关系",
            "判断线段[[1,1],[3,3]]和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系"
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case}")
            try:
                result = agent.call_llm_with_tools(test_case)
                if result["success"]:
                    print(f"结果: {result['tool_result']}")
                else:
                    print(f"失败: {result['error']}")
            except Exception as e:
                print(f"调用失败: {e}")
        
        # 示例6: 演示如何设置API密钥
        print("\n=== 示例6: API密钥设置说明 ===")
        print("要使用LLM功能，请按以下方式之一设置API密钥：")
        print("1. 环境变量: export OPENAI_API_KEY='your-api-key-here'")
        print("2. 代码中设置: agent = LLMSpatialReasoningAgent(framework, api_key='your-api-key-here')")
        print("3. 或者使用模拟LLM响应进行测试")
        
        # 示例7: 模拟LLM响应测试（不需要API密钥）
        print("\n=== 示例7: 模拟LLM响应测试 ===")
        mock_llm_response = """TOOL_CALL: point_polygon_relation
PARAMETERS: {"point": [3, 3], "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}
END_TOOL_CALL"""
        
        try:
            tool_result = agent.execute_llm_request("判断点(3,3)和多边形[[0,0],[4,0],[4,4],[0,4]]的空间关系", mock_llm_response)
            print(f"模拟测试结果: {tool_result}")
        except Exception as e:
            print(f"模拟测试失败: {e}")
        
        print("\n使用方法:")
        print("python spatial_reasoning_framework.py <jsonl_file> [max_tests] [api_key]")
        print("例如: python spatial_reasoning_framework.py test_data.jsonl 10 your-api-key") 