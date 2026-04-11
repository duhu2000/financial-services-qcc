---
name: kyb-verification
description: >
  金融机构KYB（Know Your Business）核验Skill - 标准版。
  专为银行、券商、信托等金融机构设计，实现企业客户开户、授信、尽调时的主体核验。

  核心功能：
  - 实体锚定：企业名称与注册信息验证
  - 工商信息核验：注册资本、法定代表人、股东结构比对
  - 风险扫描：司法风险、经营异常、行政处罚等风险识别
  - 受益所有人识别：股权穿透识别实际控制人
  - 关联关系排查：集团客户、隐性关联识别

  适用场景：企业开户KYB、信贷授信前调查、存量客户年检、反洗钱客户尽调。

  使用方式：/kyb-verification 企业名称 [统一社会信用代码]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services
  version: "1.0"
  plugin-commands: "/kyb-verification"
  mcp-integrations: "Web Search, Companies House, Creditsafe"
  industry: "Financial Services - Banking/Securities/Trust"
---

## UNIVERSAL RULES

- **NEVER** 仅凭客户提供的信息完成KYB核验——**必须**通过独立数据源验证
- **NEVER** 忽视注册资本实缴与认缴的差异
- **NEVER** 将存在股权冻结、失信、被执行的企业直接评级为"低风险"
- **ALWAYS** 明确标注数据时效性和数据来源
- **ALWAYS** 对疑似异常信息触发人工复核提示

## MANDATORY OUTPUT HEADER

```
================================================================
KYB核验报告 - 标准版
================================================================
任务编号:    [自动生成]
核验企业:    [企业全称]
核验时间:    [YYYY-MM-DD HH:MM:SS]
数据来源:    Web Search / Companies House / Creditsafe
核验状态:    [通过/异常/高风险 - 需人工复核]
----------------------------------------------------------------
```

## KYB核验工作流 (4阶段)

### Phase 1: 实体锚定与基础信息核验

**目标**: 确认企业主体真实存在，申请材料与官方登记信息一致

**标准数据源**: Companies House (UK), Web Search, Creditsafe

### Phase 2: 股权结构与受益所有人识别

**目标**: 识别企业实际控制人及股权结构

**方法**: 公开股权登记信息 + 企业年报

### Phase 3: 风险信号扫描

**目标**: 识别企业风险信号

**风险类型**: 司法风险、经营异常、行政处罚、股权冻结

### Phase 4: 关联关系排查

**目标**: 识别集团客户、隐性关联

## 风险评级

| 评级 | 描述 | 建议 |
|------|------|------|
| A | 低风险 | 标准尽职调查 |
| B | 中风险 | 增强尽职调查 |
| C | 高风险 | 高级管理层审批 |
| D | 极高风险 | 拒绝开户/授信 |

## NEVER DO THESE

- NEVER assign KYB rating without independent verification
- NEVER rely solely on customer-provided documents
- NEVER fabricate verification data
- ALWAYS flag incomplete verifications for manual review

ALL OUTPUTS REQUIRE REVIEW BY A QUALIFIED PROFESSIONAL.
