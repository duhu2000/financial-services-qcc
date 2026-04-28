"""
build_report_v1_2.py · V1.2 报告生成主入口
=================================================================
端到端流程：
  USCC 校验 → 调用 MCP → 数据契约校验 → 一致性自检 → 渲染 MD → 生成 manifest

用法：
    python build_report_v1_2.py --uscc 91320594088140947F --out ./output

或在 Claude SKILL 编排环境中：
    from v1_2.data_extractor import ReportExtractor
    extractor = ReportExtractor(uscc=...)
    extractor.feed("qcc-company.get_company_registration_info", mcp_response_dict)
    # ... 喂完所有需要的工具
    report = extractor.build_report_schema()  # 通过 schema 校验
    md = render_markdown(report)
    extractor.manifest.write("manifest.json")

关键约束：
- 任一 schema 校验失败 → 直接 abort，不生成 PDF/MD
- 任一 consistency check 抛 ConsistencyError → 直接 abort
- 任一字段缺 evidence → manifest 不完整，告警

历史教训映射（V1.1.3 事故 → V1.2 防护）：
| V1.1.3 事故                     | V1.2 防护机制                         |
|---------------------------------|---------------------------------------|
| USCC 编造（91320506MA1UYUWY3X） | uscc_validator 校验位算法直接拦截     |
| 股东 9 vs MCP 13                | CurrentShareholdersSection.count_match|
| 历史股东 16 vs MCP 17           | HistoricalShareholdersSection 同上    |
| 董监高 9 vs MCP 10              | ExecutiveSection 同上                 |
| 对外投资 5 vs MCP 7             | InvestmentSection 同上                |
| 专利年度分布 65 ≠ 总数 94       | yearly_distribution() 算法生成        |
| 处罚日期 2022 ≠ 2025            | data_extractor 直引 MCP 字段          |
| 处罚状态"已处置" 编造           | consistency_check 禁止 BANNED_PHRASES |
| 编造"递交主板申报稿"            | schema 无对应字段 → 不可写入          |
| 字符错误"竝"vs"竑"             | data_extractor 直引 MCP raw_value     |
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .uscc_validator import validate_uscc, USCCValidationError
from .evidence import ManifestBuilder
from .data_extractor import ReportExtractor
from .consistency_check import assert_consistency, ConsistencyError
from .render_md import render_markdown
from .render_pdf import render_pdf


def generate_report(
    uscc: str,
    *,
    mcp_responses: dict[str, dict] | None = None,
    mcp_call=None,
    out_dir: str = "./output",
    report_id: str | None = None,
) -> dict:
    """生成 V1.2 报告。

    Args:
        uscc: 统一社会信用代码（必须通过校验位校验）
        mcp_responses: 预先调好的 MCP 返回数据（推荐：避免运行时调外部）
                       格式 {tool_name: response_dict, ...}
        mcp_call: 或者传一个 callable (tool_name, search_key) -> dict
        out_dir: 输出目录
        report_id: 自定义报告号；不传自动生成

    Returns:
        {"md_path": ..., "manifest_path": ..., "warnings": [...]}
    """
    # Step 1 · USCC 必须先过校验位
    ok, msg = validate_uscc(uscc)
    if not ok:
        raise USCCValidationError(f"USCC 不合法：{msg} · 值：{uscc}")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Step 2 · 调 MCP / 喂数据
    extractor = ReportExtractor(uscc=uscc, report_id=report_id)
    if mcp_responses is not None:
        for tool, resp in mcp_responses.items():
            extractor.feed(tool, resp)
    elif mcp_call is not None:
        extractor.fetch_all(mcp_call)
    else:
        raise ValueError("必须提供 mcp_responses 或 mcp_call 之一")

    # Step 3 · 构造 schema 对象（pydantic 会校验 count ≡ rows、USCC 等）
    report = extractor.build_report_schema()

    # Step 4 · 跨章节一致性自检（编造、状态词、时间合理性）
    warnings = assert_consistency(report)

    # Step 5 · 渲染 MD
    md = render_markdown(report)
    md_path = out_path / f"{extractor.report_id}.md"
    md_path.write_text(md, encoding="utf-8")

    # Step 6 · 渲染 PDF（保留 V1.1.3 圆点时间轴样式）
    pdf_path = out_path / f"{extractor.report_id}.pdf"
    render_pdf(report, pdf_path)

    # Step 7 · 输出 manifest.json（字段级 evidence 链）
    manifest_path = out_path / f"{extractor.report_id}.manifest.json"
    extractor.manifest.write(str(manifest_path))

    return {
        "md_path": str(md_path),
        "pdf_path": str(pdf_path),
        "manifest_path": str(manifest_path),
        "warnings": warnings,
        "report_id": extractor.report_id,
        "company_name": report.company.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="V1.2 schema-driven 报告生成器")
    parser.add_argument("--uscc", required=True, help="统一社会信用代码")
    parser.add_argument(
        "--mcp-responses-json",
        help="预先抓好的 MCP 返回 JSON 文件路径（推荐用于离线生成）",
    )
    parser.add_argument("--out", default="./output", help="输出目录")
    parser.add_argument("--report-id", help="自定义报告号")
    args = parser.parse_args()

    if not args.mcp_responses_json:
        print(
            "错误：本入口暂不支持运行时实时调用 MCP（需要 MCP client 上下文）。\n"
            "请用 --mcp-responses-json 预存的 JSON 文件，或在 Claude SKILL 环境中"
            "通过编排 prompt 完成 MCP 调用 + extractor.feed()。",
            file=sys.stderr,
        )
        return 2

    with open(args.mcp_responses_json, encoding="utf-8") as f:
        mcp_responses = json.load(f)

    result = generate_report(
        uscc=args.uscc,
        mcp_responses=mcp_responses,
        out_dir=args.out,
        report_id=args.report_id,
    )

    print(f"✓ MD 生成成功：{result['md_path']}")
    print(f"✓ PDF 生成成功：{result['pdf_path']}")
    print(f"✓ 溯源 manifest：{result['manifest_path']}")
    print(f"  报告号：{result['report_id']}")
    print(f"  企业：{result['company_name']}")
    if result["warnings"]:
        print(f"\n⚠ {len(result['warnings'])} 条警告：")
        for w in result["warnings"]:
            print(f"   - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
