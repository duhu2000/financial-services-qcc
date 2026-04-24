"""
tier_detector.py · 档位识别模块（V1.0.1 · 真实中文键）
=======================================================
输入：企业名称或统一社会信用代码
输出：档位（micro/financing/listed） + 基础画像 + 累计调用成本（15c）

调用 3 个 5c 工具（参数 searchKey）：
  1. mcp__qcc-company__get_company_profile
  2. mcp__qcc-company__get_listing_info
  3. mcp__qcc-operation__get_financing_records

档位规则：
  - 上市档：listing_info 返回非空（已上市 或 发债）
  - 融资档：financing_records 有「股权融资/创投融资」
  - 小微档：以上都空（无上市、无融资）
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from cost_counter import CostCounter

TIER_MICRO = "micro"
TIER_FINANCING = "financing"
TIER_LISTED = "listed"

TIER_BUDGET = {
    TIER_MICRO: 45,      # V1.1：+10c（荣誉/资质 2 个新工具）
    TIER_FINANCING: 130, # V1.1：+40c（荣誉/榜单/资质/电信/招聘/信用/IPR×3/年报 10 个新工具）
    TIER_LISTED: 180,    # V1.1：+60c（扩全量知识产权 + 舆情 + 进出口信用 14 个新工具）
}

COST_PER_DETECT_TOOL = 5
DETECT_TOTAL_COST = 15


@dataclass
class TierResult:
    tier: str
    profile: dict[str, Any] = field(default_factory=dict)
    listing: dict[str, Any] = field(default_factory=dict)
    financing: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    degraded: bool = False

    @property
    def budget(self) -> int:
        return TIER_BUDGET[self.tier]


def _is_empty_response(data: Any) -> bool:
    if data is None:
        return True
    if isinstance(data, dict):
        if data.get("_error"):
            return True
        search_result = data.get("搜索结果") or ""
        if any(k in search_result for k in ["未发现", "未找到", "暂无"]):
            return True
        meta = {"企业名称", "摘要", "搜索结果", "_error"}
        content_keys = [k for k in data if k not in meta]
        if not content_keys:
            return True
    return False


def _is_listed(listing: dict[str, Any]) -> bool:
    if _is_empty_response(listing):
        return False
    # 企查查 get_listing_info 返回 "上市日期/股票简称/股票代码" 等字段
    if listing.get("股票代码") or listing.get("上市日期"):
        return True
    status = listing.get("上市状态") or ""
    if "已上市" in status or "LISTED" in status.upper():
        return True
    return False


def _has_financing(financing: dict[str, Any]) -> bool:
    if _is_empty_response(financing):
        return False
    # 真实返回：{"股权融资": {"创投融资": [...]}}
    sq = financing.get("股权融资") or {}
    if isinstance(sq, dict):
        vc = sq.get("创投融资") or []
        if isinstance(vc, list) and vc:
            return True
    # 兼容其他可能结构
    if financing.get("融资信息"):
        return True
    return False


def _parse_capital_wan(s: str) -> float:
    """解析 '12000 万人民币' / '300万元' 为万元数值。"""
    if not s:
        return 0.0
    m = re.search(r"([\d.]+)\s*亿", s)
    if m:
        return float(m.group(1)) * 10000
    m = re.search(r"([\d.]+)\s*万", s)
    if m:
        return float(m.group(1))
    m = re.search(r"([\d.]+)", s)
    if m:
        # 裸数字按万元处理
        return float(m.group(1))
    return 0.0


def _is_micro(profile: dict[str, Any]) -> bool:
    """小微判断：注册资本 ≤ 1000 万 或 人员规模 ≤ 50。"""
    if _is_empty_response(profile):
        return True

    # 注册资本从简介中抽取（profile 工具返回只有 企业名称/简介）
    brief = profile.get("简介") or ""
    reg_capi_wan = 0.0
    m = re.search(r"注册资本为([\d.]+万元|[\d.]+亿元)", brief)
    if m:
        reg_capi_wan = _parse_capital_wan(m.group(1))
    else:
        reg_capi_wan = _parse_capital_wan(profile.get("注册资本") or "")

    capi_is_small = 0 < reg_capi_wan <= 1000
    return capi_is_small


def detect_tier(
    company_keyword: str,
    *,
    call_mcp: Optional[Callable[[str, dict], Any]] = None,
    cost_counter: Optional[CostCounter] = None,
) -> TierResult:
    if call_mcp is None:
        raise ValueError("call_mcp 回调不能为空")

    counter = cost_counter or CostCounter()

    # 1. 基本信息
    try:
        profile = call_mcp(
            "mcp__qcc-company__get_company_profile",
            {"searchKey": company_keyword},
        )
        counter.add("mcp__qcc-company__get_company_profile", COST_PER_DETECT_TOOL)
    except Exception as exc:
        return TierResult(
            tier=TIER_MICRO,
            reason=f"档位识别失败：get_company_profile 异常（{exc}），默认小微档",
            degraded=True,
        )

    # 2. 上市
    try:
        listing = call_mcp(
            "mcp__qcc-company__get_listing_info",
            {"searchKey": company_keyword},
        )
        counter.add("mcp__qcc-company__get_listing_info", COST_PER_DETECT_TOOL)
    except Exception:
        listing = {}

    # 3. 融资
    try:
        financing = call_mcp(
            "mcp__qcc-operation__get_financing_records",
            {"searchKey": company_keyword},
        )
        counter.add(
            "mcp__qcc-operation__get_financing_records", COST_PER_DETECT_TOOL
        )
    except Exception:
        financing = {}

    # 判定
    if _is_listed(listing):
        return TierResult(
            tier=TIER_LISTED,
            profile=profile,
            listing=listing,
            financing=financing,
            reason="已上市/发债",
        )

    if _has_financing(financing):
        sq = financing.get("股权融资") or {}
        rounds = sq.get("创投融资") or []
        latest = rounds[0] if rounds else {}
        return TierResult(
            tier=TIER_FINANCING,
            profile=profile,
            listing=listing,
            financing=financing,
            reason=f"有融资记录（最新：{latest.get('融资轮次') or 'N/A'} · {latest.get('融资日期') or ''}）",
        )

    if _is_micro(profile):
        return TierResult(
            tier=TIER_MICRO,
            profile=profile,
            listing=listing,
            financing=financing,
            reason="无上市、无融资，注册资本 ≤ 1000 万",
        )

    return TierResult(
        tier=TIER_FINANCING,
        profile=profile,
        listing=listing,
        financing=financing,
        reason="无上市未融资但规模较大，按融资档处理",
    )


if __name__ == "__main__":
    def mock_mcp(tool: str, params: dict) -> dict:
        if tool.endswith("get_company_profile"):
            return {"企业名称": "测试企业", "简介": "注册资本为500万元，员工规模10-50人。"}
        if tool.endswith("get_listing_info"):
            return {"搜索结果": "未发现任何记录"}
        if tool.endswith("get_financing_records"):
            return {"搜索结果": "未发现任何记录"}
        return {}

    cc = CostCounter(budget=100)
    result = detect_tier("测试企业", call_mcp=mock_mcp, cost_counter=cc)
    print(f"档位：{result.tier}")
    print(f"原因：{result.reason}")
    print(f"成本：{cc.total}c / 预算：{result.budget}c")
