"""
build_timeline.py · 时间轴 PNG 渲染模块（V1.1）
=====================================================
为 build_docx.py 提供 5 种时间轴 PNG 产出：
  - 注册资本变更轨迹（每节点一行：金额 + 增量）
  - 名称变更时间线
  - 地址变迁时间线
  - 历任法定代表人时间线
  - 股东进出快照（多时间节点 + 每节点股东表）
  - 通用单行时间轴（用于历任董监高、大事年表等）

样式基准：QCC Advanced Report 的 CHANGE HISTORY 章节
  · 主色 #1A73E8，次文 #6B7280，线 #D1D5DB
  · 圆点：已知日期实心 ● 蓝，起点未知空心 ○ 灰
  · 左栏日期 + 中栏竖线 + 右栏内容

中英混排：手动 per-char fallback（matplotlib 自带 fallback 不逐字）
  · CJK 走 Noto/Droid Sans Fallback / PingFang
  · ASCII 走 Liberation Sans / Helvetica / DejaVu Sans
"""

from __future__ import annotations

import io
import os
import warnings
from typing import Any

# 抑制 matplotlib 字体警告
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager


# ---------------------------------------------------------------------------
# 字体解析（按优先级选择 CJK 和 ASCII 字体）
# ---------------------------------------------------------------------------

CJK_FONT_CANDIDATES = [
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    # Linux Noto
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    # Linux WenQuanYi
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
    # Linux Droid fallback
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts-droid-fallback/truetype/DroidSansFallback.ttf",
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
]

ASCII_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def _first_existing(paths: list[str]) -> str | None:
    for p in paths:
        if os.path.exists(p):
            return p
    return None


_CJK_FONT_PATH = _first_existing(CJK_FONT_CANDIDATES)
_ASCII_FONT_PATH = _first_existing(ASCII_FONT_CANDIDATES)

if _CJK_FONT_PATH:
    font_manager.fontManager.addfont(_CJK_FONT_PATH)
if _ASCII_FONT_PATH:
    font_manager.fontManager.addfont(_ASCII_FONT_PATH)

CJK_FP = font_manager.FontProperties(fname=_CJK_FONT_PATH) if _CJK_FONT_PATH else font_manager.FontProperties()
ASCII_FP = font_manager.FontProperties(fname=_ASCII_FONT_PATH) if _ASCII_FONT_PATH else font_manager.FontProperties()


# Advanced Report 配色
BLUE = "#1A73E8"
LIGHT_BLUE_BG = "#EFF6FF"
DARK_TEXT = "#222222"
GRAY_TEXT = "#6B7280"
LINE_GRAY = "#D1D5DB"


# ---------------------------------------------------------------------------
# 中英混排核心
# ---------------------------------------------------------------------------


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (
        0x4E00 <= o <= 0x9FFF
        or 0x3000 <= o <= 0x303F
        or 0xFF00 <= o <= 0xFFEF
        or 0x3400 <= o <= 0x4DBF
    )


def _split_segments(text: str) -> list[tuple[str, bool]]:
    if not text:
        return []
    segs: list[tuple[str, bool]] = []
    cur = [text[0]]
    cur_cjk = _is_cjk(text[0])
    for ch in text[1:]:
        ch_cjk = _is_cjk(ch)
        if ch_cjk == cur_cjk:
            cur.append(ch)
        else:
            segs.append(("".join(cur), cur_cjk))
            cur = [ch]
            cur_cjk = ch_cjk
    segs.append(("".join(cur), cur_cjk))
    return segs


