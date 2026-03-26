---
name: kyb-verification-qcc
description: >
  金融机构KYB（Know Your Business）自动化核验Skill - 企查查MCP增强版。
  专为银行、券商、信托等金融机构设计，实现企业客户开户、授信、尽调时的自动化主体核验。

  核心功能：
  - 实体锚定：统一社会信用代码与企业名称交叉验证
  - 工商信息核验：注册资本、法定代表人、股东结构实时比对
  - 风险扫描：司法风险、经营异常、行政处罚、股权冻结等18类风险
  - 受益所有人识别：股权穿透自动识别实际控制人
  - 关联关系排查：集团客户、隐性关联、一致行动人识别

  适用场景：企业开户KYB、信贷授信前调查、存量客户年检、反洗钱客户尽调。

  使用方式：/kyb-verification-qcc 企业名称 [统一社会信用代码]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP)
  version: "2.0"
  plugin-commands: "/kyb-verification-qcc"
  mcp-integrations: "QCC MCP (Company/Risk/IPR/Operation)"
  industry: "Financial Services - Banking/Securities/Trust"
---

## MCP 配置要求

**⚠️ 重要：使用本SKILL前，必须确保企查查MCP服务器已配置**

### 检查清单：
1. ✅ `~/.claude/.mcp.json` 文件存在且配置正确
2. ✅ `QCC_MCP_API_KEY` 环境变量已设置
3. ✅ Claude Code 已重启加载MCP配置

### 配置方法：
```bash
# 1. 创建 MCP 配置文件
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": { "Authorization": "Bearer ${QCC_MCP_API_KEY}" }
    },
    "qcc-risk": {
      "url": "https://agent.qcc.com/mcp/risk/stream",
      "headers": { "Authorization": "Bearer ${QCC_MCP_API_KEY}" }
    }
  }
}
EOF

# 2. 设置 API Key
export QCC_MCP_API_KEY="your_api_key_here"

# 3. 重启 Claude Code
```

详见文档：https://github.com/duhu2000/financial-services-qcc/blob/main/docs/MCP_CONFIGURATION.md

---

## UNIVERSAL RULES (适用于所有KYB任务)

- **NEVER** 仅凭客户提供的信息完成KYB核验——**必须**通过企查查MCP工具获取官方数据
- **NEVER** 使用网页搜索代替企查查MCP——所有中国企业数据必须通过 `qcc-company` / `qcc-risk` 等MCP工具获取
- **NEVER** 忽视注册资本实缴与认缴的差异——标注"认缴"并提示实缴情况未知
- **NEVER** 将存在股权冻结、失信、被执行的企业直接评级为"低风险"
- **ALWAYS** 明确标注数据时效性和数据来源——所有企查查数据必须标注查询时间
- **ALWAYS** 对疑似异常信息触发人工复核提示——包括但不限于：近期股权变更、地址频繁变更、经营范围重大调整
- **FOR CHINESE ENTERPRISES: ALWAYS use QCC MCP as primary data source** —— Companies House和Creditsafe对中国企业无覆盖

## MANDATORY OUTPUT HEADER

每个KYB核验输出必须以以下格式开头：

```
================================================================
KYB核验报告 - 企查查MCP增强版
================================================================
任务编号:    [自动生成]
核验企业:    [企业全称]
统一社会信用代码: [91350100M0001YHXXX]
核验时间:    [YYYY-MM-DD HH:MM:SS]
数据来源:    企查查MCP (企业基座/风控大脑/知产引擎/经营罗盘)
核验状态:    [通过/异常/高风险 - 需人工复核]
----------------------------------------------------------------
```

## KYB核验工作流 (4阶段)

### Phase 1: 实体锚定与基础信息核验 (Entity Verification)

**目标**: 确认企业主体真实存在，申请材料与官方登记信息一致

**企查查MCP调用**:
1. **企业登记信息查询** (qcc_company/get_company_registration_info)
   - 核验企业名称、统一社会信用代码是否匹配
   - 获取法定代表人、注册资本、成立日期、登记状态

2. **企业联系方式查询** (qcc_company/get_contact_info)
   - 获取工商登记电话、邮箱、官网
   - 与客户提供的联系方式比对

**核验要点**:
| 字段 | 客户提供 | 企查查官方 | 核验结果 |
|------|---------|-----------|---------|
| 企业名称 | [ ] | [ ] | [一致/不一致] |
| 统一社会信用代码 | [ ] | [ ] | [一致/不一致] |
| 法定代表人 | [ ] | [ ] | [一致/不一致] |
| 注册资本 | [ ] | [ ] | [一致/不一致] |
| 成立日期 | [ ] | [ ] | [一致/不一致] |
| 登记状态 | [ ] | [ ] | [存续/注销/吊销] |
| 注册地址 | [ ] | [ ] | [一致/不一致] |

