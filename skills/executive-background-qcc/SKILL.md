---
name: executive-background-qcc
description: >
  高管背景核查 SKILL · 企查查 MCP V2.0 增强版。
  以"企业 + 人名双锚"为基础，针对目标企业的法定代表人、董事长、总经理、核心董监高、实际控制人开展个人风险穿透与关联网络测绘。

  核心能力：
  - 个人司法风险 × 历史追溯：18 个现状工具 + 14 个历史工具，覆盖失信 / 限高 / 限出境 / 股权冻结 / 股权出质 / 税收违法 / 行政处罚 / 裁判文书等维度
  - 任职履历与职业轨迹：在外任职、历史任职、担任法代历史、集团内部历任高管 —— 还原完整职业曲线
  - 关联企业网络：控制企业 / 关联企业 / 对外投资 / 最终受益人 × 历史版本，输出高管私人商业帝国图谱
  - 利益冲突与历史合作伙伴：关联交易嫌疑、竞业禁止、家族关联、资金链腾挪痕迹识别
  - 同名误查保护：所有人员工具均双锚定（企业名 + 人员姓名），避免同名自然人串查

  适用场景：投资尽调 / 人才引进 / 高管聘任 / IPO 核查 / 反洗钱 KYC / 客户风险画像。

  使用方式：/executive-background-qcc 企业名称 [--person 姓名] [--depth full] [--period 10年] [--format md|docx|pptx]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP V2.0)
  version: "2.0"
  plugin-commands: "/executive-background-qcc"
  mcp-integrations: "qcc-company, qcc-executive, qcc-history, qcc-risk"
  industry: "Financial Services - Investment / HR / Compliance"
---

# 高管背景核查 · 企查查 MCP V2.0 增强版

## SKILL 定位

本 SKILL 服务于投资尽调、人才引进、高管聘任、IPO 核查、反洗钱 KYC、金融机构客户风险画像等场景的关键人员背调需求。输入目标企业全称或统一社会信用代码后，SKILL 自动锁定该企业的法定代表人、董事长、总经理、核心董监高与实际控制人，以"企业 + 姓名双锚"方式拉取 MCP V2.0 中的 qcc-executive 42 个人员画像工具，形成个人司法、任职履历、关联企业、利益冲突四位一体的结构化背调报告。

与旧版"从企业数据推断高管个人情况"的做法相比，V2.0 工具链把查询主体从"企业"切换到了"人"，输出的数据颗粒度从篇幅性的事件描述升级为每个自然人一份独立的风险档案，真正满足尽调口径与合规档案留存要求。

## MCP 依赖与配置

SKILL 运行前必须确保以下 MCP Server 已配置：

必选：
- `qcc-company`（企业基座，15 工具）—— 获取企业基础信息、主要人员清单、股东、实际控制人
- `qcc-executive`（人员画像，42 工具）—— 本 SKILL 核心数据源，所有个人级查询均来自此 Server

强烈建议开通（用于历史轨迹）：
- `qcc-history`（历史存档，34 工具）—— 提供历届高管、历任法代等企业侧的历史维度数据
- `qcc-risk`（风控大脑，34 工具）—— 对关联企业做快速风险标签时使用

配置后需在 Claude Code 中重启加载 MCP。详细配置方法参见 `docs/MCP_CONFIGURATION.md`。

## 通用执行原则

本 SKILL 在任何场景下均遵循以下业务原则，不得省略或简化：

**第一，时间维度必须穿透。** 任何一项现任职务、控制企业、任职履历、司法记录均须同步查询 historical 版本，识别"曾经存在但已退出"的关联关系。这是揪出利益输送、隐性关联、跳槽时点异常的关键。5 年内的历史事件视同现状事件处理，5-10 年内的事件单独成段分析始末，10 年以上的事件归入"历史标注"层级、不触发当前尽调升级。

**第二，个人风险不等于企业风险。** 同一自然人在 A 企业可能是清洁法代、在 B 企业可能是被执行人。个人失信不等于其任职的所有企业都有问题，但个人失信一定影响其作为高管的信用判断。个人风险扫描必须以"人"为主体独立成章，不得与企业风险混报。

**第三，法代 / 实控人 / 董事长 / 总经理必须分别画像。** 这四类角色在境内公司治理中的法律责任、经济利益、决策权重差异显著，简化合并将导致关键风险信号丢失。即便四者由同一自然人兼任，仍须分别列出其在四个角色下的责任边界。

**第四，利益冲突排查优先于关联企业清点。** 单纯列出关联企业清单是信息堆砌。必须对每一家关联企业标注"与目标企业的业务重叠度"、"是否为供应商 / 客户 / 竞对"、"是否存在资金往来嫌疑"，才构成可用的利益冲突评估。

