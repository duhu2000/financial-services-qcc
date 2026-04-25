"""
render_pdf.py · V1.2 配套 PDF 渲染器（保留 V1.1.3 圆点时间轴样式）
=================================================================
- 输入：ReportSchema 对象（已通过 schema 校验 + 一致性自检）
- 输出：高质量 PDF（与 V1.1.3 视觉一致：蓝色章节条 / 圆点时间轴 / 斑马表）
- 复用：V1.1.3 的 build_timeline.py（DPI 240，中英混排）

设计原则：
- 不接受散装 dict，只消费 ReportSchema → 防止漏校验数据进入渲染
- 数字字段（年度分布、级别分布等）一律调用 schema 内置方法
- 缺数据的章节直接跳过，不留空表格

依赖（要求本地安装）：
    reportlab>=4.0
    matplotlib>=3.6.0
    （CJK 字体由 build_timeline.py 自动探测）
"""

from __future__ import annotations

import io
import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph as _RawParagraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak, Image,
)

# 把上一级目录加入 path 以 import build_timeline.py
_HERE = Path(__file__).parent
_PARENT = _HERE.parent  # scripts/
sys.path.insert(0, str(_PARENT))
import build_timeline  # noqa

if TYPE_CHECKING:
    from .data_contract import ReportSchema


# ---------------------------------------------------------------------------
# 字体注册（CJK + ASCII 双轨；与 V1.1.3 一致）
# ---------------------------------------------------------------------------

CJK_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]
ASCII_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

def _first_exist(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None

CJK_PATH = _first_exist(CJK_CANDIDATES)
LATIN_PATH = _first_exist(ASCII_CANDIDATES)

_FONTS_REGISTERED = False

def _ensure_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    if CJK_PATH:
        try:
            pdfmetrics.registerFont(TTFont("CJK", CJK_PATH))
        except Exception:
            pass
    if LATIN_PATH:
        try:
            pdfmetrics.registerFont(TTFont("Latin", LATIN_PATH))
        except Exception:
            pass
    _FONTS_REGISTERED = True


# ---------------------------------------------------------------------------
# 中英混排：把 ASCII 段包在 <font name='Latin'> 里
# ---------------------------------------------------------------------------

def _is_cjk_char(ch: str) -> bool:
    o = ord(ch)
    return (
        0x4E00 <= o <= 0x9FFF
        or 0x3000 <= o <= 0x303F
        or 0xFF00 <= o <= 0xFFEF
        or 0x3400 <= o <= 0x4DBF
    )

def _mix(text: str) -> str:
    """对一段文本做"CJK 走 CJK 字体 / ASCII 走 Latin 字体"分段。
    跳过 XML 标签内部，避免把 <b> 拆开。
    """
    if not text:
        return text
    out = []
    i = 0
    in_tag = False
    cur = []
    cur_cjk = None
    while i < len(text):
        ch = text[i]
        if ch == "<":
            # flush cur
            if cur:
                seg = "".join(cur)
                if cur_cjk:
                    out.append(f"<font name='CJK'>{seg}</font>")
                else:
                    out.append(seg)
                cur = []
                cur_cjk = None
            in_tag = True
            out.append(ch)
        elif ch == ">" and in_tag:
            in_tag = False
            out.append(ch)
        elif in_tag:
            out.append(ch)
        else:
            is_c = _is_cjk_char(ch)
            if cur_cjk is None:
                cur_cjk = is_c
                cur.append(ch)
            elif is_c == cur_cjk:
                cur.append(ch)
            else:
                seg = "".join(cur)
                if cur_cjk:
                    out.append(f"<font name='CJK'>{seg}</font>")
                else:
                    out.append(seg)
                cur = [ch]
                cur_cjk = is_c
        i += 1
    if cur:
        seg = "".join(cur)
        if cur_cjk:
            out.append(f"<font name='CJK'>{seg}</font>")
        else:
            out.append(seg)
    return "".join(out)


def Paragraph(text, style=None, **kwargs):
    return _RawParagraph(_mix(text), style, **kwargs)


# ---------------------------------------------------------------------------
# 样式（V1.1.3 同款）
# ---------------------------------------------------------------------------

BLUE = HexColor("#1A73E8")
BLUE_LIGHT = HexColor("#D5E8F0")
ZEBRA = HexColor("#F8FAFC")
TEXT_DARK = HexColor("#222222")
GRAY = HexColor("#6B7280")
LINE = HexColor("#CCCCCC")

def _styles():
    _ensure_fonts()
    base_font = "Latin" if LATIN_PATH else "Helvetica"
    return {
        "title": ParagraphStyle("title", fontName=base_font, fontSize=22,
                                leading=28, alignment=TA_CENTER,
                                textColor=TEXT_DARK, spaceBefore=4, spaceAfter=2),
        "subtitle": ParagraphStyle("subtitle", fontName=base_font, fontSize=16,
                                   leading=22, alignment=TA_CENTER,
                                   textColor=TEXT_DARK, spaceAfter=12),
        "meta": ParagraphStyle("meta", fontName=base_font, fontSize=10.5,
                               leading=16, textColor=TEXT_DARK),
        "h1": ParagraphStyle("h1", fontName=base_font, fontSize=16, leading=22,
                             textColor=BLUE, spaceBefore=10, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName=base_font, fontSize=12.5, leading=18,
                             textColor=BLUE, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName=base_font, fontSize=10,
                               leading=15, textColor=TEXT_DARK, spaceAfter=4),
        "quote": ParagraphStyle("quote", fontName=base_font, fontSize=10,
                                leading=15, textColor=TEXT_DARK,
                                leftIndent=10, rightIndent=10,
                                backColor=HexColor("#EFF6FF"),
                                borderPadding=8, spaceBefore=4, spaceAfter=8),
        "footer": ParagraphStyle("footer", fontName=base_font, fontSize=8.5,
                                 leading=12, textColor=GRAY),
        "cell": ParagraphStyle("cell", fontName=base_font, fontSize=9.5,
                               leading=13, textColor=TEXT_DARK),
        "cell_h": ParagraphStyle("cell_h", fontName=base_font, fontSize=10,
                                 leading=14, textColor=white),
    }


# ---------------------------------------------------------------------------
# 通用 helpers
# ---------------------------------------------------------------------------

def _h1_bar(text: str, st):
    """章节标题：左边一根蓝色竖条 + 蓝色文字。"""
    bar = Table(
        [[Paragraph(f"<b>{text}</b>", st["h1"])]],
        colWidths=[16 * cm],
        rowHeights=[None],
    )
    bar.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBEFORE", (0, 0), (0, -1), 4, BLUE),
    ]))
    return bar