def _soft_wrap_cjk(text: str, max_weight: float = 24.0,
                   hard_max_weight: float = 30.0) -> list[str]:
    """长 CJK 字符串软换行：CJK 算 1，ASCII 算 0.5。
    优先在地址常见分隔符（号/室/楼/层/幢/栋/座/院/园/路/街）后换行；
    若超过 hard_max_weight 仍未找到分隔符，则硬断。
    """
    if not text:
        return [""]
    weight_total = sum(1.0 if _is_cjk(c) else 0.5 for c in text)
    if weight_total <= max_weight:
        return [text]
    break_pat = "号室楼层幢栋座院园区路街道镇)）"
    lines: list[str] = []
    cur = ""
    cur_w = 0.0
    for ch in text:
        w = 1.0 if _is_cjk(ch) else 0.5
        cur += ch
        cur_w += w
        if cur_w >= max_weight and ch in break_pat:
            lines.append(cur)
            cur, cur_w = "", 0.0
        elif cur_w >= hard_max_weight:
            # 没遇到合适分隔符 — 硬断（避免单行过长撑出画布）
            lines.append(cur)
            cur, cur_w = "", 0.0
    if cur:
        lines.append(cur)
    return lines


def _draw_text_line(ax, x: float, y: float, text: str, *,
                    fontsize: float, color: str, ha: str, va: str) -> None:
    """单行渲染（不处理换行）。按字符类型分段、各段用对应字体画。"""
    if not text:
        return
    fig = ax.get_figure()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    segments = _split_segments(text)
    pixel_widths: list[float] = []
    for seg, is_cjk in segments:
        fp = CJK_FP if is_cjk else ASCII_FP
        t = ax.text(0, 0, seg, fontsize=fontsize, fontproperties=fp, alpha=0)
        try:
            bbox = t.get_window_extent(renderer=renderer)
            pixel_widths.append(bbox.width)
        except Exception:
            pixel_widths.append(fontsize * (1.1 if is_cjk else 0.55) * len(seg))
        t.remove()

    trans_inv = ax.transData.inverted()
    p0 = trans_inv.transform((0, 0))
    p1 = trans_inv.transform((1, 0))
    data_per_pixel = abs(p1[0] - p0[0])
    total_data_w = sum(pixel_widths) * data_per_pixel

    if ha == "right":
        start_x = x - total_data_w
    elif ha == "center":
        start_x = x - total_data_w / 2
    else:
        start_x = x

    cur_x = start_x
    for (seg, is_cjk), pw in zip(segments, pixel_widths):
        fp = CJK_FP if is_cjk else ASCII_FP
        ax.text(cur_x, y, seg, fontsize=fontsize, fontproperties=fp,
                color=color, ha="left", va=va)
        cur_x += pw * data_per_pixel


def _line_height_data(ax, fontsize: float, line_factor: float = 1.25) -> float:
    """估算一行文本在数据坐标系里占多少高度（用于换行垂直让位）。"""
    fig = ax.get_figure()
    fig_h_inch = fig.get_size_inches()[1]
    if fig_h_inch <= 0:
        return 0.4
    y0, y1 = ax.get_ylim()
    y_range = y1 - y0
    line_h_inch = fontsize * line_factor / 72.0
    return (line_h_inch / fig_h_inch) * y_range


def _draw_mixed(ax, x: float, y: float, text: str, *,
                fontsize: float = 10,
                color: str = DARK_TEXT,
                ha: str = "left",
                va: str = "center") -> None:
    """按字符类型分段、用对应字体画文字；支持 `\n` 多行（每行依次向下偏移）。"""
    if not text:
        return
    if "\n" not in text:
        _draw_text_line(ax, x, y, text, fontsize=fontsize, color=color,
                        ha=ha, va=va)
        return
    lines = text.split("\n")
    line_h = _line_height_data(ax, fontsize)
    for i, line in enumerate(lines):
        _draw_text_line(ax, x, y - i * line_h, line,
                        fontsize=fontsize, color=color, ha=ha, va=va)


# ---------------------------------------------------------------------------
# 时间轴通用底层
# ---------------------------------------------------------------------------


