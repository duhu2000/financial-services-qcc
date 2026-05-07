---
name: business-health-scan-qcc
description: >
  经营健康度扫描 SKILL · 企查查 MCP V2.0 增强版。
  企业经营活跃度与健康度的动态跟踪工具，输出"健康 / 稳定 / 衰退 / 危机"四档评级。

  核心能力：
  - **招聘活跃度**（`mcp__qcc-operation__get_recruitment_info`）—— 月度招聘速率 / 高薪岗位密度 / 团队扩张方向
  - **招投标活跃度**（`mcp__qcc-operation__get_bidding_info`）—— 中标频次 / 业务来源结构 / 增长势能
  - **V2.0 真实财务底盘**（`mcp__qcc-company__get_financial_data`）—— 3 年财报 YoY 健康度，营收 / 毛利 / 现金流真实信号
  - **V2.0 历史荣誉追溯**（`mcp__qcc-history__get_historical_honor`）—— 已失效 / 过期荣誉资质识别"虚高包装"
  - 新闻舆情监测（`mcp__qcc-operation__get_news_sentiment`）—— 负面舆情、监管动态、行业事件
  - 参保人数 YoY 趋势 + 历史从业人数对比 —— 人员收缩信号

  适用场景：投前快速筛查 / 投后被投企业持续健康度跟踪 / 客户经营活跃度复核 / 衰退预警监测。

  使用方式：/business-health-scan 企业名称 [--format md|docx|pptx]

license: Apache-2.0
metadata:
  version: "2.0"
  plugin-commands: "/business-health-scan"
  mcp-integrations: "qcc-company, qcc-risk, qcc-history, qcc-executive, qcc-operation"
---

# 经营健康度扫描 · 企查查 MCP V2.0 增强版

## SKILL 定位

企业经营活跃度与健康度的动态跟踪工具。V2.0 新增真实财务底盘 + 历史荣誉两层能力。

## 工作流维度

1. 招聘活跃度（qcc-operation get_recruitment_info）
2. 招投标活跃度（get_bidding_info）
3. **V2.0 新能力：真实财务数据**（get_financial_data —— 3 年财报做 YoY 健康度）
4. **V2.0 新能力：历史荣誉追溯**（qcc-history get_historical_honor —— 已失效的过期荣誉 / 资质）
5. 新闻舆情（get_news_sentiment）
6. 参保人数 YoY 趋势

## 评级

健康 / 稳定 / 衰退 / 危机



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
