import json
import math
from typing import Dict, List, Tuple, Any, Optional, Union
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

class SpatialRelation(Enum):
    """空间关系枚举"""
    EQUALS = "Equals"
    CONTAINS = "Contains"
    WITHIN = "Within"
    OVERLAPS = "Overlaps"
    CROSSES = "Crosses"
    TOUCHES = "Touches"
    DISJOINT = "Disjoint"

class DE9IMMatrix:
    """DE-9IM矩阵实现"""
    
    def __init__(self, matrix: List[List[int]]):
        """
        初始化DE-9IM矩阵
        matrix: 3x3矩阵，表示两个几何对象的交集维度
        """
        self.matrix = matrix
    
    def __str__(self):
        return f"DE-9IM Matrix:\n{self.matrix[0]}\n{self.matrix[1]}\n{self.matrix[2]}"
    
    def get_relation(self) -> str:
        """根据DE-9IM矩阵确定空间关系"""
        # 简化的关系判断逻辑
        interior_interior = self.matrix[0][0]
        interior_boundary = self.matrix[0][1]
        interior_exterior = self.matrix[0][2]
        boundary_interior = self.matrix[1][0]
        boundary_boundary = self.matrix[1][1]
        boundary_exterior = self.matrix[1][2]
        exterior_interior = self.matrix[2][0]
        exterior_boundary = self.matrix[2][1]
        exterior_exterior = self.matrix[2][2]
        
        # 根据DE-9IM规则判断关系
        if interior_interior >= 0 and boundary_boundary >= 0 and exterior_exterior >= 0:
            return SpatialRelation.EQUALS.value
        elif interior_interior >= 0 and boundary_boundary >= 0 and exterior_exterior == -1:
            return SpatialRelation.CONTAINS.value
        elif interior_interior >= 0 and boundary_boundary >= 0 and exterior_interior == -1:
            return SpatialRelation.WITHIN.value
        elif interior_interior >= 0 and boundary_boundary >= 0:
            return SpatialRelation.OVERLAPS.value
        elif interior_interior == -1 and boundary_boundary >= 0:
            return SpatialRelation.TOUCHES.value
        elif interior_interior == -1 and boundary_boundary == -1:
            return SpatialRelation.DISJOINT.value
        else:
            return SpatialRelation.CROSSES.value