def _render_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    # DPI 提高到 240 以避免 PDF 嵌入缩放后的字形粘连/糊化
    fig.savefig(buf, format="png", dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_single_column_timeline(
    items: list[dict],
    *,
    title: str | None = None,
    width: float = 11.0,
    row_h: float = 0.6,
) -> bytes:
    """通用单列时间轴。items: [{"date": str, "content": str, "sub": str, "known": bool}, ...]
    返回 PNG bytes。

    自适应：长 content（如完整地址）会自动按地址语义软换行成 2~3 行；
            行数大于 1 的 item 会获得更高的 row 间距，避免文字与上下行重叠。
    """
    if not items:
        return b""

    # Step 1 · 内容预换行 — 决定每个 item 实际占几行（content 行数）
    #         同时把 line 数累加成 y 坐标（avoid 横向溢出导致 bbox_inches 横向膨胀压缩）
    prepped: list[dict] = []
    for it in items:
        raw_content = it.get("content", "")
        wrapped_lines = _soft_wrap_cjk(raw_content, max_weight=24.0,
                                       hard_max_weight=28.0)
        prepped.append({
            **it,
            "content_wrapped": "\n".join(wrapped_lines),
            "n_lines": max(1, len(wrapped_lines)),
        })

    # Step 2 · 计算每个 item 的 row 跨度（行数越多，留白越大）
    #         单行 = 1.0；多行 = 1.0 + (n_lines-1) * 0.4。
    #         注意：不为 sub 单独加 row span — sub 紧贴 content 最后一行下方渲染，
    #         挤进当前 row 内的视觉留白即可，避免整体 figure 高度膨胀，
    #         否则会触发 ReportLab 把时间轴整体推到下一页（出现大片空白）。
    row_spans: list[float] = []
    for p in prepped:
        span = 1.0 + (p["n_lines"] - 1) * 0.4
        row_spans.append(span)

    total_rows = sum(row_spans)
    fig_h = (0.9 if title else 0.4) + row_h * total_rows
    fig, ax = plt.subplots(figsize=(width, fig_h))

    # Step 3 · 拉宽 xlim 给地址留更多列宽；同时把 dot 与 date 的间距加大
    ax.set_xlim(0, 14)
    ax.set_ylim(0, total_rows + (1.0 if title else 0.5))
    ax.axis("off")
    fig.canvas.draw()

    if title:
        _draw_mixed(ax, 0.2, total_rows + 0.5, title, fontsize=14, color=BLUE)

    x_date = 2.0     # 日期右对齐边
    x_dot = 2.85     # 圆点 — 与 x_date 间距 0.85（之前 0.7），避免被压缩盖住
    x_content = 3.25 # 内容左起边 — 与 x_dot 间距 0.4

    # 用动态行高 — 让 sub 副文本能精准贴在 content 最后一行下方
    content_fontsize = 11.5
    sub_fontsize = 9.5
    content_line_h = _line_height_data(ax, content_fontsize)

    # Step 4 · 反向 y 坐标：第一项在最上方
    cur_y = total_rows
    for p, span in zip(prepped, row_spans):
        # 当前 item 的中心 y（圆点位置）— 在 span 区间靠上 0.4 处
        y_center = cur_y - 0.4
        known = p.get("known", True)
        # 日期 — 始终单行
        _draw_mixed(ax, x_date, y_center, p.get("date", ""), fontsize=10.5,
                    color=DARK_TEXT if known else GRAY_TEXT, ha="right")
        # 圆点
        if known:
            ax.plot(x_dot, y_center, "o", markersize=9, color=BLUE, zorder=3)
        else:
            ax.plot(x_dot, y_center, "o", markersize=9,
                    mfc="white", mec=GRAY_TEXT, mew=1.5, zorder=3)
        # 内容 — 多行依次向下；首行 anchor 略高于圆点
        _draw_mixed(ax, x_content, y_center + 0.14, p.get("content_wrapped", ""),
                    fontsize=content_fontsize, color=DARK_TEXT)
        # 副文本 — 紧贴 content 最后一行下方（按动态行高定位，避免错位）
        sub = p.get("sub", "")
        if sub:
            sub_y = y_center + 0.14 - p["n_lines"] * content_line_h * 0.95
            _draw_mixed(ax, x_content, sub_y, sub,
                        fontsize=sub_fontsize, color=GRAY_TEXT)

        cur_y -= span

    # 时间轴竖线 — 从最后一行下方延到最上方
    ax.plot([x_dot, x_dot], [0.3, total_rows + 0.1],
            color=LINE_GRAY, linewidth=1.2, zorder=1)
    plt.tight_layout()
    return _render_to_bytes(fig)


def render_shareholder_snapshot_timeline(
    snapshots: list[dict],
    *,
    title: str | None = None,
    width: float = 13.0,
) -> bytes:
    """股东快照式：每日期节点下渲染完整股东表。
    snapshots: [{"date": str, "holders": [{"name", "ratio", "capital"}, ...]}, ...]
    """
    if not snapshots:
        return b""

    total_rows = sum(1 + len(s.get("holders", [])) + 1 for s in snapshots)
    fig_h = (1.1 if title else 0.3) + 0.42 * total_rows
    fig, ax = plt.subplots(figsize=(width, fig_h))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, total_rows + (1.0 if title else 0.5))
    ax.axis("off")
    fig.canvas.draw()

    if title:
        _draw_mixed(ax, 0.2, total_rows + 0.6, title, fontsize=14, color=BLUE)

    x_date = 2.0
    x_dot = 2.7
    x_name = 3.1
    x_ratio = 8.5
    x_shares = 10.5

    y = total_rows

    for snap in snapshots:
        _draw_mixed(ax, x_date, y, snap.get("date", ""), fontsize=11,
                    color=DARK_TEXT, ha="right")
        ax.plot(x_dot, y, "o", markersize=10, color=BLUE, zorder=3)

        y -= 0.9
        for xp, label in [(x_name, "股东名称"), (x_ratio, "持股比例"),
                          (x_shares, "认缴出资额")]:
            _draw_mixed(ax, xp, y, label, fontsize=9, color=GRAY_TEXT)

        for h in snap.get("holders", []):
            y -= 0.6
            _draw_mixed(ax, x_name, y, h.get("name", ""), fontsize=10, color=DARK_TEXT)
            _draw_mixed(ax, x_ratio, y, h.get("ratio", ""), fontsize=10, color=DARK_TEXT)
            _draw_mixed(ax, x_shares, y, h.get("capital", ""), fontsize=10, color=DARK_TEXT)

        y -= 0.9

    ax.plot([x_dot, x_dot], [0.3, total_rows], color=LINE_GRAY, linewidth=1.2, zorder=1)
    plt.tight_layout()
    return _render_to_bytes(fig)