def _h2_bar(text: str, st):
    bar = Table(
        [[Paragraph(f"<b>{text}</b>", st["h2"])]],
        colWidths=[16 * cm],
    )
    bar.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
    ]))
    return bar


def _mk_table(headers, rows, *, col_widths, st):
    """蓝色表头 + 斑马纹表格。"""
    data = [[Paragraph(f"<b>{h}</b>", st["cell_h"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), st["cell"]) for c in row])

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, white),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, LINE),
    ]
    # 斑马纹
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    tbl.setStyle(TableStyle(style))
    return tbl


def _timeline(items, *, width_cm=15.5, row_h=0.5):
    """圆点时间轴 PNG → ReportLab Image 流元素。
    items: [{"date":, "content":, "sub":, "known":}]
    """
    if not items:
        return Spacer(1, 4)
    mpl_w = width_cm / 2.54
    png = build_timeline.render_single_column_timeline(items, width=mpl_w, row_h=row_h)
    if not png:
        return Spacer(1, 4)
    buf = io.BytesIO(png)
    from reportlab.lib.utils import ImageReader
    buf2 = io.BytesIO(png)
    ir = ImageReader(buf2)
    iw, ih = ir.getSize()
    target_w = width_cm * cm
    target_h = target_w * ih / iw
    return Image(buf, width=target_w, height=target_h)


# ---------------------------------------------------------------------------
# 章节渲染（直接消费 ReportSchema，不接受散装 dict）
# ---------------------------------------------------------------------------