**第五，数据时效必须明示。** 所有输出项均须标注 MCP 采集时间戳。人员数据是动态的 —— 任职调整、司法状态更新、股权变动随时发生。决策前必须明示时效并提示关键字段的失效可能性。

**第六，同名误查须人工兜底。** qcc-executive 的双参数锚定已大幅降低同名误查风险，但无法完全消除。当职务、任职时间、关联企业三条线索中任一条出现明显矛盾时，须在报告中显式标注"疑似同名"，由人工做交叉确认。

## 工作流

### 维度一：主体确认与人员锁定

**目标**：确认目标企业身份，锁定本次背调覆盖的人员范围与优先级。

工具链：
1. `mcp__qcc-company__get_company_registration_info` — 工商登记信息，核验企业名称、统一社会信用代码、法定代表人、企业状态
2. `mcp__qcc-company__get_key_personnel` — 当前董监高全名单
3. `mcp__qcc-company__get_shareholder_info` — 股东结构
4. `mcp__qcc-company__get_actual_controller` — 实际控制人穿透链路

产出：《本次背调人员清单》—— 分为"必背"（法代 / 实控人 / 董事长 / 总经理）与"选背"（其他董事 / 监事 / 副总裁 / CFO / 技术负责人）两类，每人附职务、任职起始日期、持股比例（如有）、与目标企业的关联类型。

人员范围判定规则：
- 默认模式：仅对必背四类人员做完整画像（法代、实控人、董事长、总经理）
- `--person <姓名>`：只对指定人员做完整画像，其他人员在清单中仅列出姓名 + 职务
- `--depth full`：对清单中全部人员做完整画像

### 维度二：个人司法风险穿透（qcc-executive 核心调用）

**目标**：以"企业 + 人名双锚"对每位背调对象查询其在目标企业环境下的全部个人司法风险信号。本维度是 V2.0 MCP 相对旧版最核心的能力跃迁。

**现状扫描工具链（18 个）**：

身份限制与失信类：
- `mcp__qcc-executive__get_personnel_dishonest` — 当前是否为失信被执行人
- `mcp__qcc-executive__get_personnel_high_consumption_ban` — 当前是否被限制高消费
- `mcp__qcc-executive__get_personnel_exit_restriction` — 当前是否被限制出境
- `mcp__qcc-executive__get_personnel_property_reward_notice` — 是否被发布财产悬赏公告

执行与资产冻结类：
- `mcp__qcc-executive__get_personnel_judgment_debtor` — 当前是否作为被执行人
- `mcp__qcc-executive__get_personnel_terminated_cases` — 终本案件记录
- `mcp__qcc-executive__get_personnel_equity_freeze` — 名下股权是否被司法冻结
- `mcp__qcc-executive__get_personnel_equity_pledge` — 名下股权出质情况
- `mcp__qcc-executive__get_personnel_stock_pledge` — 上市公司股东股票质押
- `mcp__qcc-executive__get_personnel_valuation_inquiry` — 资产询价评估记录

行政与税务类：
- `mcp__qcc-executive__get_personnel_admin_penalty` — 行政处罚记录
- `mcp__qcc-executive__get_personnel_tax_violation` — 税收违法记录

司法程序类：
- `mcp__qcc-executive__get_personnel_case_filing` — 涉及的法院立案信息
- `mcp__qcc-executive__get_personnel_hearing_notice` — 开庭公告
- `mcp__qcc-executive__get_personnel_court_notice` — 法院公告
- `mcp__qcc-executive__get_personnel_service_notice` — 送达公告
- `mcp__qcc-executive__get_personnel_judicial_docs` — 裁判文书
- `mcp__qcc-executive__get_personnel_pre_litigation_mediation` — 诉前调解

**历史追溯工具链（14 个）**：对应上述工具的 historical 版本，用于识别"已解决但曾经发生"的风险事件。

- `mcp__qcc-executive__get_personnel_historical_dishonest` / `_high_consumption_ban` / `_judgment_debtor` / `_terminated_cases` / `_equity_freeze` / `_equity_pledge` / `_admin_penalty` / `_case_filing` / `_hearing_notice` / `_court_notice` / `_service_notice` / `_judicial_docs` / `_pre_litigation_mediation`

**分析要点**：

现状层以三色信号呈现 —— 🔴 红色信号为"一票否决级"，任何一项硬性失信、限高、限出境、股权冻结未解除均直接触发 D 级评级，建议不聘任 / 不投资 / 不合作。

历史层重点识别"修复型主体" —— 曾发生但已履行的失信记录在某些场景（例如创业早期融资阶段出现过的被执行）可以作为评级下调的缓解因素，但在高端金融机构 KYC、IPO 严格核查场景中仍须在报告中显式披露，不得删除。

