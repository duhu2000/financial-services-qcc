---
name: qcc-kyb-profile
description: |
  执行企业KYB（Know Your Business）自动化核验，适用于金融机构企业客户开户、授信、尽调场景。
  通过企查查MCP服务获取企业工商信息、股东结构、18类风险信号，输出A/B/C/D四级评级结果。
arguments:
  - name: company_name
    type: string
    required: true
    description: 待核验的企业全称
  - name: credit_code
    type: string
    required: false
    description: 统一社会信用代码（可选，用于交叉验证）
  - name: format
    type: string
    required: false
    default: all
    description: 输出格式（md/docx/pptx/all，默认为all同时生成三种格式）
---

## Command: /qcc-kyb-profile

执行企业KYB自动化核验，生成标准化核验报告。

### 使用示例

```
# 生成全部三种格式（默认）
/qcc-kyb-profile 华为技术有限公司

# 仅生成Markdown
/qcc-kyb-profile 华为技术有限公司 --format md

# 仅生成Word（适合风控审批）
/qcc-kyb-profile 华为技术有限公司 --format docx

# 仅生成PPT（适合快速汇报）
/qcc-kyb-profile 华为技术有限公司 --format pptx

# 带统一社会信用代码交叉验证
/qcc-kyb-profile 北京字节跳动科技有限公司 91110108MA00xxxxxx
```

### 输出格式说明

**三种格式同时生成（默认）：**
| 格式 | 文件扩展名 | 适用场景 |
|------|-----------|---------|
| Markdown | .md | 系统对接、API传输、数据入库 |
| Word | .docx | 风控审批、打印盖章、合规留档 |
| PPT | .pptx | 管理层汇报、快速风险展示 |

**文件命名规范：**
```
KYB核验报告-[企业名称]-YYYYMMDD.md
KYB核验报告-[企业名称]-YYYYMMDD.docx
KYB核验报告-[企业名称]-YYYYMMDD.pptx
```

### 执行流程

**Phase 1: 实体锚定 (Entity Verification)**
- 验证企业名称与统一社会信用代码匹配性
- 获取工商注册信息（法定代表人、注册资本、经营状态等）
- 确认企业存续状态

**Phase 2: 股权穿透与UBO识别 (Shareholder Analysis)**
- 获取股东结构信息
- 识别持股≥25%的自然人股东（受益所有人）
- 分析股权集中度

**Phase 3: 18类风险全面扫描 (Risk Scanning)**

CRITICAL级风险（立即预警）：
- 失信被执行人
- 被执行人
- 限制高消费
- 破产重整
- 股权冻结
- 司法协助

HIGH级风险（需尽调）：
- 经营异常
- 严重违法
- 行政处罚
- 环保处罚

MEDIUM级风险（关注）：
- 股权出质
- 动产抵押
- 欠税公告
- 税务非正常
- 税收违法

LOW级风险（备案）：
- 涉诉信息
- 裁判文书

**Phase 4: 经营健康度评估 (Operation Health)**
- 招投标活跃度
- 资质证书有效性
- 舆情监控

### 输出结果

**KYB评级标准：**

| 评级 | 含义 | 处理建议 |
|-----|------|---------|
| **A** | 正常准入 | 主体合法存续，无明显风险信号，可按标准流程处理 |
| **B** | 审慎准入+加强监测 | 存在中等风险或经营异常，建议增加监测频率 |
| **C** | 需人工复核 | 存在高风险项，建议加强尽调，提交风险管理部门审批 |
| **D** | 禁止准入 | 存在关键风险项，建议立即启动风险预警流程，终止业务办理 |

**输出字段：**
- `company_name`: 企业名称
- `kyb_rating`: A/B/C/D评级
- `status`: 核验状态
- `phase_results`: 各阶段详细结果
- `risk_summary`: 风险摘要统计
- `ubo`: 受益所有人列表
- `verification_suggestion`: 核验建议

### 技术实现

```python
from utils.kyb_verifier import KYBVerifier

verifier = KYBVerifier()
results = verifier.verify_company(company_name, credit_code)
```

### 错误处理

- **实体锚定失败**: 未找到企业主体信息，请核实企业名称
- **服务调用失败**: 企查查MCP服务暂时不可用，请稍后重试
- **配置错误**: 未找到MCP配置，请检查~/.claude/.mcp.json

### 相关文档

- [MCP配置指南](../docs/MCP_CONFIGURATION.md)
- [KYB核验规则说明](../docs/KYB_VERIFICATION_RULES.md)
