---
name: qcc-full-dd-profile
description: |
  生成投融资标的全维度尽调报告（IC Memo格式），适用于PE/VC投资尽调、并购重组、战略投资。
  通过企查查MCP服务获取工商信息、股权穿透、知识产权、司法风险、经营动态，输出标准化投资委员会备忘录。
arguments:
  - name: company_name
    type: string
    required: true
    description: 目标企业全称
  - name: investment_round
    type: string
    required: false
    description: 投资轮次（如Pre-A、A轮、B轮等，可选）
  - name: sector
    type: string
    required: false
    description: 行业领域（可选）
  - name: format
    type: string
    required: false
    default: all
    description: 输出格式（md/docx/pptx/all，默认为all同时生成三种格式）
---

## Command: /qcc-full-dd-profile

生成投融资全维度尽调报告，输出标准化IC Memo格式。

### 使用示例

```
# 生成全部三种格式（默认）
/qcc-full-dd-profile 华为技术有限公司

# 仅生成Markdown
/qcc-full-dd-profile 华为技术有限公司 --format md

# 仅生成Word（适合投委会审阅）
/qcc-full-dd-profile 北京字节跳动科技有限公司 --format docx

# 仅生成PPT（适合路演汇报）
/qcc-full-dd-profile 宁德时代新能源科技股份有限公司 --format pptx

# 带投资轮次和行业信息
/qcc-full-dd-profile 北京字节跳动科技有限公司 --round Series B --sector 互联网 --format all
```

### 输出格式说明

**三种格式同时生成（默认）：**
| 格式 | 文件扩展名 | 适用场景 |
|------|-----------|---------|
| Markdown | .md | 系统对接、API传输、数据入库 |
| Word | .docx | 投委会审阅、打印盖章、合规留档 |
| PPT | .pptx | 投资路演、管理层快速汇报 |

**文件命名规范：**
```
IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.md
IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.docx
IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.pptx
```

### 报告结构（7章IC Memo）

**Chapter 1: 执行摘要 (Executive Summary)**
- 投资亮点
- 主要关注点
- 关键指标速览

**Chapter 2: 公司概况与股权结构 (Company Overview & Equity)**
- 工商注册信息（企查查MCP企业基座）
- 股权穿透分析（25%规则识别UBO）
- 实际控制人识别
- 历史融资情况

**Chapter 3: 知识产权与核心竞争力 (IP & Core Competence)**
- 专利布局分析（发明/实用新型/外观）
- 商标品牌核查
- 软件著作权统计
- 核心技术评估
- 技术壁垒判断

**Chapter 4: 法律与合规风险 (Legal & Compliance)**
- 涉诉情况（原告/被告/被执行人）
- 18类风险全扫描
- 合规结论
- 风险提示

**Chapter 5: 经营与市场分析 (Operation & Market)**
- 招投标活跃度（业务规模指标）
- 资质证书有效性
- 舆情监控
- 市场地位评估

**Chapter 6: 财务分析 (Financial Analysis)**
- 注：本章节需要目标公司提供财务报表或使用第三方财务数据服务
- 建议要求目标公司提供近3年审计报告

**Chapter 7: 投资建议与风险提示 (Investment Recommendation)**
- 投资建议
- 风险等级评定
- 关键风险提示
- 建议投资条款
- 投后管理建议

### 数据来源

**企查查MCP服务：**
- `qcc-company`: 工商注册信息、股东结构
- `qcc-risk`: 18类司法风险
- `qcc-ipr`: 专利、商标、著作权
- `qcc-operation`: 招投标、资质、舆情

### 输出结果

**报告字段：**
- `company_name`: 企业名称
- `investment_round`: 投资轮次
- `sector`: 行业领域
- `status`: 报告状态
- `generated_at`: 生成时间
- `chapters`: 7章详细内容
- `summary`: 执行摘要

**风险等级评定：**

| 等级 | 含义 | 投资建议 |
|-----|------|---------|
| **高** | 存在关键法律风险 | 建议暂缓投资 |
| **中高** | 存在合规风险 | 建议谨慎投资，需充分尽调 |
| **中** | 无明显重大风险 | 建议推进投资 |

### 技术实现

```python
from utils.dd_report_generator import DDReportGenerator

generator = DDReportGenerator()
report = generator.generate_full_dd_profile(
    company_name=company_name,
    investment_round=investment_round,
    sector=sector
)
```

### 错误处理

- **企业信息获取失败**: 未找到企业主体信息
- **风险扫描失败**: 部分风险数据获取失败
- **配置错误**: MCP配置问题

### 使用建议

1. **配合KYB核验使用**：先执行/qcc-kyb-profile进行快速筛查
2. **关注风险章节**：重点关注Chapter 4的法律合规风险
3. **补充财务数据**：Chapter 6需要外部财务数据补充
4. **定期更新**：建议每季度更新尽调报告

### 相关文档

- [MCP配置指南](../docs/MCP_CONFIGURATION.md)
- [IC Memo模板说明](../docs/IC_MEMO_TEMPLATE.md)
- [尽调清单](../docs/DUE_DILIGENCE_CHECKLIST.md)