**异常标记**:
- 🚨 **CRITICAL**: 企业已注销、吊销、列入严重违法
- ⚠️ **WARNING**: 法定代表人近期变更（6个月内）、注册地址变更
- ℹ️ **INFO**: 注册资本认缴制（非实缴）

### Phase 2: 股权结构与受益所有人识别 (UBO Identification)

**目标**: 识别实际控制人，穿透识别受益所有人

**企查查MCP调用**:
1. **股东信息查询** (qcc_company/get_shareholder_info)
   - 获取前10大股东及持股比例
   - 识别控股股东（持股>50%或相对控股）

2. **对外投资查询** (qcc_company/get_external_investments)
   - 了解企业对外投资情况
   - 识别集团关联关系

3. **主要人员查询** (qcc_company/get_key_personnel)
   - 获取董事、监事、高管名单
   - 识别关键管理人员

**受益所有人识别规则** (根据央行《关于加强反洗钱客户身份识别有关工作的通知》)：
```
受益所有人判定标准：
├─ 直接或者间接拥有25%以上股权或表决权的自然人
├─ 通过人事、财务等其他方式对公司进行控制的自然人
└─ 公司的高级管理人员（如无法识别前述两类）
```

**输出格式**:
```
股权结构分析:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
控股股东:        [股东名称] ([持股比例]%)
实际控制人:      [姓名] (通过[直接持股/间接控股/协议控制])
受益所有人:      [姓名1], [姓名2] (各持股[X]%)

股权穿透路径:
├─ [实控人姓名] → [持股平台/公司] → [目标企业] ([X]%)
└─ [其他自然人] → [直接持股] → [目标企业] ([X]%)

关联关系排查:
├─ 集团关联企业: [N]家
├─ 一致行动人:   [已识别/未识别]
└─ 隐性关联:     [需关注/无异常]
```

### Phase 3: 风险扫描与合规审查 (Risk Screening)

**目标**: 全面扫描18类风险，识别潜在合规风险

**企查查MCP调用 - 司法风险** (qcc_risk Server):
```
风险类别                调用工具                              优先级
─────────────────────────────────────────────────────────────────
🔴 CRITICAL (< 4小时)
├─ 失信信息             get_dishonest_info                    必须核查
├─ 被执行人             get_judgment_debtor_info              必须核查
├─ 限制高消费           get_high_consumption_restriction      必须核查
├─ 破产重整             get_bankruptcy_reorganization         必须核查
├─ 股权冻结             get_equity_freeze                     必须核查

🔴 HIGH (< 24小时)
├─ 经营异常             get_business_exception                必须核查
├─ 严重违法             get_serious_violation                 必须核查
├─ 终本案件             get_terminated_cases                  建议核查
├─ 司法拍卖             get_judicial_auction                  建议核查

🟡 MEDIUM (< 7天)
├─ 行政处罚             get_administrative_penalty            抽样核查
├─ 环保处罚             get_environmental_penalty             抽样核查
├─ 税收违法             get_tax_violation                     抽样核查
├─ 欠税公告             get_tax_arrears_notice                抽样核查
├─ 股权出质             get_equity_pledge_info                建议核查
├─ 动产抵押             get_chattel_mortgage_info             建议核查
```

**风险扫描输出**:
```
风险扫描摘要:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 CRITICAL 风险: [N]项
├─ [风险类型1]: [描述] [日期]
└─ [风险类型2]: [描述] [日期]

🔴 HIGH 风险: [N]项
├─ [风险类型1]: [描述] [日期]
└─ ...

🟡 MEDIUM 风险: [N]项
├─ [风险类型1]: [描述] [日期]
└─ ...

风险综合评级: [高风险/中风险/低风险]
建议措施:     [禁止准入/审慎准入/加强监测/正常准入]
```

### Phase 4: 经营健康度与持续经营能力 (Operational Health)

**目标**: 评估企业持续经营能力，识别空壳公司、僵尸企业

**企查查MCP调用** (qcc_operation Server):
1. **资质证书查询** (get_qualifications)
   - 核查行业特许经营资质
   - 检查资质有效期

2. **行政许可查询** (get_administrative_license)
   - 核查经营许可有效性
   - 识别超范围经营风险

