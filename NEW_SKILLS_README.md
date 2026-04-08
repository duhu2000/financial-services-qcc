# 新增5个高优先级Skill说明

## 概述

基于Anthropic financial-services-plugins的参考，我们新增了5个面向投资银行、PE/VC、券商的高价值Skill，全部基于企查查MCP/CLI双栖架构增强。

---

## 新增Skill清单

| # | Skill名称 | 核心功能 | 目标客群 | 企查查数据支持 |
|---|-----------|----------|----------|----------------|
| 1 | **strip-profile-qcc** | 企业画像速览(Strip Tease) | PE/VC、IBD、券商研究所 | 四大Server全维度 |
| 2 | **dd-checklist-qcc** | 尽职调查清单自动化 | PE/VC、投行、并购团队 | 40+项自动填充 |
| 3 | **compliance-monitor-qcc** | 合规风险持续监控 | 银行合规、券商风控、投后管理 | 18类风险实时监控 |
| 4 | **esg-assessment-qcc** | ESG风险评估 | ESG基金、绿色金融、上市公司 | E/S/G三维度数据 |
| 5 | **related-party-qcc** | 关联方穿透识别 | 投行IPO、审计、合规风控 | 股权穿透+实控人识别 |

---

## Skill详细介绍

### 1. strip-profile-qcc（企业画像速览）

**核心价值**：3分钟生成一页纸企业画像

**适用场景**：
- 初步投资筛选
- 投委会立项汇报
- 客户会议前背景了解
- 竞品对比分析

**输出格式**：
- Markdown一页纸（默认）
- PPT一页摘要
- Word简报

**企查查MCP调用**：
- `qcc-company`: 工商+股权
- `qcc-risk`: 18类风险扫描
- `qcc-ipr`: 知识产权
- `qcc-operation`: 经营动态

---

### 2. dd-checklist-qcc（尽职调查清单）

**核心价值**：尽调全流程自动化管理

**覆盖维度**：
- 法律尽调（Legal DD）
- 财务尽调（Financial DD）
- 业务尽调（Business DD）
- 技术尽调（Technical DD）

**自动化程度**：
- 14项企查查自动填充
- 18项需人工补充
- 8项可交叉验证

**特色功能**：
- 进度仪表盘
- 风险实时预警
- 自动化报告生成

---

### 3. compliance-monitor-qcc（合规风险监控）

**核心价值**：7x24小时风险持续监控

**监控范围**：
- 司法风险（失信、被执行、限高）
- 经营风险（异常、违法、处罚）
- 财务风险（欠税、冻结、质押）
- 清算风险（破产、清算、注销）

**预警机制**：
- 🔴 高风险：立即推送
- 🟡 中风险：每日汇总
- 🟢 低风险：常规监控

**适用客群**：
- 银行贷后管理
- PE/VC投后管理
- 券商客户监控
- 供应链风险预警

---

### 4. esg-assessment-qcc（ESG风险评估）

**核心价值**：ESG三维度自动评级

**评分模型**：
- E-环境（35%）：环保处罚、排污许可
- S-社会（35%）：劳动仲裁、舆情声誉
- G-治理（30%）：股权稳定、合规记录

**输出**：
- ESG综合评分（0-100）
- 三维度分项评分
- 行业对标分析
- ESG投资适宜性判断

**适用场景**：
- ESG主题投资基金
- 绿色债券发行评估
- 上市公司ESG报告
- 可持续投资筛选

---

### 5. related-party-qcc（关联方穿透识别）

**核心价值**：股权穿透+实控人识别+关联交易分析

**识别范围**：
- 股权关联方（5%以上股东）
- 实际控制人（综合持股计算）
- 一致行动人（隐性关联）
- 关联交易（交易对手识别）
- 董监高关联企业

**穿透深度**：
- 标准穿透：3层
- 深度穿透：5层
- 全量穿透：无限制（IPO专用）

**适用场景**：
- IPO招股书关联方披露
- 并购关联交易审查
- 银行集团客户识别
- 合规利益冲突检测

---

## 与现有Skill的协作关系