# ---------------------------------------------------------------------------
# 业务包装层（build_docx 直接调用）
# ---------------------------------------------------------------------------


def timeline_capital(hist_capital: list[dict]) -> bytes:
    """hist_capital: [{历史注册资本, 起始日期, 终止日期}, ...]"""
    items = []
    for rec in hist_capital:
        date = rec.get("起始日期") or "—"
        known = bool(rec.get("起始日期"))
        items.append({
            "date": date,
            "content": rec.get("历史注册资本", ""),
            "sub": f"有效至 {rec.get('终止日期') or '至今'}" if rec.get("终止日期") else "",
            "known": known,
        })
    return render_single_column_timeline(items, width=11)


def timeline_name(hist_name: list[dict]) -> bytes:
    items = []
    for rec in hist_name:
        date = rec.get("起始日期") or "—"
        items.append({
            "date": date,
            "content": rec.get("历史名称", ""),
            "sub": f"使用至 {rec.get('终止日期') or '至今'}" if rec.get("终止日期") else "",
            "known": bool(rec.get("起始日期")),
        })
    return render_single_column_timeline(items, width=12)


def timeline_address(hist_addr: list[dict]) -> bytes:
    items = []
    for rec in hist_addr:
        date = rec.get("起始日期") or "—"
        items.append({
            "date": date,
            "content": rec.get("历史地址", ""),
            "sub": f"使用至 {rec.get('终止日期') or '至今'}" if rec.get("终止日期") else "",
            "known": bool(rec.get("起始日期")),
        })
    return render_single_column_timeline(items, width=13)


