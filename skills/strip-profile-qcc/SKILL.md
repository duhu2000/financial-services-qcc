---
name: strip-profile-qcc
description: >
  企业画像速览 SKILL · 企查查 MCP V2.0 增强版。
  PE / VC / FA 在 LP 推介前、项目初步筛选、内部立项汇报等场景的轻量尽调工具。3 分钟生成一页纸企业画像，整合工商登记、核心风险信号、知识产权资产、V2.0 主体延续性、核心管理层概要五大板块，以结构化方式呈现企业基本面。

  核心能力：
  - 基础工商核验 + 主体延续性（V2.0 新能力，qcc-history 治理稳定性回溯）
  - 核心风险标签：1 页内呈现失信 / 限高 / 被执行 / 股权冻结等关键风险信号
  - 知识产权资产概览 + 知产出质（V2.0 新工具）
  - 核心管理层概要：实控人 + 法代 + 核心高管姓名与简要画像
  - 融资与经营活跃度：融资记录 + 招聘活跃度 + 荣誉信息

  适用场景：LP 推介前 5 分钟了解目标公司全貌 / 项目初步筛选 / 内部立项汇报 / 投资分析师快速背调 / 投资经理每日浏览池。

  使用方式：/strip-profile-qcc 企业名称 [--depth quick|standard] [--format md|docx|pptx]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP V2.0)
  version: "2.0"
  plugin-commands: "/strip-profile-qcc"
  mcp-integrations: "qcc-company, qcc-risk, qcc-ipr, qcc-history, qcc-executive, qcc-operation"
  industry: "Financial Services - PE/VC/FA"
---

# 企业画像速览 · 企查查 MCP V2.0 增强版

## SKILL 定位

本 SKILL 服务于投资类场景的"快速筛查"——在 IC Memo 之前、DD 之前，投资团队常常需要对大量项目做"5 分钟扫一眼"式筛查。企业画像速览就是这种场景的标准工具：输入公司名，5 分钟内输出一张结构化的"公司身份卡"，让投资经理快速判断"这家公司是否值得进入 DD 阶段"。

V2.0 相对 V1.0 的升级在两个方面：
- **主体延续性维度**（qcc-history）—— 画像表上增加"治理稳定性"一行，识别"频繁变更"的高风险企业
- **核心管理层概要**（qcc-executive）—— 画像表上增加"创始人速览"一行，3 秒内判断实控人是否清洁

## MCP 依赖与配置

必选：
- `qcc-company`（企业基座）—— 工商基础 + 股东 + 实控人
- `qcc-risk`（风控大脑）—— 核心风险标签

强烈建议：
- `qcc-history`（历史存档）—— 主体延续性
- `qcc-executive`（人员画像）—— 核心管理层快扫

可选：
- `qcc-ipr`（知产引擎）—— IP 资产概览
- `qcc-operation`（经营罗盘）—— 融资、荣誉、招聘活跃度

## 通用执行原则

**第一，轻量快速是第一目标。** 画像速览不是 IC Memo。要在 1-2 页（500-800 字）内让读者快速抓到"主体真实性 + 核心风险 + 关键人物 + IP 数量 + 融资轮次"五项核心信息，**不做深度推演**。

**第二，信息密度优先于文字包装。** 推荐用表格而非段落。每个指标一行，最多一句话解读。

**第三，主体延续性是新加入的结构化维度。** 治理稳定 / 不稳定 / 高度不稳定三档标签，不做深入分析——如读者想深入，进入下一层的 IC Memo / KYB。

**第四，创始人画像做"轻扫"而非"深扫"。** 只看 4 项核心红线（失信 / 限高 / 被执行 / 限出境）是否触发，不做完整 18 维扫描。

**第五，明确告知"可用于初步筛查不可用于投资决策"。** 画像速览定位决定了其深度——如进入正式投资决策阶段，必须升级到 IC Memo + KYB + 专项 DD 工作。

## 工作流

### 维度一：基础工商 × 主体延续性（V2.0 加强）

工具链：
- `mcp__qcc-company__get_company_registration_info`
- `mcp__qcc-company__get_shareholder_info`
- `mcp__qcc-company__get_actual_controller`
- `mcp__qcc-history__get_historical_legal_rep` / `get_historical_registration`

**速览输出**：
- 全称 + USCC
- 成立日期 + 注册资本（实缴）
- 登记状态
- 所属地区 + 行业
- 实控人 + 持股比例
- **治理稳定性标签**（V2.0 新）：稳定 / 不稳定 / 高度不稳定

