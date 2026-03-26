# 报告导出功能指南

本指南介绍 KYB 核验报告和 IC Memo 投资尽调报告的三格式导出功能。

## 支持的格式

| 格式 | 扩展名 | 适用场景 | 特点 |
|------|--------|---------|------|
| **Markdown** | .md | 系统对接、API传输 | 纯文本，便于数据提取和结构化存储 |
| **Word** | .docx | 风控审批、合规留档 | 专业排版，支持打印盖章，适合签字审批 |
| **PPT** | .pptx | 管理层汇报、路演 | 一页摘要，quadrant布局，30秒速览 |

## 快速开始

### 1. 安装依赖

```bash
pip install python-docx python-pptx
```

### 2. KYB 报告导出

```python
from utils.kyb_verifier import KYBVerifier

verifier = KYBVerifier(output_dir="./reports")

# 生成所有格式（默认）
results = verifier.verify_company(
    company_name="华为技术有限公司",
    credit_code="9144030019237XXXXX",
    export_format="all"  # md + docx + pptx
)

# 仅生成 Word
results = verifier.verify_company(
    company_name="华为技术有限公司",
    export_format="docx"
)

# 仅生成 PPT
results = verifier.verify_company(
    company_name="华为技术有限公司",
    export_format="pptx"
)

# 获取生成的文件路径
exported_files = results.get("exported_files", {})
print(f"Markdown: {exported_files.get('md')}")
print(f"Word: {exported_files.get('docx')}")
print(f"PPT: {exported_files.get('pptx')}")
```

### 3. IC Memo 报告导出

```python
from utils.dd_report_generator import DDReportGenerator

generator = DDReportGenerator(output_dir="./reports")

# 生成所有格式（默认）
report = generator.generate_full_dd_profile(
    company_name="北京至格科技有限公司",
    investment_round="C轮",
    sector="制造业",
    export_format="all"  # md + docx + pptx
)

# 仅生成 Word
report = generator.generate_full_dd_profile(
    company_name="北京至格科技有限公司",
    export_format="docx"
)

# 仅生成 PPT（适合路演）
report = generator.generate_full_dd_profile(
    company_name="北京至格科技有限公司",
    export_format="pptx"
)
```

## 命令行使用

### Commands 方式（推荐）

```bash
# KYB 核验 - 生成所有格式
/qcc-kyb-profile 华为技术有限公司

# KYB 核验 - 仅生成 Word
/qcc-kyb-profile 华为技术有限公司 --format docx

# IC Memo - 生成所有格式
/qcc-full-dd-profile 北京至格科技有限公司 --round C轮 --sector 制造业

# IC Memo - 仅生成 PPT
/qcc-full-dd-profile 北京至格科技有限公司 --format pptx
```

### Skills 方式

```bash
# KYB 核验
/kyb-verification-qcc 华为技术有限公司 --format all

# IC Memo
/ic-memo-qcc 北京至格科技有限公司 --sector 制造业 --format docx
```

## 文件命名规范

生成的文件自动采用以下命名格式：

```
KYB核验报告-[企业名称]-YYYYMMDD.md
KYB核验报告-[企业名称]-YYYYMMDD.docx
KYB核验报告-[企业名称]-YYYYMMDD.pptx

IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.md
IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.docx
IC-Memo-投资尽调报告-[企业名称]-YYYYMMDD.pptx
```

## 格式详细说明

### Markdown 格式

- 纯文本格式，便于版本控制和系统对接
- 包含完整的数据结构，便于二次处理
- 适合数据库存储和 API 传输

### Word 格式

- 专业排版，使用微软雅黑字体
- 包含表格、标题层级、项目符号
- 关键信息（评级、风险）使用颜色标识
- IC Memo 包含投委会签字页
- 适合打印、盖章、审批流程

### PPT 格式

- 一页摘要，采用 quadrant 四象限布局
- 左上：企业概况
- 右上：核心亮点/KYB评级
- 左下：风险扫描
- 右下：投资建议/经营健康度
- 适合向管理层快速汇报

## 自定义导出

如果需要自定义导出逻辑，可以直接使用 `ReportExporter` 类：

```python
from utils.report_exporter import ReportExporter

exporter = ReportExporter(output_dir="./custom_reports")

# 导出 KYB 报告
exported_files = exporter.export_kyb_report(
    report_data=kyb_results,
    company_name="华为技术有限公司",
    format_type="all"  # md/docx/pptx/all
)

# 导出 IC Memo
exported_files = exporter.export_ic_memo(
    report_data=ic_memo_data,
    company_name="北京至格科技有限公司",
    format_type="all"
)
```

## 常见问题

### Q: PPT 导出失败怎么办？

A: 请确认已安装 python-pptx：
```bash
pip install python-pptx
```

### Q: 如何修改输出目录？

A: 在初始化时指定 `output_dir` 参数：
```python
verifier = KYBVerifier(output_dir="/path/to/output")
```

### Q: 如何自定义 Word 模板？

A: 可以修改 `utils/report_exporter.py` 中的 `_export_kyb_word` 和 `_export_ic_memo_word` 方法，添加自定义样式。

### Q: 是否支持 PDF 导出？

A: 当前版本支持 Markdown/Word/PPT 三种格式。如需 PDF，可以：
1. 先生成 Word，然后使用 Word 的"另存为 PDF"功能
2. 或使用第三方库如 `docx2pdf` 进行转换

## 相关文档

- [MCP 配置指南](./MCP_CONFIGURATION.md)
- [KYB 核验规则](./KYB_VERIFICATION_RULES.md)
- [IC Memo 模板说明](./IC_MEMO_TEMPLATE.md)
