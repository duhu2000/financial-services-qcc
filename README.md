# 💼 Financial Services QCC MCP Plugins
# 金融机构企查查MCP增强版插件

> **Know Your Business (KYB) Automation & Investment Committee Memorandum (IC Memo) Due Diligence**
>
> **企业客户身份识别自动化核验 & 投资委员会备忘录全维度尽职调查**

> 为银行KYB、投资尽调提供实时中国企业数据支持

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-QCC%20企查查-orange.svg)](https://agent.qcc.com)
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

**方案三：5大高价值Skill矩阵**
- **`strip-profile-qcc`**：3分钟企业画像速览（初步筛选）
- **`dd-checklist-qcc`**：尽调清单自动化（全流程管理）
- **`compliance-monitor-qcc`**：7x24风险持续监控（投后/贷后）
- **`esg-assessment-qcc`**：ESG风险评估（绿色投资）
- **`related-party-qcc`**：关联方穿透识别（IPO/并购）

**通用能力**：
- ✅ **智能决策支持** - 自动评级+准入建议+风险缓释
- ✅ **合规可追溯** - 所有数据来自官方+时间戳记录
- ✅ **双栖接入** - MCP+CLI双模式，零Token消耗可选

---

## 快速开始

### 1分钟快速体验

```bash
# 1. 一键安装（自动配置 MCP）
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)

# 2. 配置API Key（从 https://agent.qcc.com 申请）
export QCC_MCP_API_KEY="your_api_key_here"

# 3. ⚠️ 重要：重启 Claude Code 以加载 MCP 配置
# 完全退出 Claude Code，然后重新启动

# 4. 验证 MCP 配置（重启后）
# 你应该能看到可用的 MCP 工具：qcc-company, qcc-risk, qcc-ipr, qcc-operation

# 5. 开始KYB核验
/kyb-verification-qcc 华为技术有限公司

# 6. 或生成IC Memo
/ic-memo-qcc 北京字节跳动科技有限公司
```

---

## 安装指南

### 系统要求

- **操作系统**: macOS / Linux / Windows (WSL)
- **Python**: 3.9+
- **Claude Code**: 最新版本
- **网络**: 可访问 https://agent.qcc.com

### 安装步骤

#### 步骤1: 申请企查查MCP Key

1. 访问 [企查查MCP官网](https://agent.qcc.com)
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

#### 步骤4: ⚠️ 重启 Claude Code（关键步骤）

**必须完全退出并重新启动 Claude Code**，否则 MCP 配置不会生效。

```bash
# 完全退出 Claude Code（不是只关闭窗口，要彻底退出进程）
# macOS: Cmd+Q
# Linux: 关闭终端或 kill 进程

# 然后重新启动
claude
```

#### 步骤5: 验证 MCP 配置

重启后，Claude Code 应该能识别到企查查 MCP 工具。你可以通过以下方式验证：

1. **观察工具列表**：使用 `/kyb-verification-qcc` 时，Claude 应该显示 "调用 qcc-company/get_company_registration_info" 等 MCP 工具
2. **避免网页搜索**：如果配置正确，Claude 不会使用 "网页搜索" 来获取企业信息

**如果看到 "网页搜索" 而不是 MCP 工具调用，说明配置未生效，请检查：**
- `.mcp.json` 文件是否在 `~/.claude/.mcp.json`
- 是否已设置 `QCC_MCP_API_KEY`
- 是否已重启 Claude Code

详见 [MCP 配置指南](./docs/MCP_CONFIGURATION.md)

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

**输出示例：**
```
========================================
[KYBVerifier] 开始企业 KYB 自动化核验
========================================
目标企业: 华为技术有限公司
========================================

========================================
[Phase 1] 实体锚定 - 主体信息核验
========================================
[Phase 1] 查询企业工商注册信息...
  ✅ 实体锚定成功
     企业名称: 华为技术有限公司
     统一社会信用代码: 9144030019237xxxxx
     法定代表人: 赵明路
     经营状态: 存续

========================================
[Phase 2] 股权穿透与UBO识别
========================================
  ✅ 股东数量: 2
  ✅ 识别UBO: 1 人
     - 华为投资控股有限公司: 100%

========================================
[Phase 3] 18类风险全面扫描
========================================
  ✅ 风险扫描完成
     🔴 关键风险: 0 项
     🟠 高风险: 0 项
     🟡 中风险: 0 项
     🔵 低风险: 0 项

========================================
[Phase 4] 经营健康度评估与评级
========================================

========================================
[评级计算]
========================================

========================================
[KYBVerifier] 核验完成
企业名称: 华为技术有限公司
KYB评级: A
核验结论: 🟢 正常准入 - 主体合法存续，无明显风险信号，可按标准流程处理。
========================================
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

## 使用方式

### 方式一：Commands（V2推荐）

#### KYB企业核验

```
/qcc-kyb-profile 华为技术有限公司
/qcc-kyb-profile 北京字节跳动科技有限公司 91110108MA00xxxxxx
```

**输出：** A/B/C/D四级评级 + 详细核验报告（支持三种格式）

#### 全维度尽调

```
/qcc-full-dd-profile 目标企业名称
/qcc-full-dd-profile 宁德时代新能源科技股份有限公司 --round Pre-IPO --sector 新能源
```

**输出：** 7章IC Memo尽调报告（支持三种格式）

#### 输出格式选择

默认同时生成三种格式，可通过 `--format` 参数指定：

```bash
# 仅生成Markdown（便于系统对接）
/qcc-kyb-profile 华为技术有限公司 --format md

# 仅生成Word（适合风控审批、打印盖章）
/qcc-full-dd-profile 目标企业名称 --format docx

# 仅生成PPT（适合快速汇报、路演展示）
/qcc-kyb-profile 华为技术有限公司 --format pptx
```

| 格式 | 扩展名 | 适用场景 |
|------|--------|---------|
| Markdown | .md | 系统对接、API传输、数据入库 |
| Word | .docx | 风控审批、投委会审阅、打印盖章 |
| PPT | .pptx | 管理层汇报、投资路演、快速展示 |

### 方式二：Skills（兼容V1）

#### KYB核验

```
/kyb-verification-qcc 华为技术有限公司
```

#### IC Memo生成

```
/ic-memo-qcc 北京字节跳动科技有限公司 --sector 互联网
```

### 方式三：Python API

```python
from utils.kyb_verifier import KYBVerifier
from utils.dd_report_generator import DDReportGenerator

# KYB核验
verifier = KYBVerifier()
results = verifier.verify_company("华为技术有限公司")
print(f"KYB评级: {results['kyb_rating']}")

# 尽调报告
generator = DDReportGenerator()
report = generator.generate_full_dd_profile(
    company_name="北京字节跳动科技有限公司",
    investment_round="Series B"
)
```

---

## SKILL详解

### 1. KYB Verification QCC
**Know Your Business Verification**

| 项目 | 说明 |
|------|------|
| **英文全称** | Know Your Business |
| **中文名称** | 企业客户身份识别与核验 |
| **Commands** | `/qcc-kyb-profile` |
| **Skills** | `/kyb-verification-qcc` |
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
| **Commands** | `/qcc-full-dd-profile` |
| **Skills** | `/ic-memo-qcc` |
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

---

### 3. Strip Profile QCC
**Enterprise Strip Tease / One-Page Profile**

| 项目 | 说明 |
|------|------|
| **英文全称** | Strip Tease / One-Page Enterprise Profile |
| **中文名称** | 企业画像速览 / 一页纸企业扫描 |
| **Skills** | `/strip-profile-qcc` |
| **核心用途** | PE/VC初步筛选、投委会立项汇报、客户背景快速了解、竞品对比分析 |

**业务场景描述**：

> **场景：投资经理初步筛选潜在标的**
>
> 投资经理收到BP后，需要在3分钟内快速了解企业概况，决定是否推进初步沟通。
>
> **传统痛点**：
> - 需要登录企查查、天眼查等多个平台查询
> - 信息分散，难以形成整体印象
> - 手动整理一页纸摘要耗时30分钟+
>
> **Strip Profile解决方案**：
> 输入企业名称，3分钟内自动生成一页纸企业画像，包含：
> - 企业名片（工商基本信息）
> - 股权结构（股东+实控人）
> - 18类风险信号扫描结果
> - 知识产权资产盘点
> - 经营动态（资质/招投标/舆情）
> - 初步投资判断（基于数据的快速评估）

**输出格式**：
- **默认**：Markdown一页纸（便于微信/邮件分享）
- **可选**：PPT一页摘要（投委会汇报）
- **可选**：Word简报（客户交付）

**典型用户**：
- PE/VC投资经理（初步筛选）
- 投行分析师（立项前扫描）
- 券商研究所（研报素材收集）
- 企业战投（竞品监控）

---

### 4. DD Checklist QCC
**Due Diligence Checklist Automation**

| 项目 | 说明 |
|------|------|
| **英文全称** | Due Diligence Checklist Automation |
| **中文名称** | 尽职调查清单自动化 |
| **Skills** | `/dd-checklist-qcc` |
| **核心用途** | PE/VC投资尽调、并购交易尽调、IPO尽职调查、债券发行尽调 |

**业务场景描述**：

> **场景：投资团队启动A轮项目尽调**
>
> 投资团队决定对某科技企业进行A轮投资，需要开展全面的法律、财务、业务尽调。
>
> **传统痛点**：
> - 尽调清单模板分散，每次需要重新整理
> - 40+项数据需要人工收集，耗时2周
> - 尽调进度难以追踪，容易遗漏关键项
> - 风险变化无法实时监控
>
> **DD Checklist解决方案**：
> - **自动生成清单**：根据投资阶段（天使/A/B/C/Pre-IPO）生成标准化尽调清单
> - **数据自动填充**：14项数据由企查查MCP自动填充（工商/风险/知产/经营）
> - **进度可视追踪**：实时显示尽调完成进度（如"法律尽调 60%"）
> - **风险实时预警**：尽调期间企业出现风险变化自动提醒

**四大尽调维度**：

| 维度 | 清单项数 | 企查查自动填充 | 需人工补充 |
|------|----------|----------------|-----------|
| 法律尽调 (Legal DD) | 20项 | 10项 | 10项 |
| 财务尽调 (Financial DD) | 10项 | 2项 | 8项 |
| 业务尽调 (Business DD) | 10项 | 2项 | 8项 |
| 技术尽调 (Technical DD) | 6项 | 0项 | 6项 |

**特色功能**：
- **风险信号更新**：尽调期间发现企业新增被执行人，立即推送预警
- **交叉验证标记**：企查查数据与人工收集数据自动比对，发现差异
- **尽调报告生成**：清单完成后，自动生成尽调报告底稿

**典型用户**：
- PE/VC投资经理（投资尽调）
- 投行项目经理（IPO/并购尽调）
- 并购交易团队（并购尽调）
- 风控合规部门（合规尽调）

---

### 5. Compliance Monitor QCC
**Compliance Risk Continuous Monitoring**

| 项目 | 说明 |
|------|------|
| **英文全称** | Compliance Risk Continuous Monitoring |
| **中文名称** | 合规风险持续监控 |
| **Skills** | `/compliance-monitor-qcc` |
| **核心用途** | 银行贷后监控、投后管理、供应链风险预警、集团客户风险监测 |

**业务场景描述**：

> **场景：银行对公客户经理贷后管理**
>
> 某银行对公部管理着156家贷款客户，需要持续监控企业经营风险变化。
>
> **传统痛点**：
> - 人工定期检查，耗时耗力
> - 风险发现滞后，可能错过最佳处置时机
> - 风险信息分散，难以形成整体视图
> - 预警阈值不统一，容易漏报或误报
>
> **Compliance Monitor解决方案**：
> - **7x24自动监控**：企查查MCP每日自动扫描18类风险信号
> - **分级预警机制**：
>   - 🔴 高风险（失信/被执行/限高）：立即推送
>   - 🟡 中风险（股权冻结/处罚）：每日汇总
>   - 🟢 低风险：常规监控
> - **监控仪表盘**：一目了然的总体风险分布（高风险X家/中风险X家）
> - **日报/周报/月报**：自动生成监控报告

**18类风险监控覆盖**：

| 风险类别 | 监控内容 | 预警级别 |
|----------|----------|----------|
| 司法风险 | 失信、被执行、限高、终本 | 🔴 高 |
| 经营风险 | 异常、违法、处罚、吊销 | 🔴 高 |
| 财务风险 | 欠税、股权冻结、质押 | 🟡 中 |
| 清算风险 | 破产重整、清算、注销 | 🔴 高 |

**典型用户**：
- 银行合规部（贷后风险监控）
- PE/VC投后管理团队（被投企业监控）
- 供应链金融风控（供应商监控）
- 集团风控部门（子公司监控）

---

### 6. ESG Assessment QCC
**ESG Risk Assessment & Rating**

| 项目 | 说明 |
|------|------|
| **英文全称** | Environmental, Social and Governance Assessment |
| **中文名称** | ESG风险评估与评级 |
| **Skills** | `/esg-assessment-qcc` |
| **核心用途** | ESG主题投资基金筛选、绿色债券发行评估、上市公司ESG报告、可持续投资 |

**业务场景描述**：

> **场景：ESG基金投资新能源企业前的ESG评估**
>
> 某ESG主题基金拟投资宁德时代，需要进行ESG评级，评估环境、社会、治理表现。
>
> **传统痛点**：
> - ESG数据收集困难，特别是中小企业
> - ESG评级标准不统一
> - 难以量化评估，主要靠主观判断
> - 缺乏中国企业特色的ESG指标
>
> **ESG Assessment解决方案**：
> - **三维度自动评分**：
>   - E-环境（35%）：环保处罚、排污许可、环保信用
>   - S-社会（35%）：劳动仲裁、舆情声誉、社保缴纳
>   - G-治理（30%）：股权稳定、合规记录、信息透明
> - **企查查数据支撑**：环境/治理维度数据自动采集
> - **行业对标分析**：与同行业ESG表现对比
> - **投资适宜性判断**：综合评分给出投资建议

**ESG评分等级**：

| 等级 | 分数 | 含义 | 投资建议 |
|------|------|------|----------|
| **AAA** | 90-100 | ESG表现卓越 | 强烈推荐 |
| **AA** | 80-89 | ESG表现优秀 | 推荐 |
| **A** | 70-79 | ESG表现良好 | 可考虑 |
| **BBB** | 60-69 | ESG表现一般 | 谨慎考虑 |
| **BB** | 50-59 | ESG表现较弱 | 高风险 |
| **B** | 0-49 | ESG表现差 | 回避 |

**典型用户**：
- ESG投资基金（投资标的ESG评级）
- 绿色金融产品部门（绿色债券评估）
- 上市公司董办（ESG报告编制）
- 资管机构（可持续投资筛选）

---

### 7. Related Party QCC
**Related Party Identification & Penetration**

| 项目 | 说明 |
|------|------|
| **英文全称** | Related Party Identification & Equity Penetration |
| **中文名称** | 关联方穿透识别 |
| **Skills** | `/related-party-qcc` |
| **核心用途** | IPO招股书关联方披露、并购关联交易审查、银行集团客户识别、合规利益冲突检测 |

**业务场景描述**：

> **场景：投行IPO项目组进行招股书关联方核查**
>
> 某科技企业准备IPO，投行项目组需要全面识别企业关联方，用于招股书披露。
>
> **传统痛点**：
> - 股权结构复杂，穿透层级多，手工计算容易出错
> - 隐性关联方难以发现（如一致行动人）
> - 关联交易中交易对手识别困难
> - IPO申报前需要多次更新，工作量大
>
> **Related Party解决方案**：
> - **股权穿透计算**：自动逐层穿透识别实际控制人
> - **综合持股计算**：自动计算综合持股比例（考虑多层股权）
> - **一致行动人识别**：基于企查查数据识别隐性一致行动关系
> - **关联交易发现**：自动识别报告期内的关联交易
> - **关联图谱可视化**：生成股权结构图和关联关系网络

**穿透能力**：

| 穿透模式 | 层级 | 适用场景 |
|----------|------|----------|
| **标准穿透** | 3层 | 一般尽调 |
| **深度穿透** | 5层 | 复杂股权结构 |
| **全量穿透** | 无限制 | IPO招股书 |

**关联方识别范围**：

| 类别 | 识别内容 |
|------|----------|
| 股权关联方 | 5%以上股东、实控人、控股股东控制的其他企业 |
| 人员关联方 | 董监高及其近亲属、上述人员控制的企业 |
| 交易关联方 | 报告期重大交易对手、疑似关联交易 |
| 其他关联方 | 同一控制下企业、联营/合营企业 |

**典型用户**：
- 投行IPO项目组（招股书关联方披露）
- 并购交易团队（关联交易审查）
- 银行授信审批（集团客户识别）
- 审计机构（关联方交易审计）
- 合规部门（利益冲突检测）

---

## MCP服务说明

本插件使用企查查4个MCP服务：

| 服务 | 功能 | 工具 |
|------|------|------|
| **qcc-company** | 企业基座 | 工商登记、股东信息、变更记录 |
| **qcc-risk** | 风控大脑 | 失信、被执行、限高、破产等18类风险 |
| **qcc-ipr** | 知产引擎 | 专利、商标、软件著作权 |
| **qcc-operation** | 经营罗盘 | 招投标、资质证书、舆情 |


## KYB评级标准

| 评级 | 含义 | 处理建议 |
|------|------|----------|
| **A** | 正常准入 | 主体合法存续，无明显风险信号 |
| **B** | 审慎准入+加强监测 | 存在中等风险，增加监测频率 |
| **C** | 需人工复核 | 存在高风险，加强尽调 |
| **D** | 禁止准入 | 存在关键风险，终止业务办理 |

## 18类风险扫描

**CRITICAL级（<4小时响应）：**
- 失信被执行人
- 被执行人
- 限制高消费
- 破产重整
- 股权冻结
- 司法协助

**HIGH级（<24小时响应）：**
- 经营异常
- 严重违法
- 行政处罚
- 环保处罚

**MEDIUM级（关注）：**
- 股权出质
- 动产抵押
- 欠税公告
- 税务非正常
- 税收违法

**LOW级（备案）：**
- 涉诉信息
- 裁判文书
---


## 架构设计

```
financial-services-qcc-v2/
├── .mcp.json                          # MCP服务配置
├── commands/                          # 命令定义（主推方式）
│   ├── qcc-kyb-profile.md            # KYB核验命令
│   └── qcc-full-dd-profile.md        # 全维度尽调命令
├── utils/                             # Python工具类
│   ├── __init__.py
│   ├── qcc_mcp_client.py             # MCP客户端
│   ├── kyb_verifier.py               # KYB核验器
│   ├── dd_report_generator.py        # 尽调报告生成器
│   └── config_manager.py             # 配置管理器
├── investment-banking/skills/         # 投行业务技能
│   └── strip-profile/SKILL.md        # 公司简况生成
├── private-equity/skills/             # PE业务技能
│   └── ic-memo/SKILL.md              # IC Memo生成
├── scripts/                           # 安装脚本
│   └── install_qcc_mcp_financial.sh  # 一键安装脚本
├── docs/                              # 文档
│   └── MCP_CONFIGURATION.md          # MCP配置指南
└── UNINSTALL.md                       # 卸载指南
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

- **企查查MCP官网**: [https://agent.qcc.com](https://agent.qcc.com)
- **Email**: duhu@qcc.com

### 致谢

- 原版 [Anthropics Financial Services Plugins](https://github.com/anthropics/financial-services-plugins)
- [企查查MCP](https://agent.qcc.com) - Agent-Native企业数据基座
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