3. **招投标信息查询** (get_bidding_info)
   - 评估业务活跃度
   - 识别业务断崖式下跌

4. **抽查检查记录** (get_spot_check_info)
   - 核查监管检查结果
   - 识别质量问题

5. **新闻舆情查询** (get_news_sentiment)
   - 监控负面舆情
   - 识别声誉风险

**经营健康度评估**:
```
持续经营能力评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
经营活跃度:    [高/中/低/无业务] (近12个月招投标[N]次)
资质有效性:    [全部有效/部分过期/无资质]
监管合规:      [良好/有瑕疵/严重违规]
舆情监控:      [正面/中性/负面[N]条]

KYB综合评级:   [A级-B级-C级-D级]
├─ A级: 正常经营，无风险信号
├─ B级: 轻微异常，可正常准入
├─ C级: 中高风险，需加强尽调
└─ D级: 高风险，建议禁止准入
```

## OUTPUT FORMAT (标准KYB核验报告)

**支持三种格式同时生成：**

```
输出格式 (默认全部生成):
├─ Markdown (.md)     - 可编辑原始文本，便于系统对接
├─ Word (.docx)       - 专业排版，可打印盖章，适合风控审批
└─ PPT (.pptx)        - 一页摘要，适合快速汇报

使用方式:
/kyb-verification-qcc [企业名称] [统一社会信用代码] [--format md]       # 仅生成Markdown
/kyb-verification-qcc [企业名称] [统一社会信用代码] [--format docx]     # 仅生成Word
/kyb-verification-qcc [企业名称] [统一社会信用代码] [--format pptx]     # 仅生成PPT
/kyb-verification-qcc [企业名称] [统一社会信用代码] [--format all]      # 生成全部三种格式（默认）
```

**格式选择建议：**
| 场景 | 推荐格式 | 说明 |
|------|---------|------|
| 授信审批/合规留档 | Word (.docx) | 专业排版，支持打印盖章，风控部门签字 |
| 管理层快速汇报 | PPT (.pptx) | 一页摘要， quadrant 布局，30秒速览风险等级 |
| 系统对接/API传输 | Markdown (.md) | 纯文本，便于数据提取和结构化存储 |
| 综合需求 | All (默认) | 一次生成三种格式，按需使用 |

**文件命名规范：**
```
KYB核验报告-[企业名称]-YYYYMMDD.md
KYB核验报告-[企业名称]-YYYYMMDD.docx
KYB核验报告-[企业名称]-YYYYMMDD.pptx
```

---

### 标准KYB报告模板 (Markdown 格式)

```
================================================================
KYB核验报告 - 企查查MCP增强版
================================================================

-- 第一部分：基础信息核验 --
[Phase 1 输出]

-- 第二部分：股权与受益所有人 --
[Phase 2 输出]

-- 第三部分：风险扫描结果 --
[Phase 3 输出]

-- 第四部分：经营健康度评估 --
[Phase 4 输出]

-- 第五部分：KYB综合结论 --
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KYB核验结论: [通过/有条件通过/不通过]

风险等级:    [A/B/C/D]
准入建议:    [准予开户/审慎准入/禁止准入]

需关注事项:
1. [具体事项1] - 建议措施
2. [具体事项2] - 建议措施

人工复核触发点:
□ 股权结构复杂，需进一步穿透
□ 存在司法风险，需法律审查
□ 经营异常，需解释说明
□ 其他: [说明]

下次复核时间: [建议3个月/6个月/12个月后复检]

================================================================
数据来源: 企查查MCP (65个官方数据源)
核验耗时: [X]秒
报告生成时间: [YYYY-MM-DD HH:MM:SS]
================================================================

免责声明:
本报告基于企查查MCP公开数据生成，仅供内部参考。
关键决策前建议结合实地尽调、客户面签等多维度验证。
```

## NEVER DO THESE

- NEVER 仅凭客户提供的信息完成KYB核验——必须与官方数据交叉验证
- NEVER 对存在失信、被执行记录的企业直接评级为"低风险"
- NEVER 忽视注册资本认缴与实缴的差异——必须明确标注
- NEVER 对空壳公司（无实际经营、无员工、无社保）正常准入
- NEVER 跳过受益所有人识别——这是反洗钱合规的强制要求
- NEVER 忽视集团客户关联关系——可能导致集中度风险
- NEVER 对高风险客户不设置后续监测频率

ALL OUTPUTS REQUIRE REVIEW BY A QUALIFIED COMPLIANCE OFFICER BEFORE USE IN BUSINESS DECISIONS.
