---
name: kyb-verification-qcc
description: >
  KYB 企业核验 SKILL · 企查查 MCP V2.0 增强版。
  金融机构对公客户开户、授信、尽调、年检场景的主体自动化核验工具。输入企业名称或统一社会信用代码后，SKILL 自动完成主体真实性核验、工商信息核验、历史治理稳定性回溯、受益所有人穿透、34 类司法风险扫描，输出符合 FATF / 中国央行 3 号令标准的 KYB 合规底稿。

  核心能力：
  - 主体真实性核验：企业名 + USCC + 法代三项交叉匹配（`verify_company_accuracy`）
  - 工商信息核验：注册资本、法代、股东结构、登记状态实时比对
  - **V2.0 新能力：历史治理稳定性**（qcc-history）—— 历史法代更替轨迹、历史股东变迁、历史注册资本变更，识别"频繁变更"的治理不稳定主体
  - 受益所有人穿透：股权穿透 + `get_beneficial_owners` + UBO 个人画像
  - 34 类司法风险扫描：失信 / 被执行 / 限高 / 股权冻结 / 经营异常 / 税务违法 等全量
  - 关联关系排查：集团客户识别、隐性关联、一致行动人

  适用场景：银行 / 券商 / 信托 / 保险等金融机构的对公开户 KYB、信贷授信前调查、存量客户年检、反洗钱客户尽调。

  使用方式：/kyb-verification-qcc 企业名称 [统一社会信用代码] [--depth standard|full] [--format md|docx|pptx]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP V2.0)
  version: "2.0"
  plugin-commands: "/kyb-verification-qcc"
  mcp-integrations: "qcc-company, qcc-risk, qcc-history, qcc-executive, qcc-operation"
  industry: "Financial Services - Banking / Securities / Trust / Insurance"
---

# KYB 企业核验 · 企查查 MCP V2.0 增强版

## SKILL 定位

本 SKILL 服务于金融机构对公客户全生命周期的主体核验需求——对公开户时的准入 KYB、授信前的背景调查、存量客户的年度体检、反洗钱尽调的主体基础核验。V1.0 已经覆盖了基础工商信息核验 + 18 类司法风险扫描，V2.0 的升级聚焦两个维度：

- **历史治理稳定性**：通过 qcc-history 的 5 个历史工具回溯企业近 10 年的法代更替、股东变迁、注册资本变更、经营范围变化、登记地址变更——这是传统 KYB 的盲区。一家 2 年内更换 3 任法代或频繁变更注册地的企业，即便当前登记状态为"存续"，治理不稳定性本身就是合规红旗。
- **受益所有人穿透深度**：基于 qcc-executive 的人员画像工具，对识别出的每个自然人 UBO 做独立司法画像扫描，真正实现 FATF Recommendation 10 第 3-4 步的深度核验。

## MCP 依赖与配置

必选：
- `qcc-company`（企业基座）—— 工商核验 + 股东 + 实控人 + UBO + 主要人员
- `qcc-risk`（风控大脑）—— 34 类司法风险全覆盖

强烈建议：
- `qcc-history`（历史存档）—— 历史治理稳定性回溯
- `qcc-executive`（人员画像）—— UBO 自然人穿透

可选：
- `qcc-operation`（经营罗盘）—— 经营活跃度补充指标（资质 / 荣誉 / 双随机抽查 / 纳税信用）

## 通用执行原则

**第一，KYB 的起点是"企业名 × USCC × 法代"三项一致性验证。** 任一项不匹配即触发核验失败。客户提供的 USCC 必须与 MCP 返回一致，否则怀疑客户身份造假。

**第二，登记状态为"存续"只是必要条件，不是充分条件。** 一家资不抵债但未清算的企业、一家 12 个月无业务活动的壳公司、一家实控人已被追责的僵尸主体——工商上都可能显示"存续"。KYB 必须结合治理稳定性 × 财务底盘 × 司法风险综合判断"实质存续"。

**第三，治理稳定性必须入表。** 法代 2 年内 ≥ 2 次变更、股东 1 年内 ≥ 2 次变更、注册资本近 3 年减资、注册地址近 2 年 ≥ 2 次变更——任一命中即触发"治理不稳定"标签，授信 / 开户慎重。

**第四，UBO 穿透到自然人是合规硬要求。** 根据中国央行 3 号令，金融机构必须穿透识别受益所有人（持股 25% 以上或通过其他方式实际控制）。对每个 UBO 自然人必须独立做司法画像扫描。