class AdvancedSpatialReasoningFramework:
    """
    高级空间推理框架，基于DE-9IM模型
    支持精确的空间关系判断和可视化
    """
    
    def __init__(self):
        self.tools = {
            "calculate_de9im_matrix": self.calculate_de9im_matrix,
            "determine_spatial_relation": self.determine_spatial_relation,
            "point_point_analysis": self.point_point_analysis,
            "point_line_analysis": self.point_line_analysis,
            "point_polygon_analysis": self.point_polygon_analysis,
            "line_line_analysis": self.line_line_analysis,
            "line_polygon_analysis": self.line_polygon_analysis,
            "polygon_polygon_analysis": self.polygon_polygon_analysis,
            "visualize_with_de9im": self.visualize_with_de9im,
            "batch_spatial_analysis": self.batch_spatial_analysis,
            "get_spatial_statistics": self.get_spatial_statistics
        }
    
    def calculate_de9im_matrix(self, geom1: Dict, geom2: Dict) -> Dict:
        """
        计算两个几何对象的DE-9IM矩阵
        
        Args:
            geom1: 第一个几何对象 {'type': 'point/line/polygon', 'coordinates': [...]}
            geom2: 第二个几何对象 {'type': 'point/line/polygon', 'coordinates': [...]}
        
        Returns:
            DE-9IM矩阵和关系信息
        """
        # 转换为Shapely对象
        shape1 = self._dict_to_shapely(geom1)
        shape2 = self._dict_to_shapely(geom2)
        
        # 计算DE-9IM矩阵
        matrix = self._compute_de9im_matrix(shape1, shape2)
        de9im = DE9IMMatrix(matrix)
        relation = de9im.get_relation()
        
        return {
            "de9im_matrix": matrix,
            "spatial_relation": relation,
            "matrix_visualization": str(de9im)
        }
    
    def _dict_to_shapely(self, geom_dict: Dict):
        """将字典格式的几何对象转换为Shapely对象"""
        geom_type = geom_dict['type']
        coords = geom_dict['coordinates']
        
        if geom_type == 'point':
            return Point(coords[0], coords[1])
        elif geom_type == 'line':
            return LineString(coords)
        elif geom_type == 'polygon':
            return Polygon(coords)
        else:
            raise ValueError(f"不支持的几何类型: {geom_type}")
    
    def _compute_de9im_matrix(self, shape1, shape2) -> List[List[int]]:
        """计算DE-9IM矩阵"""
        matrix = []
        
        # 获取几何对象的内部、边界和外部
        interior1 = shape1.interior if hasattr(shape1, 'interior') else shape1
        boundary1 = shape1.boundary
        exterior1 = shape1.exterior if hasattr(shape1, 'exterior') else None
        
        interior2 = shape2.interior if hasattr(shape2, 'interior') else shape2
        boundary2 = shape2.boundary
        exterior2 = shape2.exterior if hasattr(shape2, 'exterior') else None
        
        # 计算交集维度
        for i, part1 in enumerate([interior1, boundary1, exterior1]):
            row = []
            for j, part2 in enumerate([interior2, boundary2, exterior2]):
                if part1 is None or part2 is None:
                    row.append(-1)
                else:
                    intersection = part1.intersection(part2)
                    if intersection.is_empty:
                        row.append(-1)
                    else:
                        row.append(intersection.dimension)
            matrix.append(row)
        
        return matrix
    
    def determine_spatial_relation(self, geom1: Dict, geom2: Dict) -> Dict:
        """
        确定两个几何对象之间的空间关系
        
        Args:
            geom1: 第一个几何对象
            geom2: 第二个几何对象
        
        Returns:
            空间关系分析结果
        """
        # 根据几何类型选择合适的分析方法
        type1, type2 = geom1['type'], geom2['type']
        
        if type1 == 'point' and type2 == 'point':
            return self.point_point_analysis(geom1, geom2)
        elif type1 == 'point' and type2 == 'line':
            return self.point_line_analysis(geom1, geom2)
        elif type1 == 'point' and type2 == 'polygon':
            return self.point_polygon_analysis(geom1, geom2)
        elif type1 == 'line' and type2 == 'line':
            return self.line_line_analysis(geom1, geom2)
        elif type1 == 'line' and type2 == 'polygon':
            return self.line_polygon_analysis(geom1, geom2)
        elif type1 == 'polygon' and type2 == 'polygon':
            return self.polygon_polygon_analysis(geom1, geom2)
        else:
            # 交换顺序再试
            if type2 == 'point' and type1 == 'line':
                return self.point_line_analysis(geom2, geom1)
            elif type2 == 'point' and type1 == 'polygon':
                return self.point_polygon_analysis(geom2, geom1)
            elif type2 == 'line' and type1 == 'polygon':
                return self.line_polygon_analysis(geom2, geom1)
            else:
                raise ValueError(f"不支持的关系类型: {type1} - {type2}")
    
    def point_point_analysis(self, point1: Dict, point2: Dict) -> Dict:
        """点-点关系分析"""
        p1 = Point(point1['coordinates'][0], point1['coordinates'][1])
        p2 = Point(point2['coordinates'][0], point2['coordinates'][1])
        
        distance = p1.distance(p2)
        relation = "Equals" if distance < 1e-10 else "Disjoint"
        
        return {
            "relation": relation,
            "distance": distance,
            "analysis": f"点{point1['coordinates']}和点{point2['coordinates']}的距离为{distance:.6f}",
            "de9im_analysis": self.calculate_de9im_matrix(point1, point2)
        }
    
    def point_line_analysis(self, point: Dict, line: Dict) -> Dict:
        """点-线关系分析"""
        p = Point(point['coordinates'][0], point['coordinates'][1])
        l = LineString(line['coordinates'])
        
        distance = p.distance(l)
        
        if distance < 1e-10:
            relation = "Touches"
        elif p.within(l):
            relation = "Within"
        else:
            relation = "Disjoint"
        
        return {
            "relation": relation,
            "distance_to_line": distance,
            "analysis": f"点{point['coordinates']}到线段{line['coordinates']}的距离为{distance:.6f}",
            "de9im_analysis": self.calculate_de9im_matrix(point, line)
        }
    
    def point_polygon_analysis(self, point: Dict, polygon: Dict) -> Dict:
        """点-多边形关系分析"""
        p = Point(point['coordinates'][0], point['coordinates'][1])
        poly = Polygon(polygon['coordinates'])
        
        if p.within(poly):
            relation = "Within"
        elif p.touches(poly):
            relation = "Touches"
        else:
            relation = "Disjoint"
        
        distance = p.distance(poly)
        
        return {
            "relation": relation,
            "distance_to_polygon": distance,
            "analysis": f"点{point['coordinates']}到多边形{polygon['coordinates']}的距离为{distance:.6f}",
            "de9im_analysis": self.calculate_de9im_matrix(point, polygon)
        }
    
    def line_line_analysis(self, line1: Dict, line2: Dict) -> Dict:
        """线-线关系分析"""
        l1 = LineString(line1['coordinates'])
        l2 = LineString(line2['coordinates'])
        
        if l1.equals(l2):
            relation = "Equals"
        elif l1.contains(l2):
            relation = "Contains"
        elif l1.within(l2):
            relation = "Within"
        elif l1.overlaps(l2):
            relation = "Overlaps"
        elif l1.crosses(l2):
            relation = "Crosses"
        elif l1.touches(l2):
            relation = "Touches"
        else:
            relation = "Disjoint"
        
        intersection = l1.intersection(l2)
        
        return {
            "relation": relation,
            "intersection": str(intersection) if not intersection.is_empty else "无交点",
            "analysis": f"线段{line1['coordinates']}和线段{line2['coordinates']}的关系为{relation}",
            "de9im_analysis": self.calculate_de9im_matrix(line1, line2)
        }
    
    def line_polygon_analysis(self, line: Dict, polygon: Dict) -> Dict:
        """线-多边形关系分析"""
        l = LineString(line['coordinates'])
        poly = Polygon(polygon['coordinates'])
        
        if l.within(poly):
            relation = "Within"
        elif l.crosses(poly):
            relation = "Crosses"
        elif l.touches(poly):
            relation = "Touches"
        else:
            relation = "Disjoint"
        
        intersection = l.intersection(poly)
        
        return {
            "relation": relation,
            "intersection": str(intersection) if not intersection.is_empty else "无交点",
            "analysis": f"线段{line['coordinates']}和多边形{polygon['coordinates']}的关系为{relation}",
            "de9im_analysis": self.calculate_de9im_matrix(line, polygon)
        }
    
    def polygon_polygon_analysis(self, polygon1: Dict, polygon2: Dict) -> Dict:
        """多边形-多边形关系分析"""
        poly1 = Polygon(polygon1['coordinates'])
        poly2 = Polygon(polygon2['coordinates'])
        
        if poly1.equals(poly2):
            relation = "Equals"
        elif poly1.contains(poly2):
            relation = "Contains"
        elif poly1.within(poly2):
            relation = "Within"
        elif poly1.overlaps(poly2):
            relation = "Overlaps"
        else:
            relation = "Disjoint"
        
        intersection = poly1.intersection(poly2)
        union = poly1.union(poly2)
        
        return {
            "relation": relation,
            "intersection_area": intersection.area if not intersection.is_empty else 0,
            "union_area": union.area,
            "analysis": f"多边形{polygon1['coordinates']}和多边形{polygon2['coordinates']}的关系为{relation}",
            "de9im_analysis": self.calculate_de9im_matrix(polygon1, polygon2)
        }
    
    def visualize_with_de9im(self, geom1: Dict, geom2: Dict, relation: str, 
                           de9im_matrix: List[List[int]], filename: str = "spatial_analysis.png") -> str:
        """可视化空间关系并显示DE-9IM矩阵"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 绘制几何对象
        self._plot_geometry_advanced(geom1, ax1, 'blue', 'Entity 1')
        self._plot_geometry_advanced(geom2, ax1, 'red', 'Entity 2')
        
        ax1.set_title(f'Spatial Relation: {relation}', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X', fontsize=12)
        ax1.set_ylabel('Y', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        ax1.set_aspect('equal')
        
        # 绘制DE-9IM矩阵
        self._plot_de9im_matrix(de9im_matrix, ax2)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"分析图片已保存为: {filename}"
    
    def _plot_geometry_advanced(self, entity: Dict, ax, color: str, label: str):
        """高级几何对象绘制"""
        geom_type = entity['type']
        coords = entity['coordinates']
        
        if geom_type == 'point':
            ax.plot(coords[0], coords[1], 'o', color=color, markersize=10, label=label)
            ax.text(coords[0], coords[1], f'({coords[0]},{coords[1]})', 
                   fontsize=8, ha='right', va='bottom')
        elif geom_type == 'line':
            x_coords, y_coords = zip(*coords)
            ax.plot(x_coords, y_coords, color=color, linewidth=3, label=label)
            # 标记端点
            ax.plot(x_coords[0], y_coords[0], 'o', color=color, markersize=6)
            ax.plot(x_coords[-1], y_coords[-1], 's', color=color, markersize=6)
        elif geom_type == 'polygon':
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            x_coords, y_coords = zip(*coords)
            ax.plot(x_coords, y_coords, color=color, linewidth=2, label=label)
            ax.fill(x_coords, y_coords, color=color, alpha=0.3)
            # 标记顶点
            for i, (x, y) in enumerate(zip(x_coords[:-1], y_coords[:-1])):
                ax.text(x, y, f'V{i}', fontsize=8, ha='center', va='center')
    
    def _plot_de9im_matrix(self, matrix: List[List[int]], ax):
        """绘制DE-9IM矩阵"""
        ax.set_title('DE-9IM Matrix', fontsize=14, fontweight='bold')
        
        # 创建表格
        table_data = []
        for i, row in enumerate(matrix):
            table_row = []
            for j, val in enumerate(row):
                if val == -1:
                    table_row.append('∅')
                else:
                    table_row.append(str(val))
            table_data.append(table_row)
        
        # 绘制表格
        table = ax.table(cellText=table_data,
                        rowLabels=['Interior', 'Boundary', 'Exterior'],
                        colLabels=['Interior', 'Boundary', 'Exterior'],
                        cellLoc='center',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # 设置表格样式
        for i in range(4):
            for j in range(4):
                if i == 0 or j == 0:  # 标题行和列
                    table[(i, j)].set_facecolor('#E6E6E6')
                else:
                    table[(i, j)].set_facecolor('#F0F8FF')
        
        ax.axis('off')
    
    def batch_spatial_analysis(self, geometries: List[Dict]) -> Dict:
        """批量空间关系分析"""
        results = []
        relations_count = {}
        
        for i, geom1 in enumerate(geometries):
            for j, geom2 in enumerate(geometries[i+1:], i+1):
                analysis = self.determine_spatial_relation(geom1, geom2)
                results.append({
                    "pair": (i, j),
                    "geometry1": geom1,
                    "geometry2": geom2,
                    "analysis": analysis
                })
                
                relation = analysis['relation']
                relations_count[relation] = relations_count.get(relation, 0) + 1
        
        return {
            "total_pairs": len(results),
            "relations_distribution": relations_count,
            "detailed_results": results
        }
    
    def get_spatial_statistics(self, geometries: List[Dict]) -> Dict:
        """获取空间统计信息"""
        stats = {
            "total_geometries": len(geometries),
            "geometry_types": {},
            "bounding_box": None,
            "centroids": []
        }
        
        all_points = []
        
        for geom in geometries:
            geom_type = geom['type']
            stats['geometry_types'][geom_type] = stats['geometry_types'].get(geom_type, 0) + 1
            
            # 收集所有点用于计算边界框
            if geom_type == 'point':
                all_points.append(geom['coordinates'])
            elif geom_type == 'line':
                all_points.extend(geom['coordinates'])
            elif geom_type == 'polygon':
                all_points.extend(geom['coordinates'])
        
        if all_points:
            x_coords, y_coords = zip(*all_points)
            stats['bounding_box'] = {
                'min_x': min(x_coords),
                'max_x': max(x_coords),
                'min_y': min(y_coords),
                'max_y': max(y_coords)
            }
        
        return stats
    
    def get_tool_descriptions(self) -> Dict[str, Dict]:
        """获取工具描述"""
        return {
            "calculate_de9im_matrix": {
                "description": "计算两个几何对象的DE-9IM矩阵",
                "parameters": {
                    "geom1": {"type": "dict", "description": "第一个几何对象"},
                    "geom2": {"type": "dict", "description": "第二个几何对象"}
                },
                "returns": "DE-9IM矩阵和关系信息"
            },
            "determine_spatial_relation": {
                "description": "确定两个几何对象之间的空间关系",
                "parameters": {
                    "geom1": {"type": "dict", "description": "第一个几何对象"},
                    "geom2": {"type": "dict", "description": "第二个几何对象"}
                },
                "returns": "详细的空间关系分析结果"
            },
            "visualize_with_de9im": {
                "description": "可视化空间关系并显示DE-9IM矩阵",
                "parameters": {
                    "geom1": {"type": "dict", "description": "第一个几何对象"},
                    "geom2": {"type": "dict", "description": "第二个几何对象"},
                    "relation": {"type": "string", "description": "空间关系"},
                    "de9im_matrix": {"type": "list", "description": "DE-9IM矩阵"},
                    "filename": {"type": "string", "description": "保存的文件名"}
                },
                "returns": "图片保存路径"
            },
            "batch_spatial_analysis": {
                "description": "批量分析多个几何对象之间的空间关系",
                "parameters": {
                    "geometries": {"type": "list", "description": "几何对象列表"}
                },
                "returns": "批量分析结果和统计信息"
            }
        }


# 示例使用
if __name__ == "__main__":
    # 创建高级框架
    framework = AdvancedSpatialReasoningFramework()
    
    # 示例1: 点-多边形关系分析
    print("=== 示例1: 点-多边形关系分析 ===")
    point = {"type": "point", "coordinates": [2, 2]}
    polygon = {"type": "polygon", "coordinates": [[0, 0], [4, 0], [4, 4], [0, 4]]}
    
    result = framework.determine_spatial_relation(point, polygon)
    print(f"关系: {result['relation']}")
    print(f"分析: {result['analysis']}")
    print(f"DE-9IM矩阵: {result['de9im_analysis']['de9im_matrix']}")
    
    # 示例2: 可视化
    print("\n=== 示例2: 可视化 ===")
    visualization = framework.visualize_with_de9im(
        point, polygon, result['relation'], 
        result['de9im_analysis']['de9im_matrix'], 
        "advanced_example.png"
    )
    print(visualization)
    
    # 示例3: 批量分析
    print("\n=== 示例3: 批量分析 ===")
    geometries = [
        {"type": "point", "coordinates": [1, 1]},
        {"type": "point", "coordinates": [3, 3]},
        {"type": "line", "coordinates": [[0, 0], [4, 4]]},
        {"type": "polygon", "coordinates": [[0, 0], [4, 0], [4, 4], [0, 4]]}
    ]
    
    batch_result = framework.batch_spatial_analysis(geometries)
    print(f"总对数: {batch_result['total_pairs']}")
    print(f"关系分布: {batch_result['relations_distribution']}")
    
    # 示例4: 统计信息
    print("\n=== 示例4: 统计信息 ===")
    stats = framework.get_spatial_statistics(geometries)
    print(f"几何对象总数: {stats['total_geometries']}")
    print(f"几何类型分布: {stats['geometry_types']}")
    print(f"边界框: {stats['bounding_box']}") 