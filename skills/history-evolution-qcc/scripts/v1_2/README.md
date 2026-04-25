# V1.2 schema-driven 生成器框架

> **目标：** 从代码层面杜绝 V1.1.3 的"自信地犯错"事故（USCC 编造、股东漏列、专利数错位、处罚状态编造等）。

---

## 1. 模块结构

```
v1_2/
├── __init__.py
├── uscc_validator.py        # GB 32100-2015 USCC 校验位算法
├── evidence.py              # MCP 调用证据锚点系统
├── data_contract.py         # pydantic schema（count ≡ rows、强类型）
├── data_extractor.py        # MCP 返回 → ReportSchema 转换器
├── consistency_check.py     # 跨章节一致性检查
├── render_md.py             # 从 schema 渲染 Markdown
├── build_report_v1_2.py     # 主入口
├── test_v1_2.py             # 红绿对照测试
└── README.md
```

## 2. 防御机制 ↔ V1.1.3 事故映射

| V1.1.3 事故 | V1.2 防御点 | 文件 |
|---|---|---|
| USCC 编造 `91320506MA1UYUWY3X` | GB 32100 校验位算法直接拦截 | `uscc_validator.py` |
| 当前股东 9 vs MCP 13 | `total_count == len(rows)` validator | `data_contract.py:CurrentShareholdersSection` |
| 历史股东 16 vs MCP 17 | 同上 | `HistoricalShareholdersSection` |
| 历任董监高 9 vs MCP 10 | 同上 | `ExecutiveSection` |
| 对外投资 5 vs MCP 7 | 同上 | `InvestmentSection` |
| 专利年度分布 65 ≠ 总数 94 | 算法 `yearly_distribution()` 自动 group-by | `data_contract.py:PatentSection` |
| 处罚日期 2022 ≠ 2025 | extractor 直引 MCP raw_value | `data_extractor.py:_build_penalties` |
| 处罚状态"已处置/已闭环"编造 | `BANNED_PHRASES` 一致性检查 | `consistency_check.py` |
| 编造"递交主板申报稿" | schema 无对应字段 → 不可写入 | — |
| 字符错误 "竝" vs "竑" | extractor 直引 MCP raw_value | `data_extractor.py` |
| 全字段无溯源 | `ManifestBuilder` 字段级 evidence 链 | `evidence.py` |

## 3. 使用方式

### A. 离线生成（推荐）

```bash
# 第一步：抓取 MCP 数据（在能访问 MCP 的环境）
# 把 12 个工具的返回 JSON 合并存为 mcp_responses.json
# 格式：{"qcc-company.get_company_registration_info": {...}, ...}

# 第二步：本地跑 V1.2 生成器
cd skills/history-evolution-qcc
pip install pydantic    # 必装
python -m scripts.v1_2.build_report_v1_2 \
    --uscc 91320594088140947F \
    --mcp-responses-json /path/to/mcp_responses.json \
    --out ./output
```

输出：
- `output/SKILL-HE-QCC-{ts}.md` — 报告 Markdown
- `output/SKILL-HE-QCC-{ts}.manifest.json` — 字段级 evidence 链

### B. 在 Claude SKILL 编排环境中

```python
from scripts.v1_2.data_extractor import ReportExtractor
from scripts.v1_2.consistency_check import assert_consistency
from scripts.v1_2.render_md import render_markdown

# 1. 实例化（USCC 校验位会立即跑）
extractor = ReportExtractor(uscc="91320594088140947F")

# 2. LLM 编排：依次调用 12 个 MCP 工具，每次喂数据
extractor.feed("qcc-company.get_company_registration_info", mcp_resp_1)
extractor.feed("qcc-company.get_shareholder_info", mcp_resp_2)
# ... 依次喂完

# 3. 构造 schema（schema 校验在这里跑：count ≡ rows、USCC、字段类型）
report = extractor.build_report_schema()

# 4. 跨章节一致性检查
warnings = assert_consistency(report)
for w in warnings:
    print("⚠", w)

# 5. 渲染
md = render_markdown(report)
extractor.manifest.write("output/manifest.json")
```

### C. 测试

```bash
python -m scripts.v1_2.test_v1_2
```

应输出：
```
✓ test_uscc_fabricated
✓ test_count_vs_rows_shareholders
✓ test_count_vs_rows_historical
✓ test_count_vs_rows_executives
✓ test_count_vs_rows_investments
✓ test_penalty_banned_phrases
✓ test_e2e_with_mock_mcp（生成于 /tmp/v1_2_test_output/...）
```

## 4. 与 V1.1.3 的兼容性

V1.2 框架放在 `scripts/v1_2/` 子目录下，**不修改 V1.1.3 的 `build_docx.py` / `build_timeline.py`**。

迁移路径：
1. **过渡阶段（推荐）**：用 V1.2 生成 MD + manifest，再用 V1.1.3 的 `build_docx.py` 把 MD 转 DOCX/PDF。
2. **完全迁移**：把 `build_docx.py` 改为消费 `ReportSchema` 对象（而非散装 dict）。这是 V1.3 的工作。

## 5. 强制约束（不可绕过）

1. **USCC 必须通过 GB 32100 校验位** — 拦截编造主体。
2. **每个 list 字段必须 `total_count == len(rows)`** — 拦截截断/漏列。
3. **专利年度分布必须用 `yearly_distribution()`** — 算法生成而非手写。
4. **处罚字段不得含 BANNED_PHRASES**（已处置/已闭环/当期整改）— 这些状态需 MCP 显式返回。
5. **每个被消费的 MCP 字段必须经 `recorder.evidence_for(json_path)` 取值** — 强制 evidence 锚点。

## 6. 已知边界

- **行政处罚详情**：MCP `get_administrative_penalty` 不返回违法行为类型 / 处置状态。V1.2 不允许在报告里写这两个字段（写了 schema 也不接受）。如果业务上必须呈现，请走"另调用 MCP 公开公告查询工具"路径，并接到独立 schema。
- **里程碑算法**：V1.2 的 `_render_section_2_milestones()` 是基于"成立 + 名称变更 + 国家级首次荣誉"的简单算法。如需更精细的里程碑（如股改、上市辅导）需要扩展规则。
- **§5.5 关联方网络**：V1.2 暂未实现陈德强级别的人员关联方穿透（涉及 `qcc-executive` 8 个工具），可在 V1.3 补齐。

## 7. 下一步（V1.3 规划）

- `build_docx.py` 改为消费 `ReportSchema` 对象，彻底替换 V1.1.3。
- 加入 `qcc-executive.*` 工具集成，支持关联方网络章节。
- 加入字符相似度检查（防止"竝/竑"类错字 — 直引 MCP 已能防御，但可加一道字符预警）。
- 提供 `regenerate_examples.sh` 一键脚本：拉 MCP → 生成 MD → 转 PDF → 部署到 mcp_web 仓库。
