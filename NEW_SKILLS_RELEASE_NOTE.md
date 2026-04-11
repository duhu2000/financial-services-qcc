# V2.0 版本新增9个Skill发布说明

## 中优先级 - 专业扩展技能（5个）

**信贷风控场景（1个）**：
credit-rating-qcc（企业信用评级）—— 四维度信用评分，自动生成AAA-C评级与授信建议

**投资尽调场景（2个）**：
ip-due-diligence-qcc（知识产权尽调）—— 专利/商标/软著全维度尽调，技术竞争力评估与FTO风险分析
litigation-analysis-qcc（诉讼风险分析）—— 涉诉全景扫描，案件性质与执行风险深度分析

**供应链金融场景（1个）**：
supply-chain-risk-qcc（供应链风险评估）—— 供应商风险、集中度分析、招投标活跃度与韧性评估

**人力合规场景（1个）**：
executive-background-qcc（高管背景调查）—— 法定代表人/董监高/实控人背景核查与利益冲突排查

---

## 低优先级 - 研究辅助技能（4个）

**行业研究场景（1个）**：
industry-analysis-qcc（行业分析辅助）—— 基于招投标与资质数据的行业规模、格局、趋势分析

**战略分析场景（1个）**：
competitive-map-qcc（竞争格局分析）—— 竞争对手识别、多维对标、生态位与竞争策略建议

**并购投资场景（1个）**：
merger-screening-qcc（并购筛查）—— 潜在标的筛查、匹配度分析、估值参考与交易可行性评估

**VC/FA场景（1个）**：
fundraising-tracker-qcc（融资动态追踪）—— 融资历史、估值趋势、投资方画像与竞品对比

---

## 使用示例

```bash
# 企业信用评级（银行信贷）
/credit-rating-qcc 企业名称 --sector 制造业

# 知识产权尽调（科技投资）
/ip-due-diligence-qcc 企业名称 --peer 竞品企业

# 诉讼风险分析（法务尽调）
/litigation-analysis-qcc 企业名称 --period 近3年

# 供应链风险评估（制造业）
/supply-chain-risk-qcc 企业名称 --tier 1

# 高管背景调查（HR/投资）
/executive-background-qcc 企业名称 --person 高管姓名

# 行业分析辅助（研究所）
/industry-analysis-qcc 新能源行业 --region 全国

# 竞争格局分析（战略投资）
/competitive-map-qcc 企业名称 --scope 全景

# 并购筛查（MA）
/merger-screening-qcc 收购方企业 --industry 目标行业

# 融资动态追踪（VC/FA）
/fundraising-tracker-qcc 企业名称 --sector 行业
```

---

## 完整16个Skill架构

| 优先级 | 数量 | 场景覆盖 |
|--------|------|---------|
| 核心技能 | 2个 | KYB核验、IC Memo投资备忘录 |
| 高优先级 | 5个 | 企业画像、尽调清单、合规监控、ESG评估、关联方穿透 |
| 中优先级 | 5个 | 信用评级、知识产权尽调、诉讼分析、供应链风险、高管背调 |
| 低优先级 | 4个 | 行业分析、竞争格局、并购筛查、融资追踪 |

**总计：16个Skill，覆盖银行、券商、PE/VC、制造业、研究所、FA全场景**
