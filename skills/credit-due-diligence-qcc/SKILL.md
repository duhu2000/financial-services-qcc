---
name: credit-due-diligence-qcc
description: >
  授信尽调报告 SKILL · 企查查 MCP V2.0 增强版。
  信贷审批放款前的全维度企业尽调工具。输入目标企业全称后，自动完成工商核验、真实财务底盘、司法风险扫描、信用修复追溯、实控人个人风险五位一体的授信风险画像，输出可直接归档的授信决策底稿。

  核心能力：
  - 真实财务底盘：`get_financial_data` 首次引入授信场景，直接返回 3 年完整财报（资产负债率 / 速动比率 / 所有者权益 / 经营现金流），告别旧版仅靠事件信号推断偿债
  - 信用修复追溯：qcc-history 14 个历史风险工具识别"修复型主体 vs 连年失信型"，对评级起决定性作用
  - 实控人 × 法代个人兜底能力评估：qcc-executive 核心工具快扫，识别"企业清洁、实控人出险"的隐性风险
  - 授信评级 × 建议授信额度 × 风险缓释条款：输出可直接进入信贷审批委员会的决策材料

  适用场景：银行对公贷款审批 / 供应链金融授信 / 融资租赁风控 / 保理业务准入 / 流贷 × 项目贷 × 并购贷预审。

  使用方式：/credit-due-diligence 企业名称 [--amount 授信金额] [--tenor 授信期限] [--type 流贷|项目贷|并购贷] [--format md|docx|pptx]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP V2.0)
  version: "2.0"
  plugin-commands: "/credit-due-diligence"
  mcp-integrations: "qcc-company, qcc-risk, qcc-history, qcc-executive"
  industry: "Financial Services - Banking / Credit / SCF"
---

# 授信尽调报告 · 企查查 MCP V2.0 增强版

## SKILL 定位

本 SKILL 服务于银行对公贷款审批、供应链金融授信、融资租赁风控、保理业务准入等场景的放款前企业尽调需求。输入目标企业全称或统一社会信用代码后，SKILL 自动串联 qcc-company / qcc-risk / qcc-history / qcc-executive 四大 MCP Server，执行"工商核验 × 真实财务底盘 × 司法风险扫描 × 信用修复追溯 × 实控人个人风险"五位一体的授信画像，最终输出可直接归档的标准化授信尽调底稿。

相对 V1.0 版本的最大跃迁在于两点：第一，`get_financial_data` 让授信评估第一次能拿到真实的资产负债率 / 速动比率 / 所有者权益等硬指标，从"靠事件信号推断"升级为"有数据可算"；第二，qcc-history 的 14 个历史风险工具让 SKILL 能够识别"曾经出险但已履行"的修复型主体与"连年失信"的高危主体，这对评级阈值的设定具有决定性意义。

## MCP 依赖与配置

必选：
- `qcc-company`（企业基座）—— 工商登记、股东、实控人、对外投资、**get_financial_data**
- `qcc-risk`（风控大脑）—— 失信、被执行、限高、终本、股权冻结、股权质押、动产抵押

强烈建议：
- `qcc-history`（历史存档）—— 识别信用修复模式，影响评级阈值
- `qcc-executive`（人员画像）—— 法代 + 实控人个人画像，识别"企业清洁 × 个人出险"的隐性风险

## 通用执行原则

**第一，财务硬指标先行，事件信号为辅。** V2.0 有了真实财报数据后，偿债能力评估的主路径是"资产负债率 / 流动比率 / 速动比率 / 有息负债 / EBITDA"五项核心比率，司法事件仅作为交叉验证。如果 `get_financial_data` 返回空（非上市小微），SKILL 需明示"无直接财务数据"并在评级上下调一级做保守处理。

**第二，历史修复必须加权评估。** 5 年内的历史失信或被执行即便已履行，仍须在评级中起保守作用（相对无历史记录的主体下调半级）；10 年以上的历史事件可归入"历史标注"层，不触发评级调整。

**第三，实控人个人兜底单独评估。** 企业授信的最后一条防线是实控人个人偿债能力与其他关联企业的资产池。凡原告债权金额超过企业近 3 年累计净利润的情境，均须对实控人做完整个人画像扫描，不得省略。

**第四，授信金额与风险敞口必须对比注册资本。** 拟授信金额占注册资本比例超过 20% 即需引发内部授信委员会特别审议；超过 50% 原则上不建议普通流贷，改走项目贷或增加担保。

**第五，数据时效明示。** 所有 MCP 数据均须附采集时间戳。授信决策前 48 小时内须复核一次企业主体侧的重要负面信号（新增失信 / 限高 / 被执行 / 经营异常等）。

## 工作流

### 维度一：主体工商核验与实控人穿透

