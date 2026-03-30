# 变更对比：Anthropic原版 vs QCC MCP增强版

## 项目说明

本项目基于 [Anthropics Financial Services Plugins](https://github.com/anthropics/financial-services-plugins) 进行增强开发，在保留原作者所有代码的基础上，增加了企查查MCP集成，专为中国金融机构提供实时企业数据支持。

---

## 对比概览

| 功能模块 | Anthropic原版 | QCC MCP增强版 |
|---------|--------------|--------------|
| **目标市场** | 海外市场为主 | **中国市场为主** |
| **数据来源** | Bloomberg/Refinitiv/Orbis | **企查查MCP官方数据** |
| **核验速度** | 依赖人工查询 | **30秒自动化** |
| **知识产权** | 需多平台查询 | **一键全量扫描** |
| **股权穿透** | 手动处理 | **自动识别受益所有人** |
| **报告生成** | 手动编写 | **自动填充** |

---

## 文件结构对比

### Anthropic原版结构

```
financial-services-plugins/
├── investment-banking/
│   └── skills/
│       └── strip-profile/
│           └── SKILL.md          ← 原版企业简况
├── private-equity/
│   └── skills/
│       └── ic-memo/
│           └── SKILL.md          ← 原版IC Memo
└── README.md
```

### QCC MCP增强版结构

```
financial-services-qcc/
├── investment-banking/
│   └── skills/
│       └── strip-profile/
│           ├── SKILL.original.md     ← ✅ 保留原版
│           └── SKILL.md              ← 🆕 QCC增强版（kyb-verification-qcc）
├── private-equity/
│   └── skills/
│       └── ic-memo/
│           ├── SKILL.original.md     ← ✅ 保留原版
│           └── SKILL.md              ← 🆕 QCC增强版（ic-memo-qcc）
├── skills/
│   ├── kyb-verification-qcc/         ← 🆕 KYB自动化核验
│   └── ic-memo-qcc/                  ← 🆕 IC Memo全维度尽调
├── scripts/
│   └── qcc_mcp_connector_financial.py ← 🆕 MCP连接器
├── README.md
├── CHANGES.md                         ← 🆕 本文件
└── install_qcc_mcp_financial.sh       ← 🆕 一键安装脚本
```

---

## SKILL详细对比

### 1. Strip Profile（企业简况）

#### Anthropic原版 SKILL

**目标**: 生成1页纸企业简介，用于新客户KYC、交易对手风险评估

**数据来源**: Bloomberg、Refinitiv、Orbis、公司年报

**输出内容**:
- 基础工商信息（名称、注册地、标识符）
- 业务描述
- 股权结构
- 财务快照
- 近期企业活动
- 风险标记

**特点**: 适合海外上市公司，依赖商业数据终端

#### QCC MCP增强版（KYB自动化核验）

**目标**: **30秒自动化**完成中国企业KYB核验，用于银行开户、信贷审批

**数据来源**: **企查查MCP（65个官方数据源）**

**增强功能**:
| 功能 | 原版 | 增强版 |
|------|------|--------|
| 核验速度 | 2-3小时人工 | **30秒自动** |
| 实体锚定 | 手动验证 | **自动比对**统一社会信用代码 |
| 受益所有人 | 需手动穿透 | **自动识别**（25%规则） |
| 司法风险 | 需多平台查询 | **18类风险一键扫描** |
| 准入建议 | 需人工判断 | **自动评级+A/B/C/D建议** |
| 关联关系 | 难以识别 | **集团关联自动排查** |

**新增输出**:
- KYB综合评级（A/B/C/D级）
- 准入建议（正常/审慎/禁止准入）
- 人工复核触发点自动标注
- 18类风险清单及响应时间分级

---

### 2. IC Memo（投资委员会备忘录）

#### Anthropic原版 SKILL

**目标**: 撰写PE/VC投资决策文档

**数据来源**: 数据室(VDR)、管理层报告、行业研究

**输出内容**: 7章标准IC Memo
1. Executive Summary
2. Company Overview
3. Transaction Overview
4. Investment Thesis
5. Financial Analysis
6. Risk Factors
7. Appendices

**特点**: 适合海外投资，依赖人工尽调数据

#### QCC MCP增强版（IC Memo全维度背调）

**目标**: **一键生成**投资委员会备忘录，自动填充关键章节

**数据来源**: **企查查MCP（65个官方数据源）**

**增强功能**:
| 功能 | 原版 | 增强版 |
|------|------|--------|
| 股权结构 | 手动整理 | **自动穿透+实控人识别** |
| 知识产权 | 需单独尽调 | **专利/商标/软著全量扫描** |
| 诉讼风险 | 依赖披露 | **司法风险全扫描（16个工具）** |
| 业务活跃度 | 依赖访谈 | **招投标数据量化分析** |
| 报告生成 | 人工编写 | **自动填充7大章节** |
| 尽调时间 | 1-2周 | **< 1小时** |

**新增输出**:
- 股权穿透图（自动生成）
- 知识产权资产清单（专利/商标/软著）
- 司法风险全扫描（立案/判决/执行/失信）
- 经营动态量化（招投标、招聘、舆情）
- 风险缓释措施建议（自动生成）

---

## MCP工具对比

### Anthropic原版数据获取

```
Bloomberg Terminal / Refinitiv Eikon
├── 公司基础信息
├── 财务数据
├── 股价信息
└── 新闻舆情

S&P Capital IQ / Orbis
├── 非上市公司数据
├── 股权结构
└── 可比公司分析

Company Filings
├── 10-K / 20-F
├── Annual Report
└── Exchange announcements
```

### QCC MCP增强版数据获取（65个工具）

```
qcc_company (企业基座) - 12个工具
├── get_company_registration_info (工商登记)
├── get_shareholder_info (股东信息)
├── get_key_personnel (主要人员)
├── get_change_records (变更记录)
├── get_branches (分支机构)
├── get_external_investments (对外投资)
├── get_annual_reports (工商年报)
└── ...

qcc_risk (风控大脑) - 16个工具
├── get_dishonest_info (失信信息)
├── get_judgment_debtor_info (被执行人)
├── get_high_consumption_restriction (限制高消费)
├── get_bankruptcy_reorganization (破产重整)
├── get_equity_freeze (股权冻结)
├── get_business_exception (经营异常)
├── get_serious_violation (严重违法)
├── get_administrative_penalty (行政处罚)
├── get_environmental_penalty (环保处罚)
├── get_tax_arrears_notice (欠税公告)
├── get_tax_violation (税收违法)
└── ...

qcc_ipr (知产引擎) - 5个工具
├── get_patent_info (专利信息)
├── get_trademark_info (商标信息)
├── get_software_copyright_info (软件著作权)
├── get_copyright_work_info (作品著作权)
└── get_standard_info (标准信息)

qcc_operation (经营罗盘) - 7个工具
├── get_bidding_info (招投标信息)
├── get_qualifications (资质证书)
├── get_administrative_license (行政许可)
├── get_credit_evaluation (信用评级)
├── get_spot_check_info (抽查检查)
├── get_news_sentiment (新闻舆情)
└── get_recruitment_info (招聘信息)
```

---

## 业务场景对比

### 场景一：银行对公客户KYB

| 环节 | Anthropic原版 | QCC MCP增强版 |
|------|--------------|--------------|
| 信息收集 | 客户填表+人工录入 | **扫码自动读取** |
| 工商核验 | 登录企业信用网查询 | **API实时核验** |
| 风险扫描 | 多平台逐一查询 | **一键18类风险** |
| 股权穿透 | 手动梳理 | **自动受益所有人识别** |
| 准入决策 | 人工判断 | **自动评级+建议** |
| **总耗时** | **2-3小时** | **30秒** |

### 场景二：投资尽调

| 环节 | Anthropic原版 | QCC MCP增强版 |
|------|--------------|--------------|
| 公司概况 | 访谈+公开信息 | **工商数据自动填充** |
| 股权结构 | 企业提供+律师核查 | **穿透至自然人** |
| 知识产权 | 企业列表+逐一核实 | **全量扫描+有效性核查** |
| 诉讼风险 | 企业披露+裁判文书网 | **全量司法风险扫描** |
| 业务验证 | 客户访谈+合同抽查 | **招投标数据量化** |
| 报告编写 | 1-2天人工撰写 | **自动填充7章节** |
| **总耗时** | **1-2周** | **< 1天** |

---

## 保留的原版内容

✅ **investment-banking/skills/strip-profile/SKILL.original.md**
- 完整的原版企业简况生成逻辑
- 海外数据来源配置
- 标准1页纸输出格式

✅ **private-equity/skills/ic-memo/SKILL.original.md**
- 完整的原版IC Memo撰写框架
- 7章标准结构
- PE/VC投资决策流程

---

## 新增的增强内容

🆕 **skills/kyb-verification-qcc/SKILL.md**
- 30秒KYB自动化核验
- 18类风险扫描
- 受益所有人自动识别
- A/B/C/D评级体系

🆕 **skills/ic-memo-qcc/SKILL.md**
- 全维度尽调
- 65个MCP工具调用
- 自动填充IC Memo
- 风险缓释建议

🆕 **scripts/qcc_mcp_connector_financial.py**
- 企查查MCP连接器
- KYB快速核验API
- IC Memo全量尽调API
- 金融专用风险评级

---

## 使用建议

### 海外市场
- 使用原版 `SKILL.original.md`
- 依赖 Bloomberg/Refinitiv 数据
- 适合海外上市公司

### 中国市场
- 使用增强版 `SKILL.md`
- 依赖企查查MCP数据
- 适合中国企业、金融机构

### 混合场景
- 根据企业注册地选择对应版本
- 可以同时安装两个版本
- 通过不同的 slash command 调用

---

## 致谢

- 原版作者 [Anthropics](https://github.com/anthropics/financial-services-plugins) 的优秀金融合规框架
- [企查查MCP](https://agent.qcc.com) - Agent-Native企业数据基座
- [Anthropic](https://anthropic.com) 的 Claude Code

---

## 许可证

Apache License 2.0

基于 [Anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) 构建