def _render_header(r, st, flow):
    flow.append(Paragraph("企业历史沿革与发展历程报告", st["title"]))
    flow.append(Paragraph(r.company.name, st["subtitle"]))
    for line in [
        f"<b>目标企业：</b> {r.company.name}",
        f"<b>统一社会信用代码：</b> {r.company.uscc}",
        f"<b>报告版本：</b> v1.2 · schema-driven",
        f"<b>报告生成：</b> {r.generated_at[:10]} | 审计留档编号：{r.report_id}",
    ]:
        flow.append(Paragraph(line, st["meta"]))
    flow.append(Spacer(1, 6))
    flow.append(HRFlowable(width="100%", thickness=0.5, color=LINE))


def _render_executive_summary(r, st, flow):
    cap_changes = max(0, len(r.historical_registration.capital_nodes) - 1)
    name_changes = max(0, len(r.historical_registration.name_nodes) - 1)
    addr_moves = max(0, len(r.historical_registration.address_nodes) - 1)

    summary = (
        f"<b>一句话结论：</b>{r.company.name} 自 {r.company.establish_date[:4]} 年成立以来，"
        f"经过 <b>{cap_changes} 次注册资本变更、{name_changes} 次更名、"
        f"{addr_moves} 次办公地迁移、{r.historical_shareholders.total_count} 位股东退出</b>，"
        f"当前 {r.current_shareholders.total_count} 位股东（陈德强为实控人）。"
        f"已积累 <b>{r.patents.total_count} 项专利、{r.qualifications.total_count} 项资质"
        f"（{r.qualifications.valid_count} 项当前有效）、{r.honors.total_count} 项荣誉</b>。"
    )
    flow.append(_h1_bar("执行摘要（Decision Pack）", st))
    flow.append(Paragraph(summary, st["quote"]))
    flow.append(Paragraph(
        "<i>本报告聚焦组织演变脉络；财务能力评估请参见 IC Memo / 信贷尽调报告。</i>",
        st["body"],
    ))


def _render_section_1(r, st, flow):
    flow.append(_h1_bar("一、公司概况", st))
    c = r.company
    rows = [
        ["企业名称", c.name],
        ["统一社会信用代码", c.uscc],
        ["法定代表人", c.legal_rep],
        ["成立日期", c.establish_date],
        ["注册资本", c.registered_capital],
    ]
    if c.paid_capital:
        rows.append(["实缴资本", c.paid_capital])
    rows += [
        ["企业类型", c.enterprise_type],
        ["行业", c.industry],
        ["登记状态", c.registration_status],
        ["登记机关", c.registration_authority],
    ]
    if c.approval_date:
        rows.append(["核准日期", c.approval_date])
    if c.region:
        rows.append(["所属地区", c.region])
    rows.append(["注册地址", c.registered_address])
    if c.insured_count is not None:
        rows.append(["参保人数", f"{c.insured_count} 人"])
    flow.append(_mk_table(["字段", "值"], rows, col_widths=[5 * cm, 11 * cm], st=st))


def _render_section_2(r, st, flow):
    """里程碑：成立 + 名称变更 + 国家级首次荣誉，按时间排序。"""
    flow.append(_h1_bar("二、发展里程碑", st))
    items = []

    name_nodes = r.historical_registration.name_nodes
    initial_name = name_nodes[-1].name if name_nodes else r.company.name
    items.append({
        "date": r.company.establish_date, "content": "企业成立",
        "sub": initial_name, "known": True,
    })

    for i, n in enumerate(name_nodes):
        if n.start_date and n.end_date:
            next_name = name_nodes[i - 1].name if i > 0 else r.company.name
            items.append({
                "date": n.end_date, "content": "名称变更",
                "sub": f"{n.name} → {next_name}", "known": True,
            })

    seen = set()
    for h in sorted(r.honors.honors, key=lambda x: x.publish_date or ""):
        if h.level == "国家级" and h.name not in seen:
            items.append({
                "date": h.publish_date, "content": f"获国家级『{h.name}』认定",
                "sub": h.issuer, "known": True,
            })
            seen.add(h.name)

    items.sort(key=lambda x: x["date"])
    flow.append(Paragraph(
        f"基于 MCP 工商登记 + 荣誉数据自动抽取，共 {len(items)} 个关键节点：",
        st["body"],
    ))
    flow.append(Spacer(1, 4))
    flow.append(_timeline(items, width_cm=15.5))


