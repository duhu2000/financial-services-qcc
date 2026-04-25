---
name: competitor-analysis-qcc
description: >
  竞品对比分析 SKILL · 企查查 MCP V2.0 增强版。
  两家或多家竞争企业的横向对比分析。V2.0 新增双方真实财报 + 历史专利商标两层能力。

  使用方式：/competitor-analysis 企业名称 [--format md|docx|pptx]

license: Apache-2.0
metadata:
  version: "2.0"
  plugin-commands: "/competitor-analysis"
  mcp-integrations: "qcc-company, qcc-risk, qcc-history, qcc-executive, qcc-operation"
---

# 竞品对比分析 · 企查查 MCP V2.0 增强版

## SKILL 定位

两家或多家竞争企业的横向对比分析。V2.0 新增双方真实财报 + 历史专利商标两层能力。

## 工作流维度

1. 基础规模对比（注册资本 / 参保 / 成立年数）
2. **V2.0 新能力：双方财报对比**（get_financial_data —— 营收 / 毛利率 / 资产负债率对比）
3. 融资历史对比（get_financing_records + get_historical_shareholders）
4. **V2.0 新能力：历史专利 / 商标**（qcc-history —— 技术积累曲线对比）
5. 司法风险对比
6. 核心团队对比（创始团队稳定性）

## 评级

领先者 / 追赶者 / 掉队者



## MCP 依赖

- 必选：qcc-company / qcc-risk
- V2.0 强烈建议：qcc-history / qcc-executive / qcc-operation / qcc-ipr（视场景）

## 输出模板

- 章节 1：Decision Pack（评级 + 关键判断 + 推荐 Action）
- 章节 2：数据来源
- 章节 3-7：各维度扫描结果
- 章节 8：V2.0 能力增量说明
- 章节 9：综合评级 × 处置建议

## 参数

- `--format md|docx|pptx`：输出格式，默认 md

## 边界与免责

本 SKILL 基于企查查 MCP V2.0 公开数据生成，不替代专业财务审计 / 律师尽调 / 技术评估。


**SKILL 版本**：v2.0 | **适配 MCP 版本**：146 工具 / 6 Server 全量
