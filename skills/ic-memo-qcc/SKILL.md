---
name: ic-memo-qcc
description: >
  IC Memo 投资备忘录 SKILL · 企查查 MCP V2.0 增强版。
  PE / VC 投资决策的核心尽调工具。一次调用并行完成目标公司工商登记、多层股权穿透、真实财务底盘、司法风险、知识产权、核心高管全景六维度扫描，直接输出符合投委会要求的标准格式备忘录。

  核心能力：
  - 多层股权穿透 + UBO 识别：`get_beneficial_owners` + `get_personnel_beneficial_owner` 双向锁定
  - **V2.0 新能力：真实财务底盘**（`get_financial_data` 3 年完整财报，首次用于投资类场景）
  - 知识产权资产清单：专利 / 商标 / 软件著作权 + 知产出质（V2.0 新工具）
  - 司法风险全景：当前 + 历史双层
  - 核心高管画像：法代 / 董事长 / 实控人 / CEO / CFO 的个人司法轨迹、任职履历、控制企业
  - 融资历史追踪：融资记录 × 历史股东变迁（qcc-history）

  适用场景：PE / VC 项目 DD、投资银行并购尽调、企业战投立项、Pre-IPO 投前核查、Term Sheet 前的快速筛查。

  使用方式：/ic-memo-qcc 目标公司名称 [--stage pre-a|a|b|c|pre-ipo] [--thesis 投资主题] [--format md|docx|pptx]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP V2.0)
  version: "2.0"
  plugin-commands: "/ic-memo-qcc"
  mcp-integrations: "qcc-company, qcc-risk, qcc-ipr, qcc-history, qcc-executive, qcc-operation"
  industry: "Financial Services - PE/VC/Investment Banking"
---

# IC Memo 投资备忘录 · 企查查 MCP V2.0 增强版

## SKILL 定位

本 SKILL 服务于 PE / VC 机构、投资银行、企业战投部门在投资决策前的项目尽调场景。IC Memo 是投委会决策的核心输入材料——传统分析师需要 2-3 小时人工拼接工商登记、股权穿透、司法风险、知识产权等多源数据，本 SKILL 一次调用 30 秒内完成所有数据收集 + 深度推演 + 标准格式输出。

V2.0 相对 V1.0 最具颠覆性的升级是 `get_financial_data` 首次让 IC Memo 能拿到真实财务数据——投资决策从"靠路演 PPT 宣称"升级为"靠 MCP 实时财务数据核验"。叠加 qcc-executive 对核心创始团队的个人画像扫描，IC Memo 的两个核心决策点（财务可信度 × 创始团队可靠性）从此具备了硬数据支撑。

## MCP 依赖与配置

必选：
- `qcc-company`（企业基座）—— 工商核验 + 股东 + 实控人 + UBO + 主要人员 + **`get_financial_data`**
- `qcc-risk`（风控大脑）—— 司法风险全维
- `qcc-ipr`（知产引擎）—— 专利 / 商标 / 软件著作权 / **`get_ipr_pledge`**（V2.0 新工具）

强烈建议：
- `qcc-history`（历史存档）—— 历史融资记录 / 历史股东变迁
- `qcc-executive`（人员画像）—— 创始团队个人画像

可选：
- `qcc-operation`（经营罗盘）—— 融资记录、招聘活跃度、荣誉信息

## 通用执行原则

**第一，IC Memo 的第一决策点是"财务数据真实性"。** 创业公司向投资人讲述的增长故事常常存在"经调整后的收入 / 非 GAAP 利润 / 管理口径"等包装。V2.0 `get_financial_data` 返回的是年报披露的审计口径数据，是判断路演 PPT 是否"水份过高"的基准。如 `get_financial_data` 返回与路演口径偏差 > 30%，IC Memo 必须显式标注"路演 vs 审计口径差异"。

**第二，创始团队是第二决策点。** 投资看人的本质是看"创始人 / 核心 CEO / CTO / CFO"过往商业记录。V2.0 qcc-executive 对这些自然人做多维扫描——个人失信 / 限高 / 限出境 / 其他控制企业是否存在过暴雷 / 历史任职记录中是否有职业稳定性问题。