### 维度二：核心风险标签

工具链：
- `mcp__qcc-risk__get_dishonest_info` / `get_judgment_debtor_info` / `get_high_consumption_restriction` / `get_equity_freeze` / `get_business_exception` / `get_tax_arrears_notice` / `get_administrative_penalty`

**速览输出 6 色标签**：
- 🟢 失信 0
- 🟢 被执行 0
- 🟢 限高 0
- 🟢 股权冻结 0
- 🟢 经营异常 0
- 🟡 行政处罚 N（有则列数量）

### 维度三：知识产权资产概览

工具链：
- `mcp__qcc-ipr__get_patent_info`（总数）
- `mcp__qcc-ipr__get_trademark_info`（总数）
- `mcp__qcc-ipr__get_software_copyright_info`（总数）
- `mcp__qcc-ipr__get_ipr_pledge`（V2.0 新工具，是否有知产出质）

**速览输出**：
- 专利 N 件 / 商标 N 件 / 软著 N 件 / 域名 N 个
- 知产出质：有 / 无（V2.0 新指标）

### 维度四：核心管理层速览（V2.0 新能力）

对实控人 + 法代做 4 项红线快扫：
- `mcp__qcc-executive__get_personnel_dishonest`
- `mcp__qcc-executive__get_personnel_high_consumption_ban`
- `mcp__qcc-executive__get_personnel_judgment_debtor`
- `mcp__qcc-executive__get_personnel_exit_restriction`

**速览输出**：
- 实控人姓名 + 4 项红线扫描结果（全绿 / 有红）
- 法代姓名 + 红线扫描结果
- 如两人非同一人，各扫一遍

### 维度五：融资与经营活跃度

工具链：
- `mcp__qcc-operation__get_financing_records`（融资历史）
- `mcp__qcc-operation__get_recruitment_info`（招聘活跃度）
- `mcp__qcc-operation__get_honor_info`（荣誉）

**速览输出**：
- 最近融资轮次 + 金额 + 时间 + 投资方
- 招聘活跃度（近 3 月职位数）
- 荣誉：高新技术企业 / 专精特新 / 国家级 / 省级 等关键标签

## 画像速览标准模板（一页纸格式）

```
┌─────────────────────────────────────────────────────┐
│  【企业画像速览】目标公司名称                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ▎基础信息                                           │
│    USCC：___  成立：___  注册资本：___               │
│    行业：___  地区：___  登记状态：___               │
│    实控人：___（持股 __%）                           │
│    治理稳定性（V2.0）：🟢 稳定 / 🟡 不稳定 / 🔴 高度不稳定 │
│                                                     │
│  ▎核心风险标签                                       │
│    🟢 失信 0  🟢 被执行 0  🟢 限高 0                │
│    🟢 股权冻结 0  🟢 经营异常 0  🟡 行政处罚 N      │
│                                                     │
│  ▎知识产权（V2.0 + 知产出质）                        │
│    专利 N 件  商标 N 件  软著 N 件                   │
│    知产出质：🟢 无 / 🔴 有                          │
│                                                     │
│  ▎核心管理层速览（V2.0 新）                         │
│    实控人 ___（4 项红线）：🟢 / 🔴                   │
│    法代 ___（4 项红线）：🟢 / 🔴                    │
│                                                     │
│  ▎融资与活跃度                                       │
│    最近融资：__ 轮（__ 万 __ 年 __ 月）             │
│    投资方：___                                       │
│    招聘活跃度：近 3 月 N 个职位                      │
│    荣誉：__                                          │
│                                                     │
│  ▎一句话结论（由 AI 基于上述数据生成）               │
│    "___"                                            │
└─────────────────────────────────────────────────────┘

## 参数

- `--depth <quick|standard>`：quick（默认）仅 4 红线 + 基础工商；standard 涵盖所有维度
- `--format md|docx|pptx`：输出格式，默认 md；pptx 为一页 PPT 速览模板

## 边界与免责

画像速览仅供"初步筛查 / 立项前浏览 / LP 推介前准备"场景。**不得**作为投资决策依据——任何投资决策应基于 IC Memo + KYB + 专项 DD 的完整尽调流程。

---

**SKILL 版本**：v2.0（MCP V2.0 升级版）
**适配 MCP 版本**：146 工具 / 6 Server 全量版
**所需 Server**：qcc-company（必选）、qcc-risk（必选）、qcc-history（建议）、qcc-executive（建议）、qcc-ipr（可选）、qcc-operation（可选）
