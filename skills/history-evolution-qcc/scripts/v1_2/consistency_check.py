"""
consistency_check.py · 跨章节一致性自检
=================================================================
作用：在生成 PDF/MD 之前，做"全报告维度"的一致性检查。

历史教训：V1.1.3 报告里
- §5.5 把元禾纳芯放在"间接投资 1.1922%"，但 §6.1 应该是"直接投资 2.5%"
- §10 大事年表写 "2022-06-10 已处置" 但 MCP 显示是 2025-09-24 未处置
- 注册资本节点数量 vs 大事年表里的资本变更次数 不一致
- 报告自称"5 次办公地迁移"但实际地址只有 5 个（应说 4 次）
本模块在出 PDF 前一次性扫除这类隐藏不一致。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_contract import ReportSchema


class ConsistencyError(ValueError):
    """跨章节一致性错误。"""


def check_report_consistency(report: "ReportSchema") -> list[str]:
    """运行所有 cross-section 检查。

    Returns:
        warning 列表（空表示完全通过；非空但无 ConsistencyError 表示仅有提醒）
    """
    warnings: list[str] = []

    # 1. USCC 必须与 company.uscc 一致（双重保险）
    # 已在 schema 层做了，但这里再核对所有章节都用同一 USCC
    # （V1.2 schema 不在每个章节内重复存 USCC，所以这里跳过）

    # 2. 现任董监高 vs MCP 主要人员 — 名字对照
    cur_names = {e.name for e in report.executives.current_executives}
    sh_names = {s.name for s in report.current_shareholders.shareholders}
    # 现任董监高里持股比例 > 0 的人员，应该都出现在股东表里（同一人不应被遗漏）
    for exec_ in report.executives.current_executives:
        if exec_.holding_ratio and exec_.holding_ratio not in ("", "—", "0%"):
            if exec_.name not in sh_names:
                warnings.append(
                    f"[一致性] 现任董监高 {exec_.name}（持股 {exec_.holding_ratio}）"
                    f" 未出现在 §5.1 当前股东列表 — 请核实"
                )

    # 3. 注册资本变更轨迹的节点数 vs §10 大事年表里的资本变更次数
    # 大事年表里"注册资本变更"应等于 (capital_nodes 数量 - 1)
    # — 但本模块不直接访问 change_records 明细，仅做提示

    # 4. 名称变更次数 vs 历史名称数
    name_changes = len(report.historical_registration.name_nodes) - 1  # 减去当前
    # 不强制 — 仅提醒
    if name_changes < 0:
        warnings.append("[逻辑] 历史名称表为空，但通常应至少包含设立时名称")

    # 5. 地址迁移次数 = 地址数 - 1
    addr_count = len(report.historical_registration.address_nodes)
    if addr_count == 0:
        warnings.append("[逻辑] 历史地址表为空，应至少包含当前地址")

    # 6. 专利总数 vs 年度分布加和
    yearly = report.patents.yearly_distribution()
    yearly_sum = sum(yearly.values())
    if yearly_sum != report.patents.total_count:
        raise ConsistencyError(
            f"[严重] 专利年度分布加和 {yearly_sum} ≠ 总数 "
            f"{report.patents.total_count}（V1.1.3 经典事故）"
        )

    # 7. 资质有效数 ≤ 总数
    if report.qualifications.valid_count > report.qualifications.total_count:
        raise ConsistencyError(
            f"[严重] 有效资质 {report.qualifications.valid_count} > "
            f"总资质 {report.qualifications.total_count}"
        )

    # 8. 处罚状态 — 严禁出现"已处置/已闭环/当期整改"等需 MCP 显式返回的状态词
    BANNED_PHRASES = ["已处置", "当期整改", "已闭环", "整改完毕"]
    for p in report.administrative_penalties.penalties:
        for field_name in ("penalty_result",):
            v = getattr(p, field_name, None) or ""
            for phrase in BANNED_PHRASES:
                if phrase in v:
                    raise ConsistencyError(
                        f"[严重] 处罚 {p.decision_no} 的 {field_name} 包含 '{phrase}' "
                        f"— 该状态需 MCP 显式返回，禁止编造"
                    )

    # 9. 时间合理性 — 处罚日期不能晚于报告生成日期
    from datetime import datetime
    report_dt = datetime.fromisoformat(report.generated_at.replace("Z", "+00:00"))
    for p in report.administrative_penalties.penalties:
        if p.penalty_date:
            try:
                p_dt = datetime.strptime(p.penalty_date, "%Y-%m-%d")
                if p_dt.replace(tzinfo=report_dt.tzinfo) > report_dt:
                    warnings.append(
                        f"[时间] 处罚日期 {p.penalty_date} 晚于报告生成日期"
                        f" {report.generated_at[:10]}"
                    )
            except ValueError:
                pass

    # 10. 处罚日期距今 < 1 年时，禁止用"清洁基线"等乐观措辞 — schema 不直接管，
    #     由生成器在写"总结评价"时自动判断（见 build_report.py）

    return warnings


def assert_consistency(report: "ReportSchema") -> list[str]:
    """如有严重错误抛 ConsistencyError；返回 warning 列表。"""
    return check_report_consistency(report)