工具链：
- `mcp__qcc-company__get_company_registration_info` — 工商登记信息（全称、USCC、法代、成立日期、注册资本、登记状态）
- `mcp__qcc-company__verify_company_accuracy` — 企业名称 + 法代 + USCC 三项匹配核验
- `mcp__qcc-company__get_shareholder_info` — 股东结构
- `mcp__qcc-company__get_actual_controller` — 实际控制人穿透链路
- `mcp__qcc-company__get_key_personnel` — 主要人员名单（为维度五铺垫）

产出：《主体身份档案》——企业全称、USCC、法代、成立年限、登记状态、注册资本与实缴率、股权结构简图、实控人识别。

### 维度二：真实财务底盘（V2.0 核心新能力）

工具链：
- `mcp__qcc-company__get_financial_data` —— **V2.0 新工具**，返回 3 年完整财报（利润表 + 资产负债表 + 现金流量表 + 盈利/偿还/营运/成长能力四类比率）
- `mcp__qcc-company__get_annual_reports` —— 企业年报（作为 `get_financial_data` 的补充）
- `mcp__qcc-company__get_tax_invoice_info` —— 税号信息（为税务合规性铺垫）

核心偿债比率矩阵：

| 指标 | 行业正常值 | 警戒线 | 致命线 |
|------|-----------|-------|-------|
| 资产负债率 | < 70% | 70-90% | > 100%（资不抵债） |
| 流动比率 | > 1.5 | 1.0-1.5 | < 1.0 |
| 速动比率 | > 1.0 | 0.5-1.0 | < 0.3 |
| 有息负债 / EBITDA | < 3 倍 | 3-5 倍 | > 5 倍 |
| 经营现金流 | 正 | 微正或微负 | 持续负 |

分析要点：任何一项触及致命线即直接触发 D 级评级。三项以上触及警戒线则下调至少一级。成长能力指标（营收同比 / 总资产同比）若连续两年为负，授信额度建议不超过其近 3 年平均净利润的 50%。

### 维度三：司法风险扫描

工具链（当前层）：
- `mcp__qcc-risk__get_dishonest_info` — 失信被执行人
- `mcp__qcc-risk__get_judgment_debtor_info` — 被执行人
- `mcp__qcc-risk__get_high_consumption_restriction` — 限制高消费
- `mcp__qcc-risk__get_terminated_cases` — 终本案件
- `mcp__qcc-risk__get_equity_freeze` — 股权冻结
- `mcp__qcc-risk__get_equity_pledge_info` — 股权出质
- `mcp__qcc-risk__get_chattel_mortgage_info` — 动产抵押
- `mcp__qcc-risk__get_land_mortgage_info` — 土地抵押
- `mcp__qcc-risk__get_tax_arrears_notice` — 欠税公告
- `mcp__qcc-risk__get_business_exception` — 经营异常

分析要点：

- 当前失信 1 条即触发 D 级；当前限高生效直接触发 C 级
- 股权出质 + 股权冻结是"融资已枯竭"信号，需在授信额度中相应扣减
- 欠税公告是"税务合规瑕疵"信号，影响税收优惠资格判定
- 对外担保余额（`get_guarantee_info`）须作为表外负债纳入总负债计算

### 维度四：信用修复追溯（V2.0 新能力）

工具链（历史层）：
- `mcp__qcc-history__get_historical_dishonest` — 历史失信（已移出）
- `mcp__qcc-history__get_historical_judgment_debtor` — 历史被执行
- `mcp__qcc-history__get_historical_high_consumption_ban` — 历史限高
- `mcp__qcc-history__get_historical_terminated_cases` — 历史终本
- `mcp__qcc-history__get_historical_equity_freeze` — 历史股权冻结
- `mcp__qcc-history__get_historical_tax_arrears` — 历史欠税
- `mcp__qcc-history__get_historical_business_exception` — 历史经营异常
- `mcp__qcc-history__get_historical_admin_penalty` — 历史行政处罚

分析要点（5 种偿债模式识别）：

- **模式 A · 始终清洁型**（10 年零失信零被执行）：授信评级上浮半级
- **模式 B · 修复型**（5-10 年前曾出险但已修复 + 近 3 年清洁）：维持标准评级
- **模式 C · 间歇失信型**（每 2-3 年一轮）：评级下调一级
- **模式 D · 连年失信型**（近 5 年每年都有新增失信）：直接触发 D 级
- **模式 E · 集中爆发型**（近 12-24 月突发）：进入增强监测 + 评级至少 C 级

### 维度五：实控人 × 法代个人风险