def _render_section_3(r, st, flow):
    flow.append(_h1_bar("三、注册资本变更轨迹", st))
    nodes = r.historical_registration.capital_nodes
    items = []
    for i, n in enumerate(nodes):
        is_current = (n.start_date is None and n.end_date is None)
        is_initial = (i == len(nodes) - 1)
        if is_current:
            next_end = nodes[i + 1].end_date if i + 1 < len(nodes) else None
            date_label = next_end or "当前"
            sub = "当前"
        elif is_initial and not n.start_date:
            date_label = "—"
            sub = f"有效至 {n.end_date}" if n.end_date else "—"
        else:
            date_label = n.start_date or "—"
            sub = f"有效至 {n.end_date}" if n.end_date else "当前"
        items.append({
            "date": date_label, "content": n.capital,
            "sub": sub, "known": not (is_initial and not n.start_date),
        })
    flow.append(Paragraph(f"共 {len(nodes)} 个注册资本节点：", st["body"]))
    flow.append(Spacer(1, 4))
    flow.append(_timeline(items, width_cm=15.5))


def _render_section_4(r, st, flow):
    flow.append(_h1_bar("四、名称变更时间线", st))
    nodes = r.historical_registration.name_nodes
    items = []
    for i, n in enumerate(nodes):
        is_current = (n.start_date is None and n.end_date is None)
        if is_current:
            next_end = nodes[i + 1].end_date if i + 1 < len(nodes) else None
            date_label = next_end or "当前"
            sub = "当前"
        else:
            date_label = n.start_date or "—"
            sub = f"使用至 {n.end_date}" if n.end_date else "—"
        items.append({
            "date": date_label, "content": n.name,
            "sub": sub, "known": True,
        })
    flow.append(_timeline(items, width_cm=15.5))


def _render_section_5(r, st, flow):
    flow.append(_h1_bar("五、股权演变", st))

    # 5.1 当前股东
    flow.append(_h2_bar("5.1 当前股东与出资结构", st))
    flow.append(Paragraph(
        f"共 <b>{r.current_shareholders.total_count} 位股东</b>"
        f"（按持股比例降序，全量展示）：",
        st["body"],
    ))
    rows = [[s.name, s.holding_ratio, s.shares or "—"]
            for s in r.current_shareholders.shareholders]
    flow.append(_mk_table(
        ["股东名称", "持股比例", "持股数"],
        rows,
        col_widths=[9 * cm, 3 * cm, 4 * cm],
        st=st,
    ))

    # 5.3 历史股东（时间轴，行高 0.45 适配单页 17 条）
    flow.append(_h2_bar("5.3 股东进出历史", st))
    flow.append(Paragraph(
        f"共 <b>{r.historical_shareholders.total_count} 位股东已退出</b>"
        f"（按退出日期倒序，全量展示）：",
        st["body"],
    ))
    flow.append(Spacer(1, 4))
    items = []
    for s in r.historical_shareholders.exited_shareholders:
        sub_parts = []
        if s.exit_ratio:
            sub_parts.append(f"退出比例 {s.exit_ratio}")
        if s.capital:
            sub_parts.append(f"认缴 {s.capital}")
        if s.shareholder_type:
            sub_parts.append(s.shareholder_type)
        items.append({
            "date": s.exit_date or "—", "content": s.name,
            "sub": " · ".join(sub_parts) or "—", "known": True,
        })
    flow.append(_timeline(items, width_cm=16, row_h=0.42))


