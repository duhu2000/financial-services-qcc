# 💼 Financial Services QCC MCP Plugins
# 金融机构企查查MCP增强版插件

> **Know Your Business (KYB) Automation & Investment Committee Memorandum (IC Memo) Due Diligence**
>
> **企业客户身份识别自动化核验 & 投资委员会备忘录全维度尽职调查**

> 为银行KYB、投资尽调提供实时中国企业数据支持

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-QCC%20企查查-orange.svg)](https://mcp.qcc.com)
[![Claude](https://img.shields.io/badge/Claude%20Code-Compatible-purple.svg)](https://claude.ai)

> **⚠️ 重要说明：本项目基于 [Anthropics Financial Services Plugins](https://github.com/anthropics/financial-services-plugins) 增强开发**
>
> 在保留原版金融合规框架的基础上，增加了企查查MCP集成，实现中国企业数据的自动化核验。

---

## 📋 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [使用场景](#使用场景)
- [SKILL详解](#skill详解)
- [企查查MCP集成](#企查查mcp集成)
- [项目结构](#项目结构)
- [贡献与反馈](#贡献与反馈)

---

## 功能概述

### 解决的痛点

传统金融机构对公业务面临**尽调效率低、数据盲区大**的问题：
- ❌ 人工查询工商信息耗时2-3小时/户
- ❌ 司法风险、关联关系难以全面排查
- ❌ 知识产权、招投标数据分散多平台
- ❌ 投资尽调报告编写耗时1-2天

### 我们的方案

集成 **企查查MCP**，为金融机构提供：

**方案一：KYB 自动化核验 (Know Your Business Automation)**
- 全称：**Know Your Business**（了解你的企业客户）
- 适用：银行开户、信贷审批、反洗钱合规
- 功能：✅ **30秒自动核验** - 主体合法性+18类风险实时扫描

**方案二：IC Memo 全维度背调 (Investment Committee Memorandum)**
- 全称：**Investment Committee Memorandum**（投资委员会备忘录）
- 适用：PE/VC投资尽调、并购重组、战略投资
- 功能：✅ **一键生成尽调报告** - 工商/股权/知产/诉讼全维度扫描

**通用能力**：
- ✅ **智能决策支持** - 自动评级+准入建议+风险缓释
- ✅ **合规可追溯** - 所有数据来自官方+时间戳记录

---

## 快速开始

### 1分钟快速体验

```bash
# 1. 一键安装
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)

# 2. 配置API Key（从 https://mcp.qcc.com 申请）
export QCC_MCP_API_KEY="your_api_key_here"

# 3. 开始KYB核验
/kyb-verification-qcc 华为技术有限公司

# 4. 或生成IC Memo
/ic-memo-qcc 北京字节跳动科技有限公司
```

---

## 安装指南

### 系统要求

- **操作系统**: macOS / Linux / Windows (WSL)
- **Python**: 3.9+
- **Claude Code**: 最新版本
- **网络**: 可访问 https://mcp.qcc.com

### 安装步骤

#### 步骤1: 申请企查查MCP Key

1. 访问 [企查查MCP官网](https://mcp.qcc.com)
2. 注册企业账号
3. 申请金融服务场景授权
4. 获取API Key

#### 步骤2: 配置环境变量

```bash
export QCC_MCP_API_KEY="your_api_key_here"
```

#### 步骤3: 一键安装

```bash
git clone https://github.com/duhu2000/financial-services-qcc.git
cd financial-services-qcc
bash install_qcc_mcp_financial.sh
```

---

## 使用场景

### 场景一：KYB 自动化核验
**Know Your Business (KYB) Automation**

**适用对象**: 银行对公客户经理、信贷审批员、合规风控、反洗钱专员

**英文全称**: **Know Your Business** — 了解你的企业客户

**中文含义**: 金融机构在为企业客户提供服务前，必须完成的客户身份识别和尽职调查流程，是反洗钱(AML)合规的核心要求

**核心价值**:
- 30秒完成传统2小时的人工尽调
- 自动比对申请材料与官方工商数据
- 识别异常自动触发人工复核

**使用方式**:
```
/kyb-verification-qcc [企业名称] [统一社会信用代码]

示例:
/kyb-verification-qcc 华为技术有限公司
/kyb-verification-qcc 91330100788804XXXX
```

**输出内容**:
```
================================================================
KYB核验报告 - 企查查MCP增强版
================================================================
核验企业:    华为技术有限公司
统一社会信用代码: 9144030019238XXXX
核验状态:    通过
整体风险:    LOW

核验摘要:
  - 企业状态: 存续
  - 法定代表人: [匹配/不匹配]
  - 注册资本: 匹配
  - 风险扫描: 0项CRITICAL, 0项HIGH

准入建议: 正常准入。主体合法存续，无明显风险信号，可按标准流程处理。
================================================================
```

---

### 场景二：IC Memo 全维度背调
**Investment Committee Memorandum (IC Memo) Full-Dimensional Due Diligence**

**适用对象**: PE/VC投资经理、投行分析师、企业战投、FA财务顾问

**英文全称**: **Investment Committee Memorandum** — 投资委员会备忘录

**中文含义**: 投资机构内部决策机构（投资委员会）审议投资项目时使用的正式决策文档，包含投资逻辑、风险评估、回报测算等核心内容，是PE/VC投资流程中的关键文件

**核心价值**:
- 一键生成投资委员会备忘录
- 股权穿透+知识产权+诉讼风险全扫描
- 自动填充IC Memo关键章节

**使用方式**:
```
/ic-memo-qcc [目标企业名称] [--sector 行业]

示例:
/ic-memo-qcc 北京字节跳动科技有限公司 --sector 互联网
/ic-memo-qcc 宁德时代新能源科技股份有限公司 --sector 新能源
```

**输出内容**:
- Chapter 1: 执行摘要（投资建议+核心亮点+关键风险）
- Chapter 2: 公司概况与股权结构（含受益所有人）
- Chapter 3: 知识产权与核心竞争力
- Chapter 4: 法律与合规风险（全量司法风险扫描）
- Chapter 5: 经营与市场分析（招投标+舆情）
- Chapter 6: 财务分析
- Chapter 7: 投资建议与风险提示

---

## SKILL详解

### 1. KYB Verification QCC
**Know Your Business Verification**

| 项目 | 说明 |
|------|------|
| **英文全称** | Know Your Business |
| **中文名称** | 企业客户身份识别与核验 |
| **文件路径** | `skills/kyb-verification-qcc/SKILL.md` |
| **核心用途** | 银行开户、信贷审批、反洗钱合规、企业年检 |

**4阶段工作流**:

| 阶段 | 目标 | MCP调用 | 耗时 |
|------|------|---------|------|
| Phase 1 | 实体锚定 | get_company_registration_info | 5秒 |
| Phase 2 | 股权与受益所有人 | get_shareholder_info + 穿透分析 | 8秒 |
| Phase 3 | 风险扫描 | 7个核心风险工具并行 | 15秒 |
| Phase 4 | 经营健康度 | 资质+信用快速评估 | 2秒 |

**关键风险指标** (18类→7类快检):
```
🔴 CRITICAL (< 4小时响应)
├─ 失信信息 (get_dishonest_info)
├─ 被执行人 (get_judgment_debtor_info)
├─ 限制高消费 (get_high_consumption_restriction)
├─ 破产重整 (get_bankruptcy_reorganization)
└─ 股权冻结 (get_equity_freeze)

🔴 HIGH (< 24小时)
├─ 经营异常 (get_business_exception)
└─ 严重违法 (get_serious_violation)
```

**KYB评级**:
- **A级**: 正常准入
- **B级**: 审慎准入+加强监测
- **C级**: 需人工复核
- **D级**: 禁止准入

---

### 2. IC Memo QCC
**Investment Committee Memorandum**

| 项目 | 说明 |
|------|------|
| **英文全称** | Investment Committee Memorandum |
| **中文名称** | 投资委员会备忘录 / 投资决策文档 |
| **文件路径** | `skills/ic-memo-qcc/SKILL.md` |
| **核心用途** | PE/VC投资尽调、并购重组决策、战略投资审批、投委会汇报 |

**7章节结构**:

```
Chapter 1: 执行摘要
  ├─ 投资建议 (强烈推荐/推荐/谨慎考虑/不建议)
  ├─ 核心亮点 (Top 5)
  └─ 关键风险 (Top 5 + 缓释措施)

Chapter 2: 公司概况与股权结构
  ├─ 基础工商信息
  ├─ 股权结构 (投前)
  ├─ 历史融资情况
  ├─ 核心团队
  └─ 受益所有人识别 (反洗钱合规)

Chapter 3: 知识产权与核心竞争力
  ├─ 专利布局 (发明/实用新型/外观)
  ├─ 商标与品牌
  ├─ 软件著作权
  └─ 技术竞争力评估

Chapter 4: 法律与合规风险
  ├─ 涉诉情况 (原告/被告/被执行人)
  ├─ 被执行与失信
  ├─ 行政处罚
  └─ 合规结论

Chapter 5: 经营与市场分析
  ├─ 招投标活跃度 (业务规模指标)
  ├─ 资质与许可
  ├─ 市场地位与竞争
  └─ 舆情监控

Chapter 6: 财务分析
  ├─ 财务摘要 (近3年)
  ├─ 财务健康度
  └─ 估值分析

Chapter 7: 投资建议
  ├─ 投资建议与关键条款
  ├─ 主要风险提示
  └─ 投后管理要点
```

**全量MCP工具调用** (65个工具):
```
qcc_company (12个工具)
├─ 基础工商信息
├─ 股东结构
├─ 变更记录
└─ 分支机构

qcc_risk (16个工具)
├─ 司法风险全扫描
├─ 行政处罚
└─ 税务风险

qcc_ipr (5个工具)
├─ 专利
├─ 商标
├─ 软著
└─ 标准

qcc_operation (7个工具)
├─ 招投标
├─ 资质证书
├─ 信用评级
└─ 舆情监控
```

---

## 企查查MCP集成

### Server配置

```python
MCP_SERVERS = {
    "qcc_company": "https://mcp.qcc.com/data/company/stream",
    "qcc_risk": "https://mcp.qcc.com/data/risk/stream",
    "qcc_ipr": "https://mcp.qcc.com/data/ipr/stream",
    "qcc_operation": "https://mcp.qcc.com/data/operation/stream",
}
```

### 核心工具清单

| Server | 工具数 | 关键工具 |
|--------|--------|----------|
| qcc_company | 12 | 工商登记、股东信息、变更记录 |
| qcc_risk | 16 | 失信、被执行、股权冻结、破产 |
| qcc_ipr | 5 | 专利、商标、软著 |
| qcc_operation | 7 | 招投标、资质、信用评级 |

---

## 项目结构

```
financial-services-qcc/
├── README.md                           # 本文件
├── LICENSE                             # Apache 2.0
├── install_qcc_mcp_financial.sh        # 一键安装脚本
│
├── skills/
│   ├── kyb-verification-qcc/           # KYB自动化核验
│   │   └── SKILL.md
│   └── ic-memo-qcc/                    # IC Memo尽调
│       └── SKILL.md
│
├── scripts/
│   └── qcc_mcp_connector_financial.py  # MCP连接器
│
└── docs/
    ├── KYB_GUIDE.md                    # KYB使用指南
    └── IC_MEMO_GUIDE.md                # IC Memo编写指南
```

---

## 术语对照表

| 缩写 | 英文全称 | 中文名称 | 说明 |
|------|---------|---------|------|
| **KYB** | Know Your Business | 了解你的企业客户 | 金融机构对企业客户的身份识别和尽职调查 |
| **IC Memo** | Investment Committee Memorandum | 投资委员会备忘录 | 投资决策机构审议项目的正式决策文档 |
| **KYC** | Know Your Customer | 了解你的客户 | 金融机构对个人客户的身份识别 |
| **AML** | Anti-Money Laundering | 反洗钱 | 防止利用金融系统进行洗钱活动 |
| **UBO** | Ultimate Beneficial Owner | 最终受益所有人 | 对企业实施最终控制的自然人 |
| **PE/VC** | Private Equity / Venture Capital | 私募股权/风险投资 | 投资机构类型 |
| **DD** | Due Diligence | 尽职调查 | 投资前对目标企业的全面调查 |
| **MCP** | Model Context Protocol | 模型上下文协议 | AI与数据源交互的标准协议 |

---

## 核心对比

| 功能 | Anthropic原版 | QCC MCP增强版 |
|------|--------------|---------------|
| **数据来源** | Bloomberg/Refinitiv/Orbis | 企查查MCP官方数据 |
| **核验速度** | 2-3小时 | **30秒** |
| **覆盖范围** | 海外企业为主 | **中国企业全覆盖** |
| **风险扫描** | 基础合规 | **18类风险实时** |
| **股权穿透** | 人工处理 | **自动识别受益所有人(UBO)** |
| **知产尽调** | 多平台查询 | **一键全量扫描** |
| **报告生成** | 手动编写 | **自动填充IC Memo** |

---

## 贡献与反馈

### 联系方式

- **企查查MCP官网**: [https://mcp.qcc.com](https://mcp.qcc.com)
- **Email**: duhu@qcc.com

### 致谢

- 原版 [Anthropics Financial Services Plugins](https://github.com/anthropics/financial-services-plugins)
- [企查查MCP](https://mcp.qcc.com) - Agent-Native企业数据基座
- [Anthropic](https://anthropic.com) 的 Claude Code

---

## 许可证

Apache License 2.0

---

<div align="center">

**让金融机构尽调从"人工低效"走向"智能秒批"** ⚡

如果这个项目对您有帮助，请 ⭐ Star 支持！

[提交Issue](https://github.com/duhu2000/financial-services-qcc/issues) · [贡献代码](https://github.com/duhu2000/financial-services-qcc/pulls)

</div>
