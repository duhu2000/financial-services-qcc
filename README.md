# Financial Services QCC — 企查查MCP金融服务技能集

> 基于 [Anthropic Financial Services Plugins](https://github.com/anthropics/financial-services-plugins) 增强开发，深度融合企查查MCP实时数据，为金融机构提供中国企业尽调的 AI 工作流技能。

[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-QCC%20企查查-orange.svg)](https://agent.qcc.com)
[![Claude](https://img.shields.io/badge/Claude%20Code-Compatible-purple.svg)](https://claude.ai)

> ⚠️ **免责声明**：本技能集提供工作流辅助，不构成正式法律意见、投资建议或合规审批结论。关键决策前请结合专业判断与人工复核。

---

## 12个技能总览

### 核心技能（2个）

| 技能 | 命令 | 目标用户 | 核心场景 | 耗时 |
|------|------|---------|---------|------|
| **KYB企业核验** | `/kyb-verification-qcc` | 银行/券商/信托合规风控 | 企业开户核验、授信前尽调、反洗钱AML | ~30秒 |
| **IC Memo投资备忘录** | `/ic-memo-qcc` | PE/VC投资经理、IBD分析师 | Pre-IPO/并购/战投尽调，自动生成投委会备忘录 | ~30秒 |

### 增强技能（5个）—— 高优先级

| 技能 | 命令 | 目标用户 | 核心场景 |
|------|------|---------|---------|
| **企业画像速览** | `/strip-profile-qcc` | 投资经理、研究员 | 3分钟一页纸企业快速扫描，初步筛选/立项汇报 |
| **尽调清单自动化** | `/dd-checklist-qcc` | PE/VC、投行项目组 | 标准化尽调清单 + 企查查数据自动填充 + 进度追踪 |
| **合规风险监控** | `/compliance-monitor-qcc` | 银行合规部、投后管理 | 7×24小时风险信号监控，贷后/投后管理 |
| **ESG风险评估** | `/esg-assessment-qcc` | ESG基金、绿色金融 | E/S/G三维评分，可持续投资筛选 |
| **关联方穿透识别** | `/related-party-qcc` | 投行IPO项目组、审计 | 股权穿透、实控人识别、关联交易核查 |

### 专业扩展技能（5个）—— 中优先级

| 技能 | 命令 | 目标用户 | 核心场景 |
|------|------|---------|---------|
| **企业信用评级** | `/credit-rating-qcc` | 银行信贷、供应链金融 | 多维度信用评分，授信额度与利率建议 |
| **知识产权尽调** | `/ip-due-diligence-qcc` | 科技投资、IPO项目组 | 专利/商标/软著全维度尽调，技术竞争力评估 |
| **诉讼风险分析** | `/litigation-analysis-qcc` | 法务、投资机构 | 涉诉全景扫描，案件性质与执行风险深度分析 |
| **供应链风险评估** | `/supply-chain-risk-qcc` | 制造业、procurement | 供应商风险、集中度、韧性评估 |
| **高管背景调查** | `/executive-background-qcc` | HR、投资机构 | 法定代表人/董监高/实控人背景核查 |

---

## 企查查MCP集成

所有技能通过以下4个企查查MCP Server获取**官方实时数据**：

| Server | 别名 | 数据来源 | 主要能力 |
|--------|------|---------|---------|
| `qcc-company` | 企业基座 | 国家企业信用信息公示系统（SAMR）| 工商登记、股权结构、历史变更、分支机构 |
| `qcc-risk` | 风控大脑 | 法院执行网、裁判文书网、税务总局 | 失信/被执行/限高/股权冻结/行政处罚/欠税/破产 |
| `qcc-ipr` | 知产引擎 | 国家知识产权局、版权局 | 专利、商标、软件著作权 |
| `qcc-operation` | 经营罗盘 | 招投标数据库、工商许可 | 资质证书、招投标记录、行政许可、舆情 |

各技能与MCP模块的对应关系：

| 技能 | 企业基座 | 风控大脑 | 知产引擎 | 经营罗盘 |
|------|:------:|:------:|:------:|:------:|
| KYB企业核验 | ✅ | ✅ | — | ✅ |
| IC Memo备忘录 | ✅ | ✅ | ✅ | ✅ |
| 企业画像速览 | ✅ | ✅ | ✅ | ✅ |
| 尽调清单自动化 | ✅ | ✅ | ✅ | ✅ |
| 合规风险监控 | ✅ | ✅ | — | ✅ |
| ESG风险评估 | ✅ | ✅ | — | ✅ |
| 关联方穿透识别 | ✅ | ✅ | — | — |
| 企业信用评级 | ✅ | ✅ | — | ✅ |
| 知识产权尽调 | ✅ | ✅ | ✅ | — |
| 诉讼风险分析 | ✅ | ✅ | — | — |
| 供应链风险评估 | ✅ | ✅ | — | ✅ |
| 高管背景调查 | ✅ | ✅ | — | — |

---

## 快速开始

### 第一步：申请企查查MCP Key

访问 [https://agent.qcc.com](https://agent.qcc.com)，申请金融服务场景授权，获取API Key。

### 第二步：一键安装

```bash
git clone https://github.com/duhu2000/financial-services-qcc.git
cd financial-services-qcc
export QCC_MCP_API_KEY="your_api_key_here"
bash install_qcc_mcp_financial.sh
```

### 第三步：重启 Claude Code（必须）

完全退出并重新启动 Claude Code，MCP配置才会生效。

### 第四步：开始使用

```bash
# KYB企业核验
/kyb-verification-qcc 华为技术有限公司

# IC Memo投资备忘录
/ic-memo-qcc 北京字节跳动科技有限公司 --sector 互联网

# 企业画像速览（3分钟）
/strip-profile-qcc 宁德时代新能源科技股份有限公司

# 启动尽调流程
/dd-checklist-qcc 目标企业名称 --round Series-B

# 合规风险监控
/compliance-monitor-qcc 贷款企业名称 --mode daily

# ESG评估
/esg-assessment-qcc 企业名称 --sector 新能源

# 关联方穿透
/related-party-qcc 企业名称 --depth 5

# 企业信用评级（⭐新增）
/credit-rating-qcc 企业名称 --sector 制造业

# 知识产权尽调（⭐新增）
/ip-due-diligence-qcc 企业名称 --peer 竞品企业名称

# 诉讼风险分析（⭐新增）
/litigation-analysis-qcc 企业名称 --period 近3年

# 供应链风险评估（⭐新增）
/supply-chain-risk-qcc 企业名称 --tier 1 --depth 3

# 高管背景调查（⭐新增）
/executive-background-qcc 企业名称 --person 高管姓名
```

> 验证MCP是否生效：执行命令后应看到 `调用 qcc-company/get_company_registration_info` 等工具调用，而非"网页搜索"。

---

## 快速命令参考

| 命令 | 功能 | 典型耗时 | 输出格式 |
|------|------|---------|---------|
| `/kyb-verification-qcc` | KYB企业核验 | ~30秒 | Word/PPT/Markdown |
| `/ic-memo-qcc` | IC Memo投资备忘录 | ~30秒 | Word/PPT/Markdown |
| `/strip-profile-qcc` | 企业画像速览 | ~3分钟 | PPT/Markdown |
| `/dd-checklist-qcc` | 尽调清单自动化 | ~5分钟 | Markdown |
| `/compliance-monitor-qcc` | 合规风险监控 | ~2分钟 | Markdown/报告 |
| `/esg-assessment-qcc` | ESG风险评估 | ~3分钟 | Markdown |
| `/related-party-qcc` | 关联方穿透识别 | ~2分钟 | Markdown/图表 |
| `/credit-rating-qcc` | 企业信用评级 | ~2分钟 | Word/Markdown |
| `/ip-due-diligence-qcc` | 知识产权尽调 | ~5分钟 | Word/Markdown |
| `/litigation-analysis-qcc` | 诉讼风险分析 | ~3分钟 | Word/Markdown |
| `/supply-chain-risk-qcc` | 供应链风险评估 | ~5分钟 | Word/Markdown |
| `/executive-background-qcc` | 高管背景调查 | ~3分钟 | Word/Markdown |

详见 [MCP配置指南](./docs/MCP_CONFIGURATION.md)

---

## 技能详解

### 1. KYB企业核验 · `kyb-verification-qcc`

**适用对象**：银行对公客户经理、信贷审批员、合规风控、反洗钱专员、券商开户审核

**核心价值**：30秒完成传统2-3小时人工尽调，实现合规可追溯的自动化KYB核验

**工作流（4阶段）**：

| 阶段 | 工作内容 | 企查查MCP调用 |
|------|---------|-------------|
| Phase 1 · 实体锚定 | 企业名称+信用代码交叉验证，核查登记状态 | `qcc-company` · `get_company_registration_info` |
| Phase 2 · UBO识别 | 股权穿透，识别受益所有人（持股≥25%自然人，符合央行AML规定） | `qcc-company` · `get_shareholder_info` |
| Phase 3 · 风险扫描 | 18类风险全量并行扫描 | `qcc-risk` · 7个核心工具 |
| Phase 4 · 经营健康度 | 资质有效性、经营活跃度评估 | `qcc-operation` |

**18类风险分级**：

```
🔴 CRITICAL（立即预警）：失信被执行人 / 被执行人 / 限制高消费 / 破产重整 / 股权冻结
🔴 HIGH（24小时内）：经营异常 / 严重违法 / 行政处罚
🟡 MEDIUM（7天内）：股权出质 / 动产抵押 / 欠税公告 / 税务异常 / 环保处罚
🔵 LOW（备案）：涉诉信息 / 裁判文书
```

**输出格式**：A/B/C/D四级评级报告，支持 `.md` / `.docx` / `.pptx`

```
A级：正常准入          B级：审慎准入+加强监测
C级：需人工复核        D级：禁止准入
```

```bash
/kyb-verification-qcc 华为技术有限公司 91440300MA5FTZGD47
/kyb-verification-qcc 华为技术有限公司 --format docx   # 仅生成Word
```

---

### 2. IC Memo投资委员会备忘录 · `ic-memo-qcc`

**适用对象**：PE/VC投资经理、投行IBD分析师、企业战略投资部、FA财务顾问

**核心价值**：一键生成7章节标准IC Memo，企查查全4大MCP模块并行采集，<30秒完成数据采集，告别2天手工编写

**7章节结构**：

| 章节 | 内容 | 主要MCP调用 |
|------|------|-----------|
| Chapter 1 · 执行摘要 | 投资建议 / 核心亮点Top5 / 关键风险Top5 | — |
| Chapter 2 · 公司概况与股权 | 工商信息 / 股权结构 / 融资历史 / 核心团队 / 受益所有人 | `qcc-company` |
| Chapter 3 · 知识产权 | 专利（发明/实用新型/外观）/ 商标 / 软著 / 技术竞争力评估 | `qcc-ipr` |
| Chapter 4 · 法律合规风险 | 涉诉统计 / 失信被执行 / 行政处罚 / 合规结论 | `qcc-risk` |
| Chapter 5 · 经营市场分析 | 招投标活跃度 / 资质许可 / 市场地位 / 舆情监控 | `qcc-operation` |
| Chapter 6 · 财务分析 | 近3年财务摘要 / 健康度评估 / 估值分析 | `qcc-company` |
| Chapter 7 · 投资建议 | 投资条款建议 / 主要风险 / 投后管理要点 | — |

**输出格式**：支持 `.md` / `.docx` / `.pptx` 三种格式同时生成

| 格式 | 适用场景 |
|------|---------|
| Word (.docx) | 投委会审阅、打印盖章、正式存档 |
| PPT (.pptx) | 投委会现场汇报、路演展示 |
| Markdown (.md) | 系统对接、内部Wiki、数据入库 |

```bash
/ic-memo-qcc 宁德时代新能源科技股份有限公司 --round Pre-IPO --sector 新能源
/ic-memo-qcc 北京字节跳动科技有限公司 --format pptx   # 仅生成PPT
```

---

### 3. 企业画像速览 · `strip-profile-qcc`

**适用对象**：投资经理（初步筛选）、投行分析师（立项前扫描）、券商研究员（研报素材）、企业战投（竞品监控）

**核心价值**：收到BP后3分钟内生成一页纸企业画像，决定是否推进——替代登录多个平台、手动整理30分钟的传统流程

**输出内容（一页纸）**：

```
企业名片          工商基本信息 + 成立年限 + 社保人数
股权结构          前N大股东 + 实控人识别
风险信号          18类风险扫描结果（红/黄/绿）
知识产权          专利/商标/软著数量盘点
经营动态          近期招投标 + 核心资质 + 舆情摘要
初步判断          基于数据的快速投资/合作适宜性评估
```

**输出格式**：Markdown（微信/邮件分享）/ PPT（投委会立项汇报）/ Word（客户交付）

```bash
/strip-profile-qcc 美团平台有限公司
/strip-profile-qcc 企业名称 --format pptx
```

---

### 4. 尽调清单自动化 · `dd-checklist-qcc`

**适用对象**：PE/VC投资经理、投行项目经理、并购交易团队、风控合规部门

**核心价值**：一键生成标准化尽调清单，企查查数据自动填充14项，尽调周期从2周压缩至数天

**四大尽调维度**：

| 维度 | 清单项数 | 企查查自动填充 | 需人工补充 |
|------|---------|--------------|----------|
| 法律尽调（Legal DD） | 20项 | 10项 | 10项 |
| 财务尽调（Financial DD） | 10项 | 2项 | 8项 |
| 业务尽调（Business DD） | 10项 | 2项 | 8项 |
| 技术尽调（Technical DD） | 6项 | 0项 | 6项 |

**特色功能**：
- 按投资轮次（天使/A/B/C/Pre-IPO）自动匹配清单深度
- 尽调期间企业风险变化实时推送（如新增被执行人）
- 企查查数据与人工收集数据自动交叉验证，发现差异标记
- 清单完成后自动生成尽调报告底稿

```bash
/dd-checklist-qcc 目标企业名称 --round Series-B
/dd-checklist-qcc 目标企业名称 --stage IPO
```

---

### 5. 合规风险监控 · `compliance-monitor-qcc`

**适用对象**：银行合规部（贷后监控）、PE/VC投后管理团队、供应链金融风控、集团风控部门

**核心价值**：7×24小时自动扫描18类风险信号，替代人工定期检查，第一时间发现风险

**监控维度与预警分级**：

| 风险类别 | 监控内容 | 预警级别 | 响应时限 |
|---------|---------|---------|---------|
| 司法风险 | 失信、被执行、限高、终本案件 | 🔴 高 | 立即推送 |
| 经营风险 | 经营异常、严重违法、行政处罚 | 🔴 高 | 立即推送 |
| 清算风险 | 破产重整、清算信息 | 🔴 高 | 立即推送 |
| 财务风险 | 股权冻结、欠税公告、股权出质 | 🟡 中 | 每日汇总 |
| 环保风险 | 环保处罚、整改通知 | 🟡 中 | 每日汇总 |

**输出形式**：
- 实时预警通知（触发即推送）
- 日报 / 周报 / 月报（自动生成）
- 监控仪表盘（整体风险分布概览）

```bash
/compliance-monitor-qcc 企业名称 --mode daily-report
/compliance-monitor-qcc 企业名称 --mode realtime-alert
```

---

### 6. ESG风险评估 · `esg-assessment-qcc`

**适用对象**：ESG主题投资基金、绿色金融产品部门、上市公司董办（ESG报告）、资管机构可持续投资

**核心价值**：中国企业ESG数据收集难题的解法——企查查MCP自动填充E/S/G三维度关键指标

**三维度评估框架**：

| 维度 | 权重 | 企查查数据支撑 | 补充来源 |
|------|------|--------------|---------|
| E · 环境（Environmental） | 35% | 环保处罚记录、排污许可 | 年报披露、第三方报告 |
| S · 社会（Social） | 35% | 社保缴纳人数、劳动仲裁、舆情 | 招聘数据、媒体报道 |
| G · 治理（Governance） | 30% | 股权稳定性、行政处罚合规记录 | 审计意见、信披质量 |

**ESG评级**：AAA（≥90分）/ AA（80-89）/ A（70-79）/ BBB（60-69）/ BB（50-59）/ B（＜50）

```bash
/esg-assessment-qcc 宁德时代新能源科技股份有限公司 --sector 新能源
/esg-assessment-qcc 企业名称 --benchmark 行业均值对比
```

---

### 7. 关联方穿透识别 · `related-party-qcc`

**适用对象**：投行IPO项目组（招股书关联方披露）、并购交易团队（关联交易审查）、银行授信审批（集团客户识别）、审计机构

**核心价值**：替代人工逐层手算，自动穿透股权关系，发现隐性关联方与一致行动人

**穿透能力**：

| 穿透模式 | 层级 | 适用场景 |
|---------|------|---------|
| 标准穿透 | 3层 | 一般尽调 |
| 深度穿透 | 5层 | 复杂股权结构 |
| 全量穿透 | 无限制 | IPO招股书披露 |

**关联方识别范围**：

| 类别 | 识别内容 |
|------|---------|
| 股权关联方 | 5%以上股东、实控人、控股股东控制的其他企业 |
| 人员关联方 | 董监高及其近亲属控制的企业 |
| 交易关联方 | 报告期重大交易对手、疑似关联交易 |
| 隐性关联方 | 一致行动人、代持结构、协议控制 |

**输出内容**：关联方清单 + 股权结构图（Mermaid）+ 关联关系网络图 + 关联交易风险提示

```bash
/related-party-qcc 企业名称 --depth 5
/related-party-qcc 企业名称 --purpose IPO   # IPO关联方全量核查
```

---

## 典型使用场景

### 银行对公客群

**场景：企业开户KYB全流程**
```
收到开户申请
→ /kyb-verification-qcc 企业名称 统一社会信用代码
→ 企查查MCP自动采集工商+司法+经营数据（~30秒）
→ 输出A/B/C/D评级 + KYB核验报告（Word格式留档）
→ C/D级自动触发人工复核流程
```

**场景：授信后贷后风险监控**
```
放款后持续监控
→ /compliance-monitor-qcc 贷款企业 --mode realtime-alert
→ 18类风险信号7×24自动扫描
→ 风险事件立即推送，日报/月报自动生成
```

---

### 投资机构客群（PE/VC · 券商IBD）

**场景：收到BP后初步筛选**
```
收到项目BP
→ /strip-profile-qcc 目标企业名称
→ 3分钟一页纸画像：工商+风险+知产+经营+初步判断
→ 快速决定是否安排见面/推进初步调研
```

**场景：决定投资后启动正式尽调**
```
决定推进
→ /dd-checklist-qcc 目标企业名称 --round Series-B
→ 生成标准化4维度尽调清单
→ 企查查自动填充14项，剩余项目分配人工收集
→ 进度追踪 + 风险变化实时预警

尽调完成，准备投委会
→ /ic-memo-qcc 目标企业名称 --round Series-B --sector 行业
→ 自动生成7章节IC Memo（<30秒数据采集）
→ PPT格式用于投委会汇报，Word格式存档
```

**场景：IPO项目关联方核查**
```
IPO项目关联方核查
→ /related-party-qcc 目标企业名称 --purpose IPO --depth 全量
→ 自动穿透识别实控人/受益所有人/一致行动人
→ 输出关联方清单 + 股权结构图（直接对接招股书披露）
```

**场景：ESG主题基金投资前评估**
```
ESG基金拟投某新能源企业
→ /esg-assessment-qcc 企业名称 --sector 新能源 --benchmark 行业均值
→ E/S/G三维度数据自动采集 + 综合评级
→ 输出ESG评估报告（支持绿色金融产品备案）
```

---

## 与原版 Anthropic Plugins 的对比

| 能力 | Anthropic 原版 | Financial Services QCC |
|------|--------------|----------------------|
| **数据来源** | Bloomberg / Refinitiv / Orbis | **企查查MCP官方数据** |
| **中国企业覆盖** | 有限 | **全覆盖（含非上市中小企业）** |
| **核验速度** | 2-3小时人工 | **~30秒自动化** |
| **风险扫描** | 基础合规 | **18类风险实时扫描** |
| **股权穿透** | 需人工处理 | **自动识别UBO/实控人** |
| **知产尽调** | 多平台手动查询 | **一键全量扫描** |
| **ESG数据** | 西方ESG框架 | **中国本土ESG指标** |
| **输出格式** | Markdown | **Markdown + Word + PPT** |

---

## 项目结构

```
financial-services-qcc/
├── skills/                          # 12个技能（核心）
│   ├── kyb-verification-qcc/        # KYB企业核验
│   │   └── SKILL.md
│   ├── ic-memo-qcc/                 # IC Memo投资备忘录
│   │   └── SKILL.md
│   ├── strip-profile-qcc/           # 企业画像速览
│   │   └── SKILL.md
│   ├── dd-checklist-qcc/            # 尽调清单自动化
│   │   └── SKILL.md
│   ├── compliance-monitor-qcc/      # 合规风险监控
│   │   └── SKILL.md
│   ├── esg-assessment-qcc/          # ESG风险评估
│   │   └── SKILL.md
│   ├── related-party-qcc/           # 关联方穿透识别
│   │   └── SKILL.md
│   ├── credit-rating-qcc/           # 企业信用评级 ⭐新增
│   │   └── SKILL.md
│   ├── ip-due-diligence-qcc/        # 知识产权尽调 ⭐新增
│   │   └── SKILL.md
│   ├── litigation-analysis-qcc/     # 诉讼风险分析 ⭐新增
│   │   └── SKILL.md
│   ├── supply-chain-risk-qcc/       # 供应链风险评估 ⭐新增
│   │   └── SKILL.md
│   └── executive-background-qcc/    # 高管背景调查 ⭐新增
│       └── SKILL.md
├── commands/                        # 快捷命令
│   ├── qcc-kyb-profile.md
│   └── qcc-full-dd-profile.md
├── docs/
│   └── MCP_CONFIGURATION.md        # MCP配置详细指南
├── install_qcc_mcp_financial.sh     # 一键安装脚本
└── utils/                           # Python工具类
```

---

## 术语对照

| 缩写 | 英文全称 | 中文名称 |
|------|---------|---------|
| KYB | Know Your Business | 企业客户身份识别 |
| IC Memo | Investment Committee Memorandum | 投资委员会备忘录 |
| UBO | Ultimate Beneficial Owner | 最终受益所有人 |
| AML | Anti-Money Laundering | 反洗钱 |
| ESG | Environmental, Social, Governance | 环境、社会、治理 |
| DD | Due Diligence | 尽职调查 |
| MCP | Model Context Protocol | 模型上下文协议 |
| IBD | Investment Banking Division | 投资银行部 |

---

## 贡献与反馈

- **企查查MCP官网**：[https://agent.qcc.com](https://agent.qcc.com)
- **Issues**：[提交Issue](https://github.com/duhu2000/financial-services-qcc/issues)
- **原版 Anthropic Plugins**：[anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins)

---

## 许可证

[Apache License 2.0](./LICENSE)

---

<div align="center">

**让金融机构尽调从"人工低效"走向"智能秒批"** ⚡

</div>