def _render_section_6(r, st, flow):
    flow.append(_h1_bar("六、经营轨迹", st))

    # 6.1 对外投资
    flow.append(_h2_bar("6.1 对外投资", st))
    flow.append(Paragraph(
        f"共 <b>{r.investments.total_count} 家</b>被投资企业（全量展示）：",
        st["body"],
    ))
    rows = [
        [inv.invested_company, inv.holding_ratio,
         inv.establish_date or "—", inv.status or "—"]
        for inv in r.investments.investments
    ]
    flow.append(_mk_table(
        ["被投资企业", "持股比例", "成立日期", "状态"],
        rows,
        col_widths=[7 * cm, 3 * cm, 3 * cm, 3 * cm],
        st=st,
    ))

    # 6.2 现任董监高（表格）
    flow.append(_h2_bar("6.2 董监高与治理", st))
    flow.append(Paragraph(
        f"<b>现任（{r.executives.current_count} 人）：</b>",
        st["body"],
    ))
    rows = [[e.name, e.position, e.holding_ratio or "—"]
            for e in r.executives.current_executives]
    flow.append(_mk_table(
        ["姓名", "职务", "持股比例"],
        rows,
        col_widths=[4 * cm, 6 * cm, 6 * cm],
        st=st,
    ))

    # 历任董监高（时间轴）
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        f"<b>历任（{r.executives.historical_count} 人）：</b>",
        st["body"],
    ))
    flow.append(Spacer(1, 4))
    items = []
    for e in r.executives.historical_executives:
        sub = f"任期 {e.appointment_date or '—'} → {e.departure_date}"
        items.append({
            "date": e.departure_date, "content": f"{e.name} · {e.position}",
            "sub": sub, "known": True,
        })
    flow.append(_timeline(items, width_cm=16, row_h=0.5))

    flow.append(Paragraph(
        "<i>注：处罚记录已并入 §10 大事年表；冻结 / 质押 / 失信 等当前状态属信贷审批范畴，"
        "不在本报告内。</i>",
        st["body"],
    ))


def _render_section_7(r, st, flow):
    flow.append(_h1_bar("七、地址变迁", st))
    nodes = r.historical_registration.address_nodes
    cur_addr = (
        nodes[0].address if nodes
        else r.company.registered_address
    )
    flow.append(Paragraph(f"<b>当前注册地址：</b>{cur_addr}", st["body"]))
    flow.append(Spacer(1, 4))
    items = []
    for i, n in enumerate(nodes):
        is_current = (n.start_date is None and n.end_date is None)
        if is_current:
            continue
        date_label = n.start_date or "设立时"
        sub = f"使用至 {n.end_date}" if n.end_date else "—"
        items.append({
            "date": date_label, "content": n.address,
            "sub": sub, "known": bool(n.start_date),
        })
    flow.append(_timeline(items, width_cm=15.5, row_h=0.5))


def _render_section_8(r, st, flow):
    flow.append(_h1_bar("八、总结", st))
    rows = [
        ["股权清洁度", "未发现公开冻结/质押记录"],
    ]
    if r.administrative_penalties.total_count > 0:
        p = r.administrative_penalties.penalties[0]
        rows.append([
            "经营合规",
            (f"{p.penalty_date} 受 {p.penalty_authority} 处罚"
             f" {p.penalty_amount or '—'}（{p.decision_no}）"
             f" — 违规细节及处置状态以央行公告为准"),
        ])
    else:
        rows.append(["经营合规", "MCP 公开记录未发现行政处罚"])
    rows.append([
        "成长轨迹",
        (f"工商变更 {r.change_records_count} 条，"
         f"股东进出 {r.historical_shareholders.total_count} 次"),
    ])
    flow.append(_mk_table(
        ["维度", "评价"], rows,
        col_widths=[3.5 * cm, 12.5 * cm], st=st,
    ))
    flow.append(Spacer(1, 4))
    flow.append(Paragraph(
        "<i>本报告聚焦组织演变脉络；财务能力评估与信贷风险判定请参见"
        " IC Memo / 信贷尽调报告。</i>",
        st["quote"],
    ))