**第三，股权结构的清晰性决定投资可行性。** 复杂代持 / VIE 架构 / 多层离岸 SPV 等均提高尽调难度。SKILL 须标注股权结构复杂度（简单 / 中等 / 复杂）+ VIE 风险（无 / 轻度 / 重度）+ UBO 清晰度（单一 / 多元 / 模糊）。

**第四，知识产权是科技项目的核心资产评估维度。** 专利数 + 软件著作权数 + 知产出质情况（V2.0 新工具）构成科技项目估值的重要基础，若知产已被大量质押融资，净资产中的"无形资产"水分极大。

**第五，融资历史连贯性预判估值合理性。** 通过 qcc-history 追溯历史股东变迁和融资记录，识别上轮估值与本轮估值的跃升合理性，警惕"估值倒挂"型项目。

## 工作流

### 维度一：目标公司工商与股权核验

工具链：
- `mcp__qcc-company__get_company_registration_info`
- `mcp__qcc-company__verify_company_accuracy`
- `mcp__qcc-company__get_shareholder_info`
- `mcp__qcc-company__get_actual_controller`
- `mcp__qcc-company__get_beneficial_owners`
- `mcp__qcc-company__get_external_investments`

产出：主体基本信息表、股权结构图（多层穿透）、UBO 清单、对外投资清单。

### 维度二：真实财务底盘（V2.0 核心新能力）

工具链：
- `mcp__qcc-company__get_financial_data` —— 3 年完整财报
- `mcp__qcc-company__get_annual_reports` —— 年报文本数据

核心评估指标：

| 类别 | 指标 | 投资评估意义 |
|------|------|------------|
| 规模 | 营业总收入、总资产 | 业务规模 |
| 盈利 | 净利润、毛利率、净利率 | 商业模型可持续性 |
| 成长 | 营收同比、总资产同比 | 成长速度 |
| 健康 | 资产负债率、流动比率、速动比率 | 财务稳健性 |
| 现金 | 经营现金流 | 自造血能力 |

**IC Memo 财务决策逻辑**：
- 连续 3 年营收高速增长（>50%）+ 毛利率 > 30% + 经营现金流趋正 → **高成长可投** A 类
- 营收增长但毛利率薄 + 现金流持续负 → **烧钱扩张** B 类，需评估估值与轮次匹配
- 营收停滞或下降 + 现金流负 → **早期风险或已过拐点** C 类，慎投

### 维度三：核心高管画像（V2.0 新能力）

对创始人 + CEO + CFO + CTO 做 qcc-executive 画像：

- `mcp__qcc-executive__get_personnel_dishonest` / `get_personnel_high_consumption_ban` / `get_personnel_judgment_debtor` / `get_personnel_exit_restriction` / `get_personnel_tax_violation`
- `mcp__qcc-executive__get_personnel_controlled_companies` / `get_personnel_investments` / `get_personnel_positions` / `get_personnel_historical_positions`

**投资视角重点**：
- 创始人其他控制企业是否存在失信 / 破产 → 道德风险信号
- 创始人 CFO 其他任职企业是否存在财务丑闻 → 重大审计风险
- CTO 是否同时在多家公司任技术负责人 → 精力分散 / 关联技术纠纷风险
- 历史任职企业是否集中在特定行业 → 创始团队的行业经验深度

### 维度四：司法风险扫描

工具链：
- `mcp__qcc-risk__*`（与其他 SKILL 类似的 10+ 工具）
- `mcp__qcc-history__get_historical_judicial_docs` / `get_historical_dishonest` / `get_historical_judgment_debtor`

**投资视角解读**：
- 当前诉讼为被告且大额 → 负面，需评估或有负债
- 当前诉讼为原告且追讨应收 → 中性，但反映客户违约风险
- 历史失信已修复 → 有风险承担能力但需标注
- 完全零诉讼 → 可能是"太年轻尚未经历纠纷"或"真正合规"，需结合成立年数判断

### 维度五：知识产权资产（含 V2.0 `get_ipr_pledge`）