工具链（对法代和实控人分别扫描）：
- `mcp__qcc-executive__get_personnel_dishonest` — 个人失信
- `mcp__qcc-executive__get_personnel_high_consumption_ban` — 个人限高
- `mcp__qcc-executive__get_personnel_judgment_debtor` — 个人被执行
- `mcp__qcc-executive__get_personnel_exit_restriction` — 个人限制出境
- `mcp__qcc-executive__get_personnel_controlled_companies` — 个人其他控制企业
- `mcp__qcc-executive__get_personnel_investments` — 个人对外投资
- `mcp__qcc-executive__get_personnel_historical_dishonest` — 个人历史失信

分析要点：

- 实控人 / 法代任何一人当前失信直接触发 D 级
- 实控人限制出境是"跑路风险"最强信号——直接 D 级 + 拒绝授信
- 实控人控制的其他企业如有 3 家以上处于失信 / 被执行状态，整个授信建议重新评估：该实控人存在"连环担保、互保"风险
- 如法代与实控人为不同自然人，法代若为"职业清算人型"（MCP 零负面 + 任职时间短），说明企业可能处于清算或壳化阶段，评级至少下调两级

## 综合授信评级 × 建议授信额度 × 风险缓释

### 评级体系（A/B/C/D 四级）

| 评级 | 核心标准 | 授信建议 |
|------|---------|---------|
| **A 级** | 财务五项比率全部达标 + 无任何当前司法风险 + 实控人清洁 + 历史清洁或已修复 10 年以上 | 可正常授信，额度上限为近 3 年平均净利润 × 3 |
| **B 级** | 财务一项达警戒线（非致命）+ 近 3 年清洁 + 历史有已修复事件 + 实控人清洁 | 可授信但加强监测，额度为 A 级的 60-80%，增加一道风险缓释 |
| **C 级** | 财务两项以上警戒线 或 历史间歇失信 或 实控人历史已修复事件 | 谨慎授信，要求强担保（土地抵押 / 保证金 / 应收账款质押），额度为 A 级的 30-50% |
| **D 级** | 任何致命线触发 或 当前失信 / 限高 / 资不抵债 或 实控人出险 | **不建议授信**，或仅做担保类短期业务 |

### 授信额度建议公式

```
基础额度 = MIN(
  近 3 年平均净利润 × 3,
  净资产 × 30%,
  年营收 × 10%
)

调整后额度 = 基础额度 × 评级系数
  评级系数：A = 1.0 / B = 0.7 / C = 0.4 / D = 0 或担保类
```

### 风险缓释条款建议

A 级：可信用贷款，仅需基础财务承诺条款
B 级：要求实控人个人连带责任保证 + 关键财务承诺（资产负债率上限、对外担保余额上限）
C 级：要求土地抵押 / 应收账款质押 + 实控人连带责任 + 交叉违约条款 + 财务季报
D 级：放弃信用类授信，仅做全额保证金业务或不开展

## 输出模板

- 章节 1：**执行摘要 · Decision Pack**（评级 + 建议授信额度 + 关键风险信号 + T+0/T+3/T+7 Action）
- 章节 2：数据来源与互证方法
- 章节 3：主体身份档案
- 章节 4：**真实财务底盘**（`get_financial_data` 3 年对比 + 核心比率矩阵）
- 章节 5：司法风险扫描（当前层 × 历史层双层）
- 章节 6：信用修复追溯与偿债模式识别
- 章节 7：实控人与法代个人风险
- 章节 8：综合评级 × 授信额度 × 风险缓释条款
- 章节 9：数据来源、采集时间戳、免责声明

## 参数

- `--amount <金额>`：拟授信金额（必填）—— 用于授信敞口 / 注册资本比率测算
- `--tenor <期限>`：授信期限（1 年 / 3 年 / 5 年）—— 长期限授信对资产负债率警戒线更严格
- `--type <类型>`：授信类型（流贷 / 项目贷 / 并购贷 / 供应链金融）
- `--format md|docx|pptx`：输出格式，默认 md

## 边界与免责

本 SKILL 基于企查查 MCP 公开工商 + 财务 + 司法数据生成。`get_financial_data` 返回的财务数据来源于企业年报披露，对非上市小微企业可能返回空，此时 SKILL 会明示并保守处理。

授信决策涉及宏观经济、行业周期、政策导向等多维度因素，本 SKILL 仅提供基于单企业主体侧的尽调材料，不构成对市场风险、利率风险、汇率风险等宏观维度的判断。

最终授信决策应由所在机构的信贷审批委员会 / 风险管理委员会综合评审，本 SKILL 输出仅为决策支持材料。

---

**SKILL 版本**：v2.0（MCP V2.0 升级版）
**适配 MCP 版本**：146 工具 / 6 Server 全量版
**所需 Server**：qcc-company（必选）、qcc-risk（必选）、qcc-history（强烈建议）、qcc-executive（强烈建议）