def timeline_legal_rep(hist_legal: list[dict]) -> bytes:
    items = []
    for rec in hist_legal:
        start = rec.get("任职日期") or "—"
        end = rec.get("卸任日期") or "至今"
        items.append({
            "date": start,
            "content": rec.get("名称", ""),
            "sub": f"任职至 {end}",
            "known": bool(rec.get("任职日期")),
        })
    return render_single_column_timeline(items, width=11)


def timeline_historical_executives(execs: list[dict]) -> bytes:
    """历任董监高 —— 按卸任日期倒序（最近的在上）"""
    # 先按卸任日期倒序
    sorted_execs = sorted(execs, key=lambda e: e.get("卸任日期") or "9999", reverse=True)
    items = []
    for rec in sorted_execs:
        start = rec.get("任职日期") or "—"
        end = rec.get("卸任日期") or "至今"
        name = rec.get("姓名", "")
        job = rec.get("职务", "")
        items.append({
            "date": end,
            "content": f"{name} · {job}",
            "sub": f"任期 {start} → {end}",
            "known": bool(rec.get("卸任日期")),
        })
    return render_single_column_timeline(items, width=12)


def timeline_shareholder_exits(hist_shareholders: list[dict]) -> bytes:
    """股东进出历史（单列版，适合中小规模）。按退出日期倒序。
    每行：日期 · 股东名称 · 退出比例/出资。
    """
    sorted_sh = sorted(hist_shareholders,
                       key=lambda s: s.get("退出日期") or "",
                       reverse=True)
    items = []
    for rec in sorted_sh:
        date = rec.get("退出日期") or "—"
        name = rec.get("股东名称", "")
        stype = rec.get("股东类型", "")
        ratio = rec.get("退出时持股比例") or ""
        capital = rec.get("认缴出资额") or ""
        sub_parts = []
        if ratio:
            sub_parts.append(f"退出比例 {ratio}")
        if capital:
            sub_parts.append(f"认缴 {capital}")
        if stype:
            sub_parts.append(stype)
        items.append({
            "date": date,
            "content": name,
            "sub": " · ".join(sub_parts),
            "known": bool(rec.get("退出日期")),
        })
    return render_single_column_timeline(items, width=13)


def timeline_change_records(changes: list[dict], max_items: int = 40) -> bytes:
    """大事年表（附录用）——按日期倒序，内容简化"""
    sorted_c = sorted(changes, key=lambda c: c.get("变更日期") or "", reverse=True)
    sorted_c = sorted_c[:max_items]
    items = []
    for rec in sorted_c:
        before = rec.get("变更前内容") or []
        after = rec.get("变更后内容") or []
        before_s = "、".join(before) if isinstance(before, list) else str(before)
        after_s = "、".join(after) if isinstance(after, list) else str(after)
        # 内容截断
        content = rec.get("变更项目", "")
        sub = ""
        if before_s or after_s:
            # 只截取变更的差异核心词
            b_short = (before_s[:60] + "…") if len(before_s) > 60 else before_s
            a_short = (after_s[:60] + "…") if len(after_s) > 60 else after_s
            sub = f"{b_short} → {a_short}"
        items.append({
            "date": rec.get("变更日期", ""),
            "content": content,
            "sub": sub,
            "known": bool(rec.get("变更日期")),
        })
    return render_single_column_timeline(items, width=13, row_h=0.75)


# ---------------------------------------------------------------------------
# V1.1 新增 · §0 里程碑曲线图（PPT P5 风格）
# ---------------------------------------------------------------------------