工具链：
- `mcp__qcc-ipr__get_patent_info` —— 专利
- `mcp__qcc-ipr__get_trademark_info` —— 商标
- `mcp__qcc-ipr__get_software_copyright_info` —— 软著
- `mcp__qcc-ipr__get_copyright_work_info` —— 作品著作权
- `mcp__qcc-ipr__get_internet_service_info` —— 网络服务备案
- `mcp__qcc-ipr__get_ipr_pledge` —— **V2.0 新工具**，知产出质
- `mcp__qcc-history__get_historical_patent` / `get_historical_trademark` / `get_historical_ipr_pledge`

**估值关键判定**：
- 核心专利数 × 发明专利占比 → 技术壁垒深度
- 软件著作权数 → 软件资产规模
- **知产出质 > 50%** → 无形资产已大量抵押融资，净资产水分大
- 商标注册 + 域名备案 → 品牌护城河

### 维度六：融资历史与经营活跃度

工具链：
- `mcp__qcc-operation__get_financing_records` —— 融资记录
- `mcp__qcc-history__get_historical_shareholders` —— 历史股东变迁
- `mcp__qcc-history__get_historical_investments` —— 企业历史对外投资
- `mcp__qcc-operation__get_recruitment_info` —— 招聘活跃度（经营扩张信号）

**IC Memo 视角**：
- 历轮估值递进合理（每轮 2-3 倍）→ 健康
- 历轮估值倒挂 / 退出股东多 → 警惕
- 招聘活跃度 × 岗位层级 → 扩张真实性

## IC Memo 标准结构（投委会格式）

- **章节 1：交易摘要 · Decision Pack** —— 项目评级 A/B/C + 估值合理性 + 核心投资逻辑 + 核心风险点
- **章节 2：目标公司速览** —— 基本信息、所处赛道、核心产品、营收规模、团队规模
- **章节 3：股权穿透 × UBO 识别**（V2.0 加强）
- **章节 4：真实财务底盘**（V2.0 新能力）—— 3 年财报 + 关键比率 + 增长曲线
- **章节 5：核心高管画像**（V2.0 新能力）—— 创始人 + CEO + CFO + CTO 个人司法 + 任职履历
- **章节 6：司法风险全景** —— 当前 + 历史
- **章节 7：知识产权资产** —— 专利 + 商标 + 软著 + 知产出质（V2.0）
- **章节 8：融资历史与估值合理性**
- **章节 9：核心风险清单 × 缓释条款建议**（如反稀释 / 优先清算 / 对赌条款等）
- **章节 10：投委会建议与 Term Sheet 要点**

## 投委会评级

- **A 级（强烈推荐）**：财务 + 团队 + 股权 + 知产 + 融资历史五维度全部达标 → 建议 Lead / Co-lead
- **B 级（可投但有保留）**：四维度达标，一项有瑕疵 → 建议参投 + 加强对赌条款
- **C 级（暂缓）**：三维度以下达标 → 建议暂缓 + 要求补充材料
- **D 级（不投）**：任一致命风险（财务造假嫌疑 / 创始人出险 / 股权代持 / 当前重大诉讼）→ 不投

## 参数

- `--stage <轮次>`：投资轮次（Pre-A / A / B / C / Pre-IPO），影响评估重点
- `--thesis <投资主题>`：本机构对该项目的投资逻辑
- `--format md|docx|pptx`：输出格式，默认 md；pptx 为投委会一页摘要

## 边界与免责

本 SKILL 是基于主体侧公开数据的投资尽调，不涉及以下内容（需配合其他工作）：
- 创始人访谈与团队动态评估
- 市场规模与竞争格局分析
- 商业模式创新性判定
- 客户访谈与复购数据
- 供应链真实性验证（线下走访）

`get_financial_data` 覆盖上市公司、Pre-IPO 申报披露企业、部分有主动披露意愿的非上市公司。对早期 Pre-A / A 轮项目，大概率返回空——此时 IC Memo 的财务维度需依赖创业公司主动提供的审计 / VAT 报表 + 公司业务数据脱敏版。

最终投资决策由投委会综合评审，本 SKILL 输出仅为决策支持材料。

---

**SKILL 版本**：v2.0（MCP V2.0 升级版）
**适配 MCP 版本**：146 工具 / 6 Server 全量版
**所需 Server**：qcc-company（必选，含 get_financial_data）、qcc-risk（必选）、qcc-ipr（必选，含 get_ipr_pledge）、qcc-history（强烈建议）、qcc-executive（强烈建议）、qcc-operation（建议）