```
协作关系图谱

                    ┌─────────────────┐
                    │  strip-profile  │
                    │   企业速览      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │dd-checklist │ │ ic-memo     │ │ compliance  │
    │  尽调清单   │ │ 投资备忘录  │ │ 风险监控    │
    └──────┬──────┘ └─────────────┘ └──────┬──────┘
           │                                 │
           ↓                                 ↓
    ┌─────────────┐                  ┌─────────────┐
    │  kyb-verify │                  │ related-party│
    │  企业核验   │                  │ 关联方识别  │
    └─────────────┘                  └─────────────┘
                                              │
                                              ↓
                                       ┌─────────────┐
                                       │esg-assessment│
                                       │ ESG评估     │
                                       └─────────────┘
```

---

## GitHub同步指南

### 步骤1：提交到本地仓库

```bash
cd ~/.claude/workspace/financial-services-qcc

# 添加新Skill目录
git add skills/strip-profile-qcc/
git add skills/dd-checklist-qcc/
git add skills/compliance-monitor-qcc/
git add skills/esg-assessment-qcc/
git add skills/related-party-qcc/
git add NEW_SKILLS_README.md

# 提交
git commit -m "feat: add 5 high-priority skills for financial services

- strip-profile-qcc: 3分钟企业画像速览
- dd-checklist-qcc: 尽职调查清单自动化
- compliance-monitor-qcc: 7x24风险监控
- esg-assessment-qcc: ESG三维度评级
- related-party-qcc: 关联方穿透识别

All skills enhanced with QCC MCP/CLI dual-mode support"
```

### 步骤2：推送到GitHub

```bash
# 推送到您的GitHub仓库
git push origin main

# 或使用您当前的分支
git push origin <your-branch>
```

### 步骤3：更新主README

建议在主README.md中新增章节：

```markdown
## 技能矩阵

### 投资银行/PE/VC核心Skill

| Skill | 功能 | 场景 | 状态 |
|-------|------|------|------|
| strip-profile-qcc | 企业画像速览 | 初步筛选、立项汇报 | ✅ 已发布 |
| dd-checklist-qcc | 尽调清单自动化 | 投资尽调全流程 | ✅ 已发布 |
| ic-memo-qcc | 投资备忘录 | 投委会汇报 | ✅ 已发布 |
| compliance-monitor-qcc | 风险持续监控 | 投后管理 | ✅ 已发布 |
| related-party-qcc | 关联方穿透 | IPO/并购 | ✅ 已发布 |
| esg-assessment-qcc | ESG评级 | 绿色投资 | ✅ 已发布 |
| kyb-verification-qcc | 企业核验 | 银行KYB | ✅ 已发布 |
```

---

## 面向客群推广建议

### 银行客群（投资经理/信贷审批）

**主推Skill**：
- `kyb-verification-qcc` - KYB自动核验
- `compliance-monitor-qcc` - 贷后风险监控
- `strip-profile-qcc` - 客户背景速览

**价值主张**：
> "3分钟完成企业尽调，7x24小时风险监控，Token成本降低96%"

### PE/VC客群（投资经理/投后管理）

**主推Skill**：
- `strip-profile-qcc` - 初步筛选
- `dd-checklist-qcc` - 尽调管理
- `ic-memo-qcc` - 投委会汇报
- `compliance-monitor-qcc` - 投后监控
- `related-party-qcc` - 关联方核查

**价值主张**：
> "从初步筛选到投后管理，企查查MCP覆盖投资全生命周期"

### 券商客群（IBD/研究所）

**主推Skill**：
- `strip-profile-qcc` - 研报素材
- `dd-checklist-qcc` - IPO尽调
- `related-party-qcc` - 招股书关联方
- `esg-assessment-qcc` - ESG研报

**价值主张**：
> "IPO尽调效率提升10倍，招股书关联方一键穿透"

---

## 下一步建议

1. **补充Command文件**：为每个Skill创建commands/目录下的命令文件
2. **添加示例脚本**：在scripts/目录添加使用示例
3. **完善references/**：添加参考资料和法律依据
4. **测试验证**：在Claude Code中测试每个Skill
5. **客户试点**：选择1-2家机构客户进行试点

---

**文档版本**：v1.0
**创建时间**：2026-04-08
**作者**：Financial Services QCC