def render_milestone_curve(events: list[dict], *, title: str = "发展里程碑",
                           width: float = 14.0, height: float = 6.5) -> bytes:
    """PPT P5 风格：淡蓝渐变上升曲线背景 + 年份锚点圆球 + 事件标题
    events: [{"year": "2014", "title": "xxx", "sub": "xxx"}, ...]（时间升序）
    """
    if not events:
        return b""
    n = len(events)
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, n + 1)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.canvas.draw()

    # 背景上升曲线（指数 → 缓增）
    import numpy as np
    x_curve = np.linspace(0.5, n + 0.5, 200)
    y_curve = 1.5 + 6.0 * (1 - np.exp(-1.3 * (x_curve - 0.5) / n))
    ax.fill_between(x_curve, 0, y_curve, color="#4A90E8", alpha=0.15, zorder=1)
    ax.fill_between(x_curve, 0, y_curve * 0.85, color="#1A73E8", alpha=0.10, zorder=2)
    ax.plot(x_curve, y_curve, color="#1A73E8", linewidth=2.0, alpha=0.6, zorder=3)

    # 标题
    _draw_mixed(ax, 0.3, 9.5, title, fontsize=18, color=BLUE)

    # 事件锚点
    for i, ev in enumerate(events):
        x = i + 1
        y = 1.5 + 6.0 * (1 - np.exp(-1.3 * (x - 0.5) / n))
        # 圆球
        ax.plot(x, y, "o", markersize=14, color="white", mec=BLUE, mew=2.5, zorder=5)
        ax.plot(x, y, "o", markersize=7, color=BLUE, zorder=6)
        # 连接虚线
        ax.plot([x, x], [0.3, y - 0.25], color=BLUE, linewidth=1.0,
                linestyle=":", alpha=0.5, zorder=4)
        # 年份（圆球上方）
        _draw_mixed(ax, x, y + 0.55, ev.get("year", ""), fontsize=14,
                    color=BLUE, ha="center")
        # 事件标题（年份下方）
        title_text = ev.get("title", "")
        # 自动换行：超过 8 个字符的加换行
        if len(title_text) > 8:
            # 找最接近中点的空格或断点
            mid = len(title_text) // 2
            title_text = title_text[:mid] + "\n" + title_text[mid:]
        # 使用多行：分两行画
        lines = title_text.split("\n")
        base_y = 0.95
        for j, line in enumerate(lines):
            _draw_mixed(ax, x, base_y - j * 0.32, line, fontsize=9.5,
                        color=DARK_TEXT, ha="center")
        # 副标签
        sub = ev.get("sub", "")
        if sub:
            _draw_mixed(ax, x, base_y - len(lines) * 0.32 - 0.05, sub, fontsize=8,
                        color=GRAY_TEXT, ha="center")

    plt.tight_layout()
    return _render_to_bytes(fig)


# ---------------------------------------------------------------------------
# V1.1 新增 · §8.2 知识产权布局条形图（年度分布）
# ---------------------------------------------------------------------------


