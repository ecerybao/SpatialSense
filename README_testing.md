# 空间关系判断框架测试指南

## 概述

这个测试框架用于评估基于LLM的空间关系判断系统的性能。它能够：
- 从JSONL文件中加载测试数据
- 使用LLM进行空间关系判断
- 与预期结果进行比较
- 统计准确率并生成详细报告

## 文件结构

```
├── spatial_reasoning_framework.py  # 主框架文件
├── test_spatial_reasoning.py       # 测试脚本
├── README_testing.md               # 本说明文档
└── sample_test_data.jsonl          # 示例测试数据
```

## 安装依赖

```bash
pip install openai shapely matplotlib numpy
```

## 使用方法

### 1. 基本测试

```bash
# 使用示例数据测试
python test_spatial_reasoning.py

# 使用自定义数据测试
python test_spatial_reasoning.py your_data.jsonl

# 限制测试数量
python test_spatial_reasoning.py your_data.jsonl 10

# 指定API密钥
python test_spatial_reasoning.py your_data.jsonl 10 your-api-key
```

### 2. 直接使用主框架

```bash
# 使用示例数据
python spatial_reasoning_framework.py

# 使用自定义数据
python spatial_reasoning_framework.py your_data.jsonl 10 your-api-key
```

## 数据格式

测试数据应为JSONL格式，每行包含一个JSON对象：

```json
{
  "input": "Point A is at (-81, -87). Point B is at (-81, -87). What is the spatial relation between Point A and Point B?",
  "output": "Step 1: Call calculate_distance tool with points (-81, -87) and (-81, -87)\n→ Tool returns: 0.00\nStep 2: Since distance = 0, the spatial relation is 'Equals'."
}
```

### 输入格式

输入应为英文描述，包含几何对象的坐标信息，例如：
- 点-点关系：`"Point A is at (x1, y1). Point B is at (x2, y2). What is the spatial relation between Point A and Point B?"`
- 点-多边形关系：`"Point A is at (x, y). Polygon P has vertices [(x1,y1), (x2,y2), ...]. What is the spatial relation between Point A and Polygon P?"`
- 线-多边形关系：`"Given line L with endpoints [(x1,y1), (x2,y2)] and polygon P with vertices [(x1,y1), (x2,y2), ...], determine their spatial relation."`

### 输出格式

输出应包含详细的推理步骤，并在最后给出空间关系结果，例如：
- `"Spatial relation: 'Equals'"`
- `"Spatial relation: 'Disjoint'"`
- `"Spatial relation: 'Within'"`

## 支持的空间关系

框架支持以下空间关系类型：
- `Equals`: 相等
- `Contains`: 包含
- `Within`: 被包含
- `Overlaps`: 重叠
- `Crosses`: 交叉
- `Touches`: 接触
- `Disjoint`: 分离

## 测试结果

测试完成后会生成以下信息：
- 总数据量
- 成功处理数量
- 处理失败数量
- 正确判断数量
- 错误判断数量
- 准确率

结果会保存到 `test_results.json` 文件中。

## 示例输出

```
==================================================
批量测试结果
==================================================
总数据量: 100
成功处理: 95
处理失败: 5
正确判断: 87
错误判断: 8
准确率: 91.58%

详细结果:
✓ 第1条: 预期 Equals, 实际 Equals
✓ 第2条: 预期 Disjoint, 实际 Disjoint
✗ 第3条: 预期 Within, 实际 Disjoint
...
```

## 故障排除

### 1. API密钥问题
```
错误: OpenAI API密钥未设置，无法调用LLM
解决: 设置环境变量 OPENAI_API_KEY 或在代码中传入 api_key 参数
```

### 2. 数据格式问题
```
错误: 无法从输出中提取预期关系
解决: 检查输出格式，确保包含 "Spatial relation: 'XXX'" 格式的结果
```

### 3. 工具调用失败
```
错误: 解析工具调用失败
解决: 检查LLM响应格式，确保符合工具调用规范
```

## 高级配置

### 自定义API设置

```python
from spatial_reasoning_framework import LLMSpatialReasoningAgent, SpatialReasoningFramework

# 创建代理时指定模型和API密钥
framework = SpatialReasoningFramework()
agent = LLMSpatialReasoningAgent(
    framework, 
    api_key="your-api-key",
    model="gpt-4"  # 或 "gpt-3.5-turbo"
)
```

### 批量测试配置

```python
from spatial_reasoning_framework import run_comprehensive_test

# 运行自定义测试
results = run_comprehensive_test(
    jsonl_file_path="your_data.jsonl",
    api_key="your-api-key",
    max_tests=50  # 限制测试数量
)
```

## 性能优化

1. **限制测试数量**: 使用 `max_tests` 参数限制测试数量
2. **使用更快的模型**: 对于大规模测试，考虑使用 `gpt-3.5-turbo`
3. **并行处理**: 对于大量数据，可以考虑添加并行处理功能

## 扩展功能

### 添加新的空间关系类型

在 `SpatialReasoningFramework` 类中添加新的关系判断方法：

```python
def new_spatial_relation(self, params):
    """新的空间关系判断方法"""
    # 实现逻辑
    return "NewRelation"
```

### 自定义结果提取

修改 `extract_expected_relation` 函数以支持新的输出格式：

```python
def extract_expected_relation(output_text: str) -> str:
    # 添加新的模式匹配
    patterns = [
        # 现有模式...
        r"New pattern: ['\"]([^'\"]+)['\"]"
    ]
    # 实现逻辑...
```

## 联系信息

如有问题或建议，请通过以下方式联系：
- 提交Issue到项目仓库
- 发送邮件到项目维护者

## 许可证

本项目采用 MIT 许可证。 