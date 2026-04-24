# MCP 字段映射表 · V1.0

> 记录"报告章节字段 ← MCP 工具"的对应关系。build_docx.py 按此表取数渲染。MCP 未返回即留空，不生成占位。

## §1 公司概况

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 企业名称 | `qcc-company.get_company_profile` | `Name` |
| 统一社会信用代码 | `qcc-company.get_company_profile` | `CreditCode` |
| 成立日期 | `qcc-company.get_company_profile` | `StartDate` |
| 注册资本 | `qcc-company.get_company_profile` | `RegistCapi` |
| 实缴资本 | `qcc-company.get_company_registration_info` | `RecCap` |
| 经营期限 | `qcc-company.get_company_registration_info` | `TermEnd` |
| 企业类型 | `qcc-company.get_company_profile` | `EconKind` |
| 行业 | `qcc-company.get_company_profile` | `Industry` |
| 经营状态 | `qcc-company.get_company_profile` | `Status` |
| 登记机关 | `qcc-company.get_company_registration_info` | `BelongOrg` |
| 纳税人识别号 | `qcc-company.get_tax_invoice_info` | `TaxNumber` |

## §2 注册资本变更轨迹

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 历次注册资本变更记录 | `qcc-company.get_change_records` (筛 `ProjectName=注册资本`) | `BeforeContent` / `AfterContent` / `ChangeDate` |
| 历史注册资本（更完整） | `qcc-history.get_historical_registration` | `RegistCapi` 时间序列 |
| 币种 | `qcc-company.get_company_profile` | `RegistCapiCurrency` |

## §3 名称变更时间线

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 历次名称变更 | `qcc-company.get_change_records` (筛 `ProjectName=名称`) | `BeforeContent` / `AfterContent` / `ChangeDate` |
| 历史名称（更完整） | `qcc-history.get_historical_registration` | `Name` 时间序列 |

## §4 股权演变

### §4.1 注资与股东出资

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 当前股东列表 | `qcc-company.get_shareholder_info` | `Partners[]` |
| 股东认缴金额 | `qcc-company.get_shareholder_info` | `Partners[].SubConAm` |
| 股东实缴金额 | `qcc-company.get_shareholder_info` | `Partners[].RealConAm` |
| 出资方式 | `qcc-company.get_shareholder_info` | `Partners[].FundedRatio` 和 `FundType` |
| 出资时间 | `qcc-company.get_shareholder_info` | `Partners[].FundedTime` |

### §4.2 设立时股东（历史）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 设立时股东 | `qcc-history.get_historical_shareholders` (最早期记录) | `Partners[]` at `StartDate` |

### §4.3 大股东更替

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 股东变更历史 | `qcc-history.get_historical_shareholders` | 时间序列 `Partners[]` |
| 股权变更登记 | `qcc-company.get_change_records` (筛 `ProjectName=股东` 或 `股权`) | `BeforeContent` / `AfterContent` |
| 合伙企业/持股平台穿透 | 递归调用 `qcc-company.get_shareholder_info`（最多 3 层） | 同上 |

### §4.4 实控人认定（条件启用）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 实际控制人 | `qcc-company.get_actual_controller` | `Name` / `ControlRatio` |
| 受益人列表 | `qcc-company.get_beneficial_owners` | `BeneficialOwners[]` |
| 实控人反查企业 | `qcc-executive.get_personnel_beneficial_owner` | `ControlledCompanies[]` |

### §4.6 申报前 12 月新增股东（仅上市档 / Pre-IPO）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 12 月内股东变更 | `qcc-history.get_historical_shareholders` (筛最近 12 月) | 新增/退出记录 |
| 同期融资轮次 | `qcc-operation.get_financing_records` (筛最近 12 月) | `FinancingRound[]` |

## §5 经营轨迹

### §5.1 经营范围变更

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 经营范围变更 | `qcc-company.get_change_records` (筛 `ProjectName=经营范围`) | `BeforeContent` / `AfterContent` |

### §5.2 分支机构与行政许可

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 分支机构 | `qcc-company.get_branches` | `Branches[]` |
| 对外投资 | `qcc-company.get_external_investments` | `InvestCompanies[]` |
| 行政许可现状 | `qcc-operation.get_administrative_license` | `AdminLicense[]` |
| 行政许可历史 | `qcc-history.get_historical_admin_license` | 时间序列 |
| 资质证书 | `qcc-operation.get_qualifications` | `Qualifications[]` |
| 电信许可 | `qcc-operation.get_telecom_license` | `TelecomLicense[]` |
| 荣誉资质 | `qcc-operation.get_honor_info` | `Honors[]` |