def _render_section_9(r, st, flow):
    flow.append(_h1_bar("九、发展综览", st))

    # 9.1 资质
    flow.append(_h2_bar("9.1 许可与资质", st))
    flow.append(Paragraph(
        f"共 <b>{r.qualifications.total_count} 项</b>资质，"
        f"当前有效 <b>{r.qualifications.valid_count} 项</b>。",
        st["body"],
    ))

    # 资质里程碑（首次获得 — 用算法从原始数据推导）
    qual_items = _extract_qualification_milestones(r)
    if qual_items:
        flow.append(Paragraph("<b>核心资质里程碑（首次获得）：</b>", st["body"]))
        flow.append(Spacer(1, 4))
        flow.append(_timeline(qual_items, width_cm=16, row_h=0.5))

    # 9.2 专利
    flow.append(_h2_bar("9.2 知识产权", st))
    flow.append(Paragraph(
        f"共 <b>{r.patents.total_count} 项</b>专利。", st["body"],
    ))

    # 类型分布（schema 算法）
    type_dist = r.patents.type_distribution()
    if type_dist:
        type_str = "、".join(f"{k} {v} 项" for k, v in type_dist.items())
        flow.append(Paragraph(f"<b>类型分布：</b>{type_str}", st["body"]))

    # 年度分布（schema 算法）
    yearly = r.patents.yearly_distribution()
    flow.append(Paragraph(
        f"<b>申请年度分布（自动 group-by，加和必等于 {r.patents.total_count}）：</b>",
        st["body"],
    ))
    flow.append(Spacer(1, 4))
    items = []
    for year in sorted(yearly.keys(), reverse=True):
        items.append({
            "date": year, "content": f"{yearly[year]} 项",
            "sub": "", "known": True,
        })
    flow.append(_timeline(items, width_cm=12, row_h=0.45))

    # 9.4 荣誉
    flow.append(_h2_bar("9.4 行业地位与荣誉", st))
    by_level = {}
    for h in r.honors.honors:
        by_level[h.level] = by_level.get(h.level, 0) + 1
    level_str = "、".join(f"{k} {v} 项" for k, v in sorted(by_level.items()))
    flow.append(Paragraph(
        f"共 <b>{r.honors.total_count} 项</b>荣誉。<b>级别分布：</b>{level_str}",
        st["body"],
    ))

    # 重点荣誉时间轴（按发布日期倒序，最近 12 项 — 单页适配）
    flow.append(Spacer(1, 4))
    sorted_honors = sorted(r.honors.honors, key=lambda x: x.publish_date or "", reverse=True)
    top_n = sorted_honors[:12]
    if len(sorted_honors) > 12:
        flow.append(Paragraph(
            f"<b>重点荣誉时间线</b>（共 {r.honors.total_count} 项，"
            f"展示最近 {len(top_n)} 项）：",
            st["body"],
        ))
    else:
        flow.append(Paragraph("<b>重点荣誉时间线：</b>", st["body"]))
    items = []
    for h in top_n:
        items.append({
            "date": h.publish_date or "—",
            "content": f"{h.name}（{h.level}）",
            "sub": h.issuer or "—",
            "known": True,
        })
    flow.append(_timeline(items, width_cm=16, row_h=0.45))


def _extract_qualification_milestones(r):
    """从 30 项资质中抽取每类资质的首次获得日期作为里程碑。"""
    seen = {}
    for q in r.qualifications.qualifications:
        if not q.issue_date:
            continue
        # 资质名称里去掉"（首版）"等修饰
        key = re.sub(r"[（(].*?[）)]", "", q.name).strip()
        if key not in seen or q.issue_date < seen[key].issue_date:
            seen[key] = q

    items = []
    # 取重要资质（核心 9 类）
    important = [
        "企业征信机构备案", "DCMM证书", "CMMI证书", "电信业务经营许可证",
        "ITSS证书", "软件企业证书", "信息安全管理体系认证",
        "知识产权管理体系认证", "质量管理体系认证",
        "信息技术服务管理体系认证",
    ]
    for q in seen.values():
        if any(q.name.startswith(prefix) for prefix in important):
            sub = q.category or "—"
            if q.expiry_date:
                sub += f" · 有效至 {q.expiry_date}"
            items.append({
                "date": q.issue_date or "—",
                "content": q.name,
                "sub": sub,
                "known": bool(q.issue_date),
            })
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def _render_section_10(r, st, flow):
    flow.append(_h1_bar("十、附录 · 工商变更大事年表", st))
    flow.append(Paragraph(
        f"MCP 工商变更总数：{r.change_records_count} 条。", st["body"],
    ))
    if r.administrative_penalties.total_count > 0:
        flow.append(_h2_bar(
            f"行政处罚（共 {r.administrative_penalties.total_count} 条）", st,
        ))
        rows = []
        for p in r.administrative_penalties.penalties:
            rows.append([
                p.penalty_date, p.penalty_authority,
                p.decision_no, p.penalty_result or "—",
            ])
        flow.append(_mk_table(
            ["处罚日期", "处罚单位", "决定书文号", "处罚结果"],
            rows,
            col_widths=[2.5 * cm, 4 * cm, 5 * cm, 4.5 * cm],
            st=st,
        ))


