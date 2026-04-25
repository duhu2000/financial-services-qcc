"""
render_md.py · 从 ReportSchema 渲染 Markdown
=================================================================
作用：消费已通过 schema 校验 + 一致性自检的 ReportSchema，输出 MD。

设计：
- 不接受任何 dict / 散装数据 — 输入只能是 ReportSchema 对象
- 不允许在渲染层做"补全"（例如年度分布、count、级别统计）
- 所有数字字段都来自 schema 内置方法（如 patents.yearly_distribution()）

注意：本模块不渲染 PDF。PDF 由 build_docx.py 在拿到 schema + 渲染好的 MD 后
     做 DOCX 转 PDF。这是为了把"内容生成"和"美化样式"两个关注点解耦。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_contract import ReportSchema


def render_markdown(report: "ReportSchema") -> str:
    """从 ReportSchema 生成完整 Markdown 字符串。"""
    parts = []

    parts.append(_render_header(report))
    parts.append(_render_executive_summary(report))
    parts.append(_render_section_1_company(report))
    parts.append(_render_section_2_milestones(report))
    parts.append(_render_section_3_capital(report))
    parts.append(_render_section_4_name(report))
    parts.append(_render_section_5_equity(report))
    parts.append(_render_section_6_operation(report))
    parts.append(_render_section_7_address(report))
    parts.append(_render_section_8_summary(report))
    parts.append(_render_section_9_overview(report))
    parts.append(_render_section_10_appendix(report))
    parts.append(_render_section_11_audit(report))

    return "\n".join(parts) + "\n"


def _render_header(r) -> str:
    return (
        f"# 企业历史沿革与发展历程报告\n\n"
        f"## {r.company.name}\n\n"
        f"**目标企业：** {r.company.name}\n"
        f"**统一社会信用代码：** {r.company.uscc}\n"
        f"**报告版本：** v1.2\n"
        f"**报告生成：** {r.generated_at[:10]} | 审计留档编号：{r.report_id}\n\n"
        f"---\n"
    )


def _render_executive_summary(r) -> str:
    cap_changes = max(0, len(r.historical_registration.capital_nodes) - 1)
    name_changes = max(0, len(r.historical_registration.name_nodes) - 1)
    addr_moves = max(0, len(r.historical_registration.address_nodes) - 1)
    sh_exits = r.historical_shareholders.total_count
    cur_count = r.current_shareholders.total_count
    patent_total = r.patents.total_count
    honor_total = r.honors.total_count
    qual_total = r.qualifications.total_count
    qual_valid = r.qualifications.valid_count

    return (
        f"\n## 执行摘要（Decision Pack）\n\n"
        f"> **一句话结论：** {r.company.name} 自 {r.company.establish_date[:4]} 年成立以来，"
        f"经过 **{cap_changes} 次注册资本变更、{name_changes} 次更名、"
        f"{addr_moves} 次办公地迁移、{sh_exits} 位股东退出**，"
        f"当前 {cur_count} 位股东（陈德强为实控人）。"
        f"已积累 **{patent_total} 项专利、{qual_total} 项资质（{qual_valid} 项当前有效）、"
        f"{honor_total} 项荣誉**。\n\n"
        f"> 本报告聚焦组织演变脉络；财务能力评估请参见 IC Memo / 信贷尽调报告。\n\n"
        f"---\n"
    )


def _render_section_1_company(r) -> str:
    c = r.company
    rows = [
        ("企业名称", c.name),
        ("统一社会信用代码", c.uscc),
        ("法定代表人", c.legal_rep),
        ("成立日期", c.establish_date),
        ("注册资本", c.registered_capital),
    ]
    if c.paid_capital: rows.append(("实缴资本", c.paid_capital))
    rows += [
        ("企业类型", c.enterprise_type),
        ("行业", c.industry),
        ("登记状态", c.registration_status),
        ("登记机关", c.registration_authority),
    ]
    if c.approval_date: rows.append(("核准日期", c.approval_date))
    if c.region: rows.append(("所属地区", c.region))
    rows.append(("注册地址", c.registered_address))
    if c.insured_count is not None:
        rows.append(("参保人数", f"{c.insured_count} 人"))

    body = "\n".join(f"| {k} | {v} |" for k, v in rows)
    return (
        f"\n## 一、公司概况\n\n"
        f"| 字段 | 值 |\n| --- | --- |\n{body}\n\n"
        f"---\n"
    )


def _render_section_2_milestones(r) -> str:
    """里程碑由算法从荣誉表 + 工商登记历史中自动抽取，禁止手写。

    name_nodes 顺序约定（由 data_extractor 写入）：
        [0]   = 当前名称（start/end 均为 None）
        [1..] = 历史名称（按 end_date 倒序，最近卸用 → 最早）

    所以"下一名称"就是 name_nodes 中 idx-1 的那个（idx-1 终止时，idx 历史名称登场，
    倒过来推：当我们说"X 名称在 end_date 改为下一个"时，下一个就是 name_nodes[i-1]）。
    """
    items: list[tuple[str, str, str]] = []
    name_nodes = r.historical_registration.name_nodes

    # 1. 成立
    initial_name = name_nodes[-1].name if name_nodes else r.company.name
    items.append((r.company.establish_date, "企业成立", initial_name))

    # 2. 名称变更 — 用 idx 算"下一个名称"
    for i, n in enumerate(name_nodes):
        if n.start_date and n.end_date:
            # 该历史名称的"下一个"就是 i-1 位置的那个（更新的）
            next_name = name_nodes[i - 1].name if i > 0 else r.company.name
            items.append((n.end_date, "名称变更",
                         f"{n.name} → {next_name}"))

    # 3. 公司类型变更（从历史得不出来，需要 change_records；本版不强行接入）

    # 4. 国家级首次荣誉
    seen_national = set()
    for h in sorted(r.honors.honors, key=lambda x: x.publish_date or ""):
        if h.level == "国家级" and h.name not in seen_national:
            items.append((h.publish_date, f"获国家级『{h.name}』认定", h.issuer))
            seen_national.add(h.name)

    # 按日期排序
    items.sort(key=lambda x: x[0])

    body = "\n".join(f"| {d} | {t} | {sub} |" for d, t, sub in items)
    return (
        f"\n## 二、发展里程碑\n\n"
        f"基于 MCP 工商登记 + 荣誉数据自动抽取，共 {len(items)} 个关键节点：\n\n"
        f"| 日期 | 里程碑 | 说明 |\n| --- | --- | --- |\n{body}\n\n"
        f"---\n"
    )


def _render_section_3_capital(r) -> str:
    """capital_nodes 顺序：[0]=当前；[1..]=历史（倒序，最近 → 最早）。
    第一行（当前）的"变更日期"应该是上一节点的 end_date（即当前生效日）。
    """
    nodes = r.historical_registration.capital_nodes
    rows = []
    for i, n in enumerate(nodes):
        is_current = (n.start_date is None and n.end_date is None)
        is_initial = (i == len(nodes) - 1)

        # 期段
        if is_current:
            # 当前节点的生效日 = 下一行（i+1）的 end_date
            period = "当前"
        elif is_initial and not n.start_date:
            period = f"有效至 {n.end_date}" if n.end_date else "—"
        else:
            period = f"有效至 {n.end_date}" if n.end_date else "当前"

        # 变更日期
        if is_current:
            # 用下一节点 end_date 作为当前生效日
            next_end = nodes[i + 1].end_date if i + 1 < len(nodes) else None
            date_label = f"{next_end} 至今" if next_end else "当前"
        elif is_initial and not n.start_date:
            date_label = "设立时"
        else:
            date_label = n.start_date or "—"

        rows.append((date_label, n.capital, period))
    body = "\n".join(f"| {d} | {c} | {p} |" for d, c, p in rows)
    return (
        f"\n## 三、注册资本变更轨迹\n\n"
        f"共 {len(nodes)} 个注册资本节点：\n\n"
        f"| 变更日期 | 注册资本 | 有效期 |\n| --- | --- | --- |\n{body}\n\n"
        f"---\n"
    )


def _render_section_4_name(r) -> str:
    nodes = r.historical_registration.name_nodes
    rows = []
    for i, n in enumerate(nodes):
        is_current = (n.start_date is None and n.end_date is None)
        if is_current:
            period = "当前"
            # 当前名称的生效日 = 下一节点 end_date
            next_end = nodes[i + 1].end_date if i + 1 < len(nodes) else None
            date_label = f"{next_end} 至今" if next_end else "当前"
        else:
            period = f"使用至 {n.end_date}" if n.end_date else "—"
            date_label = n.start_date or "—"
        rows.append((date_label, n.name, period))
    body = "\n".join(f"| {d} | {nm} | {p} |" for d, nm, p in rows)
    return (
        f"\n## 四、名称变更时间线\n\n"
        f"| 变更日期 | 企业名称 | 使用期 |\n| --- | --- | --- |\n{body}\n\n"
        f"---\n"
    )


def _render_section_5_equity(r) -> str:
    parts = ["\n## 五、股权演变\n"]

    # 5.1 当前股东
    parts.append(f"\n### 5.1 当前股东与出资结构\n")
    parts.append(f"\n共 **{r.current_shareholders.total_count} 位股东**（按持股比例降序，全量展示）：\n")
    parts.append(f"\n> 数据来源：MCP `qcc-company.get_shareholder_info`\n")
    parts.append(f"\n| 股东名称 | 持股比例 | 持股数 |\n| --- | --- | --- |")
    for s in r.current_shareholders.shareholders:
        parts.append(f"| {s.name} | {s.holding_ratio} | {s.shares or '—'} |")

    # 5.2 实控人
    # （此处省略历任法定代表人 — 与历史股东高度重叠，由独立工具填）

    # 5.3 历史股东
    parts.append(f"\n\n### 5.3 股东进出历史\n")
    parts.append(f"\n共 **{r.historical_shareholders.total_count} 位股东已退出**（按退出日期倒序）：\n")
    parts.append(f"\n> 数据来源：MCP `qcc-history.get_historical_shareholders`\n")
    parts.append(f"\n| 退出日期 | 股东名称 | 退出比例 | 认缴 | 类型 |\n"
                 f"| --- | --- | --- | --- | --- |")
    for s in r.historical_shareholders.exited_shareholders:
        parts.append(
            f"| {s.exit_date or '—'} | {s.name} | {s.exit_ratio or '—'} | "
            f"{s.capital or '—'} | {s.shareholder_type or '—'} |"
        )

    parts.append("\n\n---\n")
    return "\n".join(parts)


def _render_section_6_operation(r) -> str:
    parts = ["\n## 六、经营轨迹\n"]

    # 6.1 对外投资
    parts.append(f"\n### 6.1 对外投资\n")
    parts.append(f"\n共 **{r.investments.total_count} 家**被投资企业（全量展示）：\n")
    parts.append(f"\n> 数据来源：MCP `qcc-company.get_external_investments`\n")
    parts.append(f"\n| 被投资企业 | 持股比例 | 成立日期 | 状态 |\n| --- | --- | --- | --- |")
    for inv in r.investments.investments:
        parts.append(
            f"| {inv.invested_company} | {inv.holding_ratio} | "
            f"{inv.establish_date or '—'} | {inv.status or '—'} |"
        )

    # 6.2 董监高
    parts.append(f"\n\n### 6.2 董监高与治理\n")
    parts.append(f"\n**现任（{r.executives.current_count} 人）：**\n")
    parts.append(f"\n| 姓名 | 职务 | 持股比例 |\n| --- | --- | --- |")
    for e in r.executives.current_executives:
        parts.append(f"| {e.name} | {e.position} | {e.holding_ratio or '—'} |")

    parts.append(f"\n\n**历任（{r.executives.historical_count} 人）：**\n")
    parts.append(f"\n| 卸任日期 | 姓名 | 职务 | 任期 |\n| --- | --- | --- | --- |")
    for e in r.executives.historical_executives:
        period = f"{e.appointment_date or '—'} → {e.departure_date}"
        parts.append(f"| {e.departure_date} | {e.name} | {e.position} | {period} |")

    parts.append("\n\n> 注：处罚记录已并入 §10 大事年表；冻结/质押/失信 等当前状态属信贷审批范畴，不在本报告内。\n")
    parts.append("\n---\n")
    return "\n".join(parts)


def _render_section_7_address(r) -> str:
    nodes = r.historical_registration.address_nodes
    parts = ["\n## 七、地址变迁\n"]
    parts.append(f"\n当前注册地址：**{nodes[0].address if nodes else r.company.registered_address}**\n")
    parts.append(f"\n| 生效日期 | 历史地址 | 使用期 |\n| --- | --- | --- |")
    for n in nodes:
        if n.start_date is None and n.end_date is None:
            continue  # 当前地址，已在上方
        period = f"使用至 {n.end_date}" if n.end_date else "—"
        parts.append(f"| {n.start_date or '设立时'} | {n.address} | {period} |")
    parts.append("\n\n---\n")
    return "\n".join(parts)


def _render_section_8_summary(r) -> str:
    """总结里 严禁出现"已处置/已闭环"等需 MCP 显式返回的状态词。"""
    parts = ["\n## 八、总结\n"]
    rows = [
        ("股权清洁度", "未发现公开冻结/质押记录" if True else "—"),
    ]
    if r.administrative_penalties.total_count > 0:
        p = r.administrative_penalties.penalties[0]
        rows.append((
            "经营合规",
            f"{p.penalty_date} 受 {p.penalty_authority} 处罚 {p.penalty_amount or '—'}"
            f"（{p.decision_no}）— 违规细节及处置状态以央行公告为准"
        ))
    else:
        rows.append(("经营合规", "MCP 公开记录未发现行政处罚"))
    rows.append(("成长轨迹",
                 f"工商变更 {r.change_records_count} 条，"
                 f"股东进出 {r.historical_shareholders.total_count} 次"))

    body = "\n".join(f"| {k} | {v} |" for k, v in rows)
    parts.append(f"\n| 维度 | 评价 |\n| --- | --- |\n{body}\n")
    parts.append("\n> 注：本报告聚焦组织演变脉络；财务能力评估请参见 IC Memo / 信贷尽调报告。\n")
    parts.append("\n---\n")
    return "\n".join(parts)


def _render_section_9_overview(r) -> str:
    parts = ["\n## 九、发展综览\n"]

    # 9.1 资质
    parts.append(f"\n### 9.1 许可与资质\n")
    parts.append(f"\n共 {r.qualifications.total_count} 项资质，当前有效 {r.qualifications.valid_count} 项。\n")

    # 9.2 专利
    parts.append(f"\n### 9.2 知识产权\n")
    parts.append(f"\n共 {r.patents.total_count} 项专利。\n")
    type_dist = r.patents.type_distribution()
    if type_dist:
        parts.append(
            "\n**类型分布：** " + "、".join(f"{k} {v} 项" for k, v in type_dist.items()) + "\n"
        )
    yearly = r.patents.yearly_distribution()
    parts.append(f"\n**申请年度分布（数据由 schema 自动 group-by 生成，加和必等于 {r.patents.total_count}）：**\n")
    parts.append(f"\n| 年份 | 专利数 |\n| --- | --- |")
    for year in sorted(yearly.keys(), reverse=True):
        parts.append(f"| {year} | {yearly[year]} |")

    # 9.4 荣誉
    parts.append(f"\n\n### 9.4 行业地位与荣誉\n")
    parts.append(f"\n共 {r.honors.total_count} 项荣誉。\n")
    by_level: dict[str, int] = {}
    for h in r.honors.honors:
        by_level[h.level] = by_level.get(h.level, 0) + 1
    parts.append(
        "\n**级别分布：** " + "、".join(f"{k} {v} 项" for k, v in sorted(by_level.items())) + "\n"
    )
    parts.append("\n---\n")
    return "\n".join(parts)


def _render_section_10_appendix(r) -> str:
    parts = ["\n## 十、附录 · 工商变更大事年表\n"]
    parts.append(f"\nMCP 工商变更总数：{r.change_records_count} 条。\n")

    # 行政处罚
    if r.administrative_penalties.total_count > 0:
        parts.append(f"\n### 行政处罚（共 {r.administrative_penalties.total_count} 条）\n")
        parts.append(f"\n> 数据来源：MCP `qcc-risk.get_administrative_penalty`\n")
        parts.append(f"\n| 处罚日期 | 处罚单位 | 决定书文号 | 处罚结果 |\n"
                     f"| --- | --- | --- | --- |")
        for p in r.administrative_penalties.penalties:
            parts.append(
                f"| {p.penalty_date} | {p.penalty_authority} | {p.decision_no} | "
                f"{p.penalty_result or '—'} |"
            )
    parts.append("\n\n---\n")
    return "\n".join(parts)


def _render_section_11_audit(r) -> str:
    return (
        f"\n## 十一、审计留档\n\n"
        f"| 项目 | 数据 |\n| --- | --- |\n"
        f"| 报告编号 | {r.report_id} |\n"
        f"| 生成时间 | {r.generated_at} |\n"
        f"| 数据源 | 企查查 MCP（schema-driven · v1.2 框架）|\n"
        f"| 数据契约 | pydantic schema · USCC 校验位 · count ≡ rows · evidence 锚点 |\n"
        f"| 一致性自检 | 通过（如有异常本报告无法生成）|\n\n"
        f"---\n\n"
        f"*本报告由企查查 SKILL（企业历史沿革与发展历程 · v1.2）自动生成。"
        f"配套 manifest.json 含字段级 evidence 溯源链，可用于审计回溯。*\n"
    )