def render_ipr_yearly_bars(ipr_by_year: dict[str, dict[str, int]],
                           *, title: str = "知识产权年度布局",
                           width: float = 12.0) -> bytes:
    """ipr_by_year: {"2023": {"专利": 30, "商标": 5, "软著": 3}, ...}"""
    if not ipr_by_year:
        return b""
    years = sorted(ipr_by_year.keys())
    categories = list({c for y in ipr_by_year.values() for c in y.keys()})
    if not categories:
        return b""

    import numpy as np
    fig, ax = plt.subplots(figsize=(width, 4.5))
    bar_w = 0.8 / len(categories)
    color_palette = ["#1A73E8", "#4DA3FF", "#7FB8FF", "#B0D4FF", "#D6E8FF"]

    for i, cat in enumerate(categories):
        values = [ipr_by_year[y].get(cat, 0) for y in years]
        x = np.arange(len(years)) + i * bar_w
        color = color_palette[i % len(color_palette)]
        ax.bar(x, values, bar_w, label=cat, color=color, edgecolor="white", linewidth=0.5)
        # 柱顶数值
        for xi, v in zip(x, values):
            if v > 0:
                ax.text(xi, v + max(values) * 0.02, str(v), ha="center",
                        fontsize=8, color=DARK_TEXT,
                        fontproperties=ASCII_FP)

    ax.set_xticks(np.arange(len(years)) + bar_w * (len(categories) - 1) / 2)
    ax.set_xticklabels(years, fontproperties=ASCII_FP, fontsize=10)
    ax.tick_params(axis="y", labelsize=9, colors=GRAY_TEXT)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(LINE_GRAY)

    # 图例（轴坐标系，CJK 字体）
    x0 = 0.02
    y0 = 0.95
    for i, cat in enumerate(categories):
        color = color_palette[i % len(color_palette)]
        ax.plot(x0 + i * 0.15, y0, "s", transform=ax.transAxes,
                markersize=10, color=color)
        ax.annotate(cat, xy=(x0 + i * 0.15 + 0.015, y0),
                    xycoords="axes fraction",
                    fontsize=9, color=DARK_TEXT,
                    fontproperties=CJK_FP,
                    va="center")

    # 标题
    _draw_mixed(ax, (len(years) - 1) * 0.5 + bar_w, max([max(ipr_by_year[y].values()) for y in years]) * 1.18,
                title, fontsize=13, color=BLUE, ha="center")
    ax.set_ylim(0, max([max(ipr_by_year[y].values()) for y in years]) * 1.3)

    plt.tight_layout()
    return _render_to_bytes(fig)


# ---------------------------------------------------------------------------
# V1.1 新增 · §8.4 荣誉/榜单数量卡片图
# ---------------------------------------------------------------------------


def render_stat_cards(stats: list[dict], *, title: str = "行业地位与荣誉",
                      width: float = 13.0) -> bytes:
    """PPT P8 风格的大数字 + 标签卡片
    stats: [{"number": "21", "unit": "项", "label": "企业荣誉"}, ...]
    """
    if not stats:
        return b""
    n = len(stats)
    fig, ax = plt.subplots(figsize=(width, 3.2))
    ax.set_xlim(0, n)
    ax.set_ylim(0, 3)
    ax.axis("off")
    fig.canvas.draw()

    _draw_mixed(ax, 0.1, 2.7, title, fontsize=13, color=BLUE)

    for i, s in enumerate(stats):
        cx = i + 0.5
        num = str(s.get("number", ""))
        unit = s.get("unit", "")
        label = s.get("label", "")

        # 把数字 + 单位当一个字符串画，避免位置错位
        combined = f"{num}{unit}" if unit else num
        # 用 _draw_mixed 居中
        _draw_mixed(ax, cx, 1.5, combined, fontsize=32, color=BLUE,
                    ha="center", va="center")
        _draw_mixed(ax, cx, 0.55, label, fontsize=11, color=DARK_TEXT, ha="center")

    plt.tight_layout()
    return _render_to_bytes(fig)


# ---------------------------------------------------------------------------
# V1.1 新增 · §8.3 员工规模年度趋势（从年报抽）
# ---------------------------------------------------------------------------


