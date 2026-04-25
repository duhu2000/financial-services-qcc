"""
qcc-history-skill · V1.2 schema-driven 框架
=============================================
事故防御机制：
- USCC 校验位（GB 32100-2015）
- pydantic schema 强制 count ≡ rows
- evidence 锚点（每字段必须可回溯到 MCP 工具调用 + JSONPath + 时间戳）
- 跨章节一致性自检
- 算法生成的数字字段（年度分布、级别分布等），禁止手写

主入口：build_report_v1_2.py
"""

__version__ = "1.2.0"