**第五，关联企业合规联动。** UBO 控制的其他企业出现失信 / 经营异常 / 行政处罚等，即便本次申请主体清洁，整个客户关系也须标记"系内合规风险"。

## 工作流

### 维度一：主体真实性 × 工商信息核验

工具链：
- `mcp__qcc-company__verify_company_accuracy` —— 企业名 + 法代 + USCC 三项匹配
- `mcp__qcc-company__get_company_registration_info` —— 工商基础信息（注册资本、成立日期、登记状态、所属地区等）
- `mcp__qcc-company__get_contact_info` —— 联系方式（用于验证客户申请材料的真实性）
- `mcp__qcc-company__get_tax_invoice_info` —— 税号开票信息（一般纳税人资质）

**核验三道红线**（任一触发即拒绝 KYB 通过）：
- 企业名 × USCC × 法代三项任一不匹配
- 登记状态为"吊销 / 注销 / 异常"
- 成立日期在客户申请材料之后

### 维度二：历史治理稳定性（V2.0 新能力）

工具链：
- `mcp__qcc-history__get_historical_registration` —— 曾用名 / 历史注册地址 / 历史经营范围
- `mcp__qcc-history__get_historical_legal_rep` —— 历届法定代表人
- `mcp__qcc-history__get_historical_shareholders` —— 历史股东（已退出）
- `mcp__qcc-history__get_historical_executives` —— 历届高管
- `mcp__qcc-history__get_historical_listing` —— 历史上市 / 挂牌信息

**治理稳定性判定**：

| 指标 | 警戒阈值 | 含义 |
|------|---------|------|
| 法代近 2 年变更次数 | ≥ 2 次 | 治理极不稳定（典型危机企业信号） |
| 股东近 1 年变更次数 | ≥ 2 次 | 控制权频繁转移，可能涉及代持 / 套壳 |
| 注册资本近 3 年变更 | 有减资 | 可能抽逃出资或股东退出 |
| 注册地址近 2 年变更次数 | ≥ 2 次 | 疑似逃避监管或债权人 |
| 曾用名次数 | ≥ 2 次 | 可能涉及"摘牌 + 更名 + 复活"模式 |
| 历史法代数 / 成立年数 | > 0.3 | 治理更替频率过高 |

**判定结论**：
- 触发 ≥ 2 个警戒阈值：**治理不稳定**，KYB 评级下调一级
- 触发 ≥ 4 个警戒阈值：**治理高度不稳定**，KYB 评级下调两级，建议要求客户提供变更说明

### 维度三：受益所有人穿透到自然人

工具链：
- `mcp__qcc-company__get_shareholder_info` —— 股东结构
- `mcp__qcc-company__get_actual_controller` —— 实际控制人
- `mcp__qcc-company__get_beneficial_owners` —— 受益所有人
- `mcp__qcc-executive__get_personnel_beneficial_owner` —— 以自然人为锚反查其 UBO 地位

**UBO 识别三层穿透**：
1. 直接持股 25% 以上的自然人
2. 间接持股（通过中间层）累计 25% 以上的自然人
3. 通过协议 / 投票权 / 管理层任免实际控制的自然人

对每个识别出的 UBO 自然人做简化画像扫描：
- `mcp__qcc-executive__get_personnel_dishonest`
- `mcp__qcc-executive__get_personnel_high_consumption_ban`
- `mcp__qcc-executive__get_personnel_exit_restriction`

任何 UBO 存在当前失信 / 限高 / 限出境 → KYB 评级直接触发"高风险"。

### 维度四：34 类司法风险扫描

工具链（全量）：
- `mcp__qcc-risk__get_dishonest_info` / `get_judgment_debtor_info` / `get_high_consumption_restriction` / `get_terminated_cases` / `get_equity_freeze` / `get_equity_pledge_info` / `get_chattel_mortgage_info` / `get_land_mortgage_info` / `get_business_exception` / `get_tax_arrears_notice` / `get_tax_violation` / `get_administrative_penalty` / `get_environmental_penalty` / `get_serious_violation` / `get_bankruptcy_reorganization` / `get_liquidation_info`
- `mcp__qcc-risk__get_judicial_documents` / `get_case_filing_info` / `get_hearing_notice`（诉讼类）

**分类处置**：

| 风险类别 | KYB 处置 |
|---------|---------|
| 当前失信 / 限高 / 限出境 / 股权冻结 | **拒绝开户 / 准入** |
| 严重违法失信名单 / 经营异常 | **拒绝 + 上报** |
| 破产重整 / 清算 | **拒绝 + 债权申报评估** |
| 税务违法 / 环保处罚 / 行政处罚 | 根据严重程度下调评级 1-2 级 |
| 民事诉讼（作为被告）> 50 件 | 下调评级 1 级 |
| 纳税信用 A 级 + 荣誉记录多 | 上调评级半级 |