def render_staff_trend(yearly_staff: dict[str, int], *, title: str = "团队规模",
                       width: float = 10.0) -> bytes:
    """yearly_staff: {"2022": 551, "2023": 595, "2024": 461}"""
    if not yearly_staff:
        return b""
    years = sorted(yearly_staff.keys())
    values = [yearly_staff[y] for y in years]

    import numpy as np
    fig, ax = plt.subplots(figsize=(width, 4.2))
    x = np.arange(len(years))
    ax.plot(x, values, "-o", color=BLUE, linewidth=2.5, markersize=10,
            markerfacecolor="white", markeredgecolor=BLUE, markeredgewidth=2.5)
    ax.fill_between(x, 0, values, color=BLUE, alpha=0.15)

    for xi, y, v in zip(x, values, values):
        _draw_mixed(ax, xi, v + max(values) * 0.04, f"{v} 人",
                    fontsize=10, color=DARK_TEXT, ha="center")

    ax.set_xticks(x)
    ax.set_xticklabels(years, fontproperties=ASCII_FP, fontsize=10)
    ax.tick_params(axis="y", labelsize=9, colors=GRAY_TEXT)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(LINE_GRAY)
    ax.set_ylim(0, max(values) * 1.25)

    _draw_mixed(ax, (len(years) - 1) / 2, max(values) * 1.18, title,
                fontsize=13, color=BLUE, ha="center")

    plt.tight_layout()
    return _render_to_bytes(fig)


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    out_dir = "/tmp/v102_timeline"
    os.makedirs(out_dir, exist_ok=True)

    # capital
    capital = [
        {"历史注册资本": "36225万元", "起始日期": "2023-10-30", "终止日期": ""},
        {"历史注册资本": "36000万元", "起始日期": "2023-07-06", "终止日期": "2023-10-30"},
        {"历史注册资本": "50万元", "起始日期": "", "终止日期": "2014-09-11"},
    ]
    with open(f"{out_dir}/capital.png", "wb") as f:
        f.write(timeline_capital(capital))
    print(f"saved capital.png")

    # name
    name = [
        {"历史名称": "企查查科技股份有限公司", "起始日期": "2023-07-06", "终止日期": ""},
        {"历史名称": "企查查科技有限公司", "起始日期": "2020-08-25", "终止日期": "2023-07-06"},
    ]
    with open(f"{out_dir}/name.png", "wb") as f:
        f.write(timeline_name(name))
    print(f"saved name.png")

    # shareholder exits
    sh = [
        {"股东名称": "万得信息技术股份有限公司", "股东类型": "企业法人", "退出时持股比例": "16.81%",
         "退出日期": "2024-10-28", "认缴出资额": "6091.20万元"},
        {"股东名称": "马群", "股东类型": "自然人股东", "退出时持股比例": "36%",
         "退出日期": "2015-05-05", "认缴出资额": "18万元"},
    ]
    with open(f"{out_dir}/shareholder_exits.png", "wb") as f:
        f.write(timeline_shareholder_exits(sh))
    print(f"saved shareholder_exits.png")

    # V1.1 新增测试
    milestones = [
        {"year": "2014", "title": "企查查成立", "sub": "APP 上线"},
        {"year": "2017", "title": "信息安全等级保护三级", "sub": "北京分公司成立"},
        {"year": "2019", "title": "央行征信机构牌照", "sub": "获万得投资"},
        {"year": "2022", "title": "DCMM 贯标优秀认证", "sub": "获元禾投资"},
        {"year": "2023", "title": "工信部大数据示范", "sub": "股改上市准备"},
        {"year": "2024", "title": "注册用户超 1.5 亿", "sub": "中国互联网百强"},
    ]
    with open(f"{out_dir}/milestone_curve.png", "wb") as f:
        f.write(render_milestone_curve(milestones, title="企查查科技 · 发展里程碑"))
    print("saved milestone_curve.png")

    stats = [
        {"number": "21", "unit": "项", "label": "企业荣誉"},
        {"number": "60", "unit": "个", "label": "上榜榜单"},
        {"number": "94", "unit": "项", "label": "专利信息"},
        {"number": "30", "unit": "类", "label": "资质证书"},
    ]
    with open(f"{out_dir}/stat_cards.png", "wb") as f:
        f.write(render_stat_cards(stats, title="企查查科技 · 行业地位与荣誉"))
    print("saved stat_cards.png")

    staff = {"2022": 551, "2023": 595, "2024": 461}
    with open(f"{out_dir}/staff_trend.png", "wb") as f:
        f.write(render_staff_trend(staff, title="员工规模年度趋势（社保参保人数）"))
    print("saved staff_trend.png")

    print(f"\nAll files in {out_dir}")