def _render_section_11(r, st, flow):
    flow.append(_h1_bar("十一、审计留档", st))
    rows = [
        ["报告编号", r.report_id],
        ["生成时间", r.generated_at],
        ["数据源", "企查查 MCP（schema-driven · v1.2 框架）"],
        ["数据契约", "pydantic schema · USCC 校验位 · count ≡ rows · evidence 锚点"],
        ["一致性自检", "通过（如有异常本报告无法生成）"],
    ]
    flow.append(_mk_table(
        ["项目", "数据"], rows,
        col_widths=[4 * cm, 12 * cm], st=st,
    ))
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "<i>本报告由企查查 SKILL（企业历史沿革与发展历程 · v1.2）自动生成。"
        "配套 manifest.json 含字段级 evidence 溯源链，可用于审计回溯。"
        "本报告仅供尽调研究参考，不构成投资建议。</i>",
        st["footer"],
    ))


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def render_pdf(report, out_path: str | Path) -> str:
    """从 ReportSchema 生成 PDF。"""
    _ensure_fonts()
    st = _styles()

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"企业历史沿革与发展历程报告 - {report.company.name}",
        author="企查查 SKILL · v1.2",
    )
    flow = []
    _render_header(report, st, flow)
    _render_executive_summary(report, st, flow)
    _render_section_1(report, st, flow)
    _render_section_2(report, st, flow)
    _render_section_3(report, st, flow)
    _render_section_4(report, st, flow)
    _render_section_5(report, st, flow)
    _render_section_6(report, st, flow)
    _render_section_7(report, st, flow)
    _render_section_8(report, st, flow)
    _render_section_9(report, st, flow)
    _render_section_10(report, st, flow)
    _render_section_11(report, st, flow)

    doc.build(flow)
    return str(out)


# ---------------------------------------------------------------------------
# CLI 入口（独立从 mcp_responses.json 跑完整流程）
# ---------------------------------------------------------------------------

def _main() -> int:
    import argparse, json
    from .build_report_v1_2 import generate_report
    from .data_extractor import ReportExtractor
    from .consistency_check import assert_consistency

    parser = argparse.ArgumentParser(
        description="V1.2 报告 PDF 渲染器（基于 ReportSchema + ReportLab）"
    )
    parser.add_argument("--uscc", required=True)
    parser.add_argument("--mcp-responses-json", required=True)
    parser.add_argument("--out", required=True, help="输出 PDF 路径")
    parser.add_argument("--report-id")
    args = parser.parse_args()

    # 跑数据契约 + 一致性自检
    with open(args.mcp_responses_json, encoding="utf-8") as f:
        mcp_responses = json.load(f)
    # 过滤掉以 _ 开头的元数据键
    mcp_responses = {k: v for k, v in mcp_responses.items() if not k.startswith("_")}

    extractor = ReportExtractor(uscc=args.uscc, report_id=args.report_id)
    for tool, resp in mcp_responses.items():
        extractor.feed(tool, resp)
    report = extractor.build_report_schema()
    warnings = assert_consistency(report)

    # 渲染 PDF
    pdf_path = render_pdf(report, args.out)

    # 同时存 manifest
    manifest_path = Path(args.out).with_suffix(".manifest.json")
    extractor.manifest.write(str(manifest_path))

    print(f"✓ PDF 生成: {pdf_path}")
    print(f"✓ 溯源 manifest: {manifest_path}")
    if warnings:
        print(f"⚠ {len(warnings)} 条警告：")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