### 维度五：关联关系排查

工具链：
- `mcp__qcc-company__get_external_investments` —— 企业对外投资
- `mcp__qcc-company__get_branches` —— 分支机构
- `mcp__qcc-executive__get_personnel_related_companies` —— 实控人其他关联企业
- `mcp__qcc-executive__get_personnel_controlled_companies` —— 实控人控制企业

**排查清单**：
- 同一实控人控制的其他企业是否存在失信 / 破产
- 集团客户识别（如果本客户是大型集团子公司）
- 一致行动人识别（股东之间是否存在隐性协同）
- 隐性关联（业务伙伴 / 历史合作伙伴）

### 维度六：经营活跃度补充指标（可选）

工具链：
- `mcp__qcc-operation__get_qualifications` —— 资质证书
- `mcp__qcc-operation__get_honor_info` —— 荣誉信息
- `mcp__qcc-operation__get_credit_evaluation` —— 政府监管信用评级（纳税信用等级）
- `mcp__qcc-operation__get_random_check` —— **V2.0 新工具**，双随机抽查记录
- `mcp__qcc-operation__get_bidding_info` —— 招投标活动（经营活跃度指标）
- `mcp__qcc-operation__get_recruitment_info` —— 招聘活跃度

**用途**：区分"形式存续但实质空壳"（无资质 / 无荣誉 / 无招投标 / 无招聘）与"正常经营主体"。

## KYB 评级

### 评级体系（A/B/C/D 四级）

| 评级 | 核心标准 | 处置 |
|------|---------|------|
| **A 级** | 主体真实 + 治理稳定 + 无任何当前司法风险 + UBO 清洁 + 经营活跃 | **通过 KYB**，可进入标准业务流程 |
| **B 级** | 主体真实 + 治理稳定 + 无当前致命风险 + 有历史已修复事件 | **通过 KYB**，启动标准监测 |
| **C 级** | 主体真实 + 治理不稳定 或 有当前轻微风险（行政处罚等）| **附条件通过**，要求加强监测 + 定期复核 |
| **D 级** | 主体真实性存疑 或 治理高度不稳定 或 任何一项致命风险命中 | **拒绝 KYB 通过**，不得开户 / 准入 |

## 输出模板

- 章节 1：**KYB 核验结论 · Decision Pack**（评级 + 关键核验结果 + 准入建议 + 后续监测要求）
- 章节 2：数据来源与互证方法
- 章节 3：**主体真实性 × 工商信息核验**（三项一致性验证）
- 章节 4：**历史治理稳定性**（V2.0 新能力）
- 章节 5：受益所有人穿透（自然人级）
- 章节 6：34 类司法风险扫描
- 章节 7：关联关系排查
- 章节 8：经营活跃度补充指标（可选）
- 章节 9：KYB 综合评级 × 准入建议 × 后续监测要求
- 章节 10：数据来源、采集时间戳、免责声明

## 参数

- `--depth <standard|full>`：核查深度。standard（默认）涵盖必选 + 强烈建议工具；full 额外覆盖可选经营活跃度维度
- `--format md|docx|pptx`：输出格式，默认 md；docx 为金融机构合规档案格式；pptx 为一页 KYB 摘要

## 边界与免责

本 SKILL 完成的是"基于公开工商 + 司法 + 财务数据的主体侧 KYB"，不涉及客户身份文件（营业执照、法人身份证、开户许可证等）的实物核验——这部分仍需客户经理线下执行。

UBO 识别基于公开股权信息，如存在未披露的代持、协议控制、一致行动安排等，MCP 无法穿透——这是合规尽调需要配合客户访谈、关联交易审查等手段完成的。

制裁清单命中（OFAC / UN / EU）不在本 SKILL 覆盖范围，须配合专业制裁筛查工具完成。

KYB 是金融机构合规的基础层，通过 KYB 不代表客户可以获得任何业务——后续的授信、反洗钱尽调、反恐怖融资筛查等层层把关仍是必需。

---

**SKILL 版本**：v2.0（MCP V2.0 升级版）
**适配 MCP 版本**：146 工具 / 6 Server 全量版
**所需 Server**：qcc-company（必选）、qcc-risk（必选）、qcc-history（强烈建议）、qcc-executive（强烈建议）、qcc-operation（可选）