时间维度的分层处理规则：
- 距今 5 年内：视同现状事件处理，纳入综合评级计算
- 距今 5-10 年：历史事件单独成段分析始末，说明是否已"修复"，对评级起缓解或加重作用
- 距今 10 年以上：归入"历史标注"层级，在报告附录出现，原则上不影响当前评级

### 维度三：任职履历与职业轨迹

**目标**：还原每位背调对象的完整职业履历，识别任职稳定性、职业梯度、跳槽可疑点。

工具链：
- `mcp__qcc-executive__get_personnel_positions` — 当前在外任职（该人员在其他企业当前担任的职务）
- `mcp__qcc-executive__get_personnel_historical_positions` — 历史在外任职（已离职的职务）
- `mcp__qcc-executive__get_personnel_legal_rep_roles` — 当前担任法定代表人的企业列表
- `mcp__qcc-executive__get_personnel_historical_legal_rep_roles` — 历史担任法定代表人的企业列表
- `mcp__qcc-history__get_historical_executives` — 目标企业自身的历届高管（上下文用）
- `mcp__qcc-history__get_historical_legal_rep` — 目标企业自身的历届法定代表人（上下文用）

**分析要点**：

任职稳定性以平均任期衡量。少于 1 年的短期任职如密集出现（例如近 3 年内 5 次以上），视为职业稳定性信号不佳，在 B 级以下的人员评级中加重。

职业梯度判断依据是历史任职企业的层级变化：从大企业到创业公司、从创业公司到大企业均有合理解读，但"职位级别持续下降"、"任职企业规模持续缩水"、"任职领域持续偏移到冷门行业"是负面信号组合。

跳槽可疑点重点关注"短期内连续变更关键职务"——例如 3 个月内连续离任 3 个董事职务，常见于企业风险爆发前的"高管集体跑路"模式。本 SKILL 明确将此列为独立的风险事件在报告中标注。

### 维度四：关联企业网络与控制力

**目标**：围绕每位背调对象绘制其直接控制、间接控制、任职、投资覆盖的完整关联企业网络。

工具链：
- `mcp__qcc-executive__get_personnel_controlled_companies` — 当前实际控制的企业
- `mcp__qcc-executive__get_personnel_related_companies` — 当前全部关联企业（涵盖任何角色）
- `mcp__qcc-executive__get_personnel_investments` — 当前对外投资（直接 + 间接双维度）
- `mcp__qcc-executive__get_personnel_beneficial_owner` — 作为最终受益人的企业
- `mcp__qcc-executive__get_personnel_historical_related_companies` — 历史全部关联企业
- `mcp__qcc-executive__get_personnel_historical_investments` — 历史对外投资
- `mcp__qcc-company__get_external_investments` — 目标企业自身对外投资（用于交叉比对）

**分析要点**：

关联企业清单不是简单罗列 —— 必须按"业务重叠度"分级：高重叠（同业务 / 上下游）、中重叠（相关领域）、低重叠（不相关）。高重叠类关联企业须在后续维度五的利益冲突章节单独分析。

对每一家关联企业同步调用 `mcp__qcc-company__get_company_registration_info` 与 `mcp__qcc-risk__get_dishonest_info`，以及对应历史版本工具，为每家关联企业快速打一个风险标签（绿 / 黄 / 红），避免"清洁人员 + 多家高风险关联企业"的隐性风险被忽略。

受益所有人维度是 AML 合规的硬性要求。凡本次背调对象在 5 家以上企业出任最终受益人的，须在报告中单独列出股权穿透图，并说明是否存在"借名持股 / 代持"的嫌疑信号（例如关联企业注册地高度集中、受益比例接近 25% 阈值等）。

### 维度五：利益冲突与历史合作伙伴

**目标**：识别潜在的关联交易、竞业冲突、家族关联、利益输送链。

工具链：
- 维度四产出的关联企业全集（作为输入）
- `mcp__qcc-executive__get_personnel_historical_partners` — 历史合作伙伴链路（V2.0 新开放）
- `mcp__qcc-operation__get_bidding_info` — 目标企业招投标对手方，用于识别关联交易
- `mcp__qcc-company__get_external_investments` — 目标企业对外投资
- 对关联企业集合与目标企业上下游集合做交叉比对

**分析要点**：

关联交易嫌疑的判定公式：

```
(关联企业集合) ∩ (供应商集合 ∪ 客户集合 ∪ 竞对集合) ≠ ∅
```

任何命中均须在报告中具体列出，注明关联方式（股东 / 法代 / 高管 / 投资人）、重叠业务、交易规模（如可获取）。

家族关联的依据有限，本 SKILL 不做"确认家族关联"断言，仅通过姓氏同源 + 相同身份证前 6 位 + 同省市注册地的启发式组合输出"疑似家族关联"提示，由人工复核确认。

