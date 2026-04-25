---
name: funding-history-qcc
description: >
  融资历史追踪 SKILL · 企查查 MCP V2.0 增强版。
  企业完整融资路径追溯工具。V2.0 新增历史股东进退轨迹 + 历史对外投资两层能力。

  使用方式：/funding-history 企业名称 [--format md|docx|pptx]

license: Apache-2.0
metadata:
  version: "2.0"
  plugin-commands: "/funding-history"
  mcp-integrations: "qcc-company, qcc-risk, qcc-history, qcc-executive, qcc-operation"
---

# 融资历史追踪 · 企查查 MCP V2.0 增强版

## SKILL 定位

企业完整融资路径追溯工具。V2.0 新增历史股东进退轨迹 + 历史对外投资两层能力。

## 工作流维度

1. 融资轮次清单（qcc-operation get_financing_records）
2. **V2.0 新能力：历史股东变迁**（qcc-history get_historical_shareholders —— 投资方的进退时间轴）
3. 历史对外投资（get_historical_investments —— 企业自己对外投资的退出 / 注销轨迹）
4. 当前股东结构快照（get_shareholder_info）
5. 历轮估值推算（基于认缴出资额时间轴）
6. 估值曲线合理性判定

## 评级

健康扩张 / 稳定融资 / 估值倒挂 / 融资枯竭



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