### §5.3 风险信息与注销

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 经营异常 | `qcc-risk.get_business_exception` | `Exceptions[]` |
| 税务异常 | `qcc-risk.get_tax_abnormal` | `TaxAbnormal[]` |
| 欠税 | `qcc-risk.get_tax_arrears_notice` | `TaxArrears[]` |
| 简易注销 | `qcc-risk.get_simple_cancellation_info` | `SimpleCancel` |
| 清算信息 | `qcc-risk.get_liquidation_info` | `Liquidation` |

### §5.4 董监高与治理（条件启用，融资/上市档）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 现任董监高 | `qcc-company.get_key_personnel` | `Employees[]` |
| 董监高历任职位 | `qcc-executive.get_personnel_positions` | `Positions[]` |
| 法人变更 | `qcc-history.get_historical_legal_rep` | 时间序列 |

### §5.5 关联方网络（条件启用，融资/上市档）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 关键人控制的其他企业 | `qcc-executive.get_personnel_controlled_companies` | `ControlledCompanies[]` |
| 关键人的其他关联企业 | `qcc-executive.get_personnel_relevant_companies`（V1.8） | `RelevantCompanies[]` |
| 参股/子公司 | `qcc-company.get_external_investments` | `InvestCompanies[]` |

### §5.6 处罚与担保（条件启用）

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 行政处罚 | `qcc-risk.get_administrative_penalty` | `Penalties[]` |
| 环保处罚 | `qcc-risk.get_environmental_penalty` | `EnvPenalties[]` |
| 严重违法 | `qcc-risk.get_serious_violation` | `Violations[]` |
| 失信被执行人 | `qcc-risk.get_dishonest_info` | `Dishonest[]` |
| 限制消费 | `qcc-risk.get_high_consumption_restriction` | `HighConsumption[]` |
| 股权冻结 | `qcc-risk.get_equity_freeze` | `EquityFreeze[]` |
| 股权质押 | `qcc-risk.get_equity_pledge_info` | `EquityPledge[]` |
| 动产抵押 | `qcc-risk.get_chattel_mortgage_info` | `ChattelMortgage[]` |
| 对外担保 | `qcc-risk.get_guarantee_info` | `Guarantees[]` |

## §6 地址变迁

| 字段 | MCP 工具 | 返回字段 |
|---|---|---|
| 当前注册地址 | `qcc-company.get_company_profile` | `Address` |
| 注册地址变更 | `qcc-company.get_change_records` (筛 `ProjectName=地址` 或 `住所`) | `BeforeContent` / `AfterContent` |
| 历史注册地址 | `qcc-history.get_historical_registration` | `Address` 时间序列 |
| 通信地址 | `qcc-company.get_contact_info` | `ContactAddress` |
| 经营场所 | `qcc-company.get_company_registration_info` | `OperAddr` |

## §7 总结

聚合前 6 章数据，按以下原则生成：

| 要素 | 来源 | 说明 |
|---|---|---|
| 整体评价 | 前 6 章聚合 | clean_baseline / recovered / evasive_high_risk 三档 |
| 股权清洁度 | §4 股东稳定性 + §5.6 股权冻结/质押 | — |
| 经营稳定度 | §5 许可续期 + §5.3 异常记录 | — |
| 成长轨迹 | §2 注册资本 + §3 名称 + §6 地址 变更频率 | — |
| 财务摘要（上市档） | `qcc-operation.get_financial_key_indicators` | 利润/资产负债/现金流/每股/盈利/偿还能力 6 类 |

## 字段来源标签格式

每个渲染字段需附来源标签（由 build_docx 自动处理）：

```
[来源: qcc-company.get_shareholder_info · snapshot=2026-04-20]
```

对多源聚合字段（如"实控人"），标签可列出所有依赖工具：

```
[来源: qcc-company.get_actual_controller + qcc-company.get_beneficial_owners · snapshot=2026-04-20]
```

## 字段缺失处理

- **完全缺失**（MCP 返回空）：该行 / 该字段不渲染
- **部分缺失**（某字段为 null）：该字段不显示，不生成"未披露"文字
- **整节缺失**（所有字段空）：整节不出现于报告

**绝对不做**：不得补写"经查询暂无"、"本次未披露"、"待补充"等占位文字（这违反 V1.0 零材料负担原则）