历史合作伙伴维度是 V2.0 MCP 新开放的能力。该维度用于识别"已经不再合作但曾有业务往来"的企业，对识别资金链切割转移、资产腾挪、亲信企业更替等敏感行为具有关键价值。在高风险尽调项目中必须覆盖。

## 综合评级

本 SKILL 按下列 ABCD 四级输出最终人员评级与整体评级。整体评级采用"最短板原则"——多位被核查人员中最低等级决定整体评级，不取平均值。

- **A 级**：无现状个人风险，无历史重大事件，任职履历稳定，关联企业清洁，无利益冲突——可正常聘任 / 可继续合作
- **B 级**：无现状个人风险，但存在 5-10 年内的轻度历史事件（例如已结清的小额被执行），或任职履历轻微波动——可聘任 / 可合作，建议在入职 / 投后协议中加入常规信息披露条款
- **C 级**：存在 5 年内已解除的中等风险历史事件，或关联企业中存在 1-2 家可疑高风险主体，或利益冲突嫌疑虽不确认但有线索——谨慎聘任 / 谨慎合作，签约前须由法务发问卷逐项澄清，合作后加强监测频率
- **D 级**：当前存在任何一项硬性失信 / 限高 / 限出境 / 股权冻结未解除；或关联企业中存在经营异常 / 破产 / 严重违法的主体；或利益冲突明显成立——建议不聘任 / 不合作

## 输出模板

报告统一采用以下章节结构，标题与元信息按示例报告标准格式渲染：

- 章节 1：**执行摘要 · Decision Pack** —— 一句话结论 + 关键判断表（5-7 项） + 推荐 Action 清单（按 T+0 / T+3 / T+7 / T+14 / T+30 紧迫度排序）
- 章节 2：**数据来源与互证方法** —— 列明 MCP 各 Server 采集时间、年报 / 招股书 / 公开报道等外部源、互证命中一览
- 章节 3：**被核查企业基本信息** —— 工商登记快照、实控人链路摘要
- 章节 4：**核心管理层背景核查**（按人逐一成节）
  - 4.X 人员姓名（角色：法代 / 实控人 / 董事长 / 总经理）
    - 个人基本信息（学历、职业起点、主要荣誉）
    - 个人司法风险——现状 × 历史 × 时间轴
    - 任职履历与职业轨迹
    - 关联企业网络（按业务重叠度分层）
    - 利益冲突提示
    - 人员评级及依据
- 章节 5：**关联企业风险地图** —— 人员 × 关联企业 × 风险等级矩阵
- 章节 6：**利益冲突综合研判** —— 合并所有被核查对象的冲突线索做总体判定
- 章节 7：**综合评级与聘任 / 合作建议** —— 整体评级、关键条款建议、投后 / 合作后监测要点
- 章节 8：**数据来源、采集时间戳、免责声明**

每个章节末尾附"深度推演"段，以业务化中文叙述阐释数据背后的判断逻辑，是本 SKILL 区别于简单信息聚合工具的核心价值。

## 参数

- `--person <姓名>`：仅对指定人员做完整画像（默认对法代 / 实控人 / 董事长 / 总经理四人做画像）
- `--depth full`：对全部董监高做完整画像
- `--period <N年>`：历史事件追溯年限，默认 10 年
- `--format md|docx|pptx`：输出格式，默认 Markdown；docx 为专业排版投委会档案格式；pptx 为一页摘要

## 边界与免责

本 SKILL 基于企查查 MCP 公开工商 + 司法数据生成，不包含非公开的征信、税务、反洗钱内部数据库。

出境限制状态、国际制裁清单（OFAC / UN / EU）、PEP 名单筛查不在 qcc-executive 工具覆盖范围内 —— SKILL 报告中的 PEP / 制裁判断仅依赖公开信息启发式推断，正式合规场景应配合企业内部合规系统或第三方制裁筛查工具（World-Check / Dow Jones 等）完成。

同名误查在双参数锚定下已大幅降低，但当被核查对象身份证号 / 生日未在 MCP 中开放时，系统仅能以"企业名 + 姓名"做关联。出现职务、任职时间、关联企业三条线索相互矛盾时，须由人工交叉确认。

关键人事决策（聘任、投资、重大合作）前应结合面试、第三方背调、人工验证完成综合判断。本 SKILL 输出属决策支持材料，不构成最终决策依据。

---

**SKILL 版本**：v2.0（MCP V2.0 升级版）
**适配 MCP 版本**：146 工具 / 6 Server 全量版（2026-04-23 发布）
**所需 Server**：qcc-company（必选）、qcc-executive（必选）、qcc-history（强烈建议）、qcc-risk（建议）
