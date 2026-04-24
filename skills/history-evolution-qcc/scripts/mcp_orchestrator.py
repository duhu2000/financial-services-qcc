"""
mcp_orchestrator.py · MCP 批量调用编排（V1.0.1）
================================================
按档位拉取企业画像。所有 MCP 调用的实际执行由外部 `call_mcp(tool, params)` 回调完成。

V1.0.1 差异：
  - 全部返回字段按中文键解析
  - 空返回 `{"搜索结果":"..."}` 形态兼容
  - 按档位裁剪关键人展开（C2/C1/不展开）
  - qcc-executive 工具使用 searchKey + personName 双参数
  - qcc-history 工具集全量接入
  - searchKey 统一使用原始企业名称
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from cost_counter import BudgetExceeded, CostCounter
from tier_detector import (
    TIER_FINANCING,
    TIER_LISTED,
    TIER_MICRO,
    detect_tier,
)


# ---------------------------------------------------------------------------
# 工具成本表（与企查查 MCP 计价一致）
# ---------------------------------------------------------------------------

MCP_TOOL_COST = {
    # qcc-company
    "mcp__qcc-company__get_company_profile": 5,
    "mcp__qcc-company__get_company_registration_info": 5,
    "mcp__qcc-company__get_shareholder_info": 5,
    "mcp__qcc-company__get_key_personnel": 5,
    "mcp__qcc-company__get_change_records": 5,
    "mcp__qcc-company__get_branches": 5,
    "mcp__qcc-company__get_external_investments": 5,
    "mcp__qcc-company__get_actual_controller": 5,
    "mcp__qcc-company__get_beneficial_owners": 5,
    "mcp__qcc-company__get_listing_info": 5,
    "mcp__qcc-company__get_contact_info": 5,
    "mcp__qcc-company__get_tax_invoice_info": 5,
    "mcp__qcc-company__get_financial_data": 3,
    "mcp__qcc-company__get_annual_reports": 5,
    # qcc-operation
    "mcp__qcc-operation__get_financing_records": 5,
    "mcp__qcc-operation__get_administrative_license": 5,
    "mcp__qcc-operation__get_qualifications": 5,
    "mcp__qcc-operation__get_honor_info": 5,
    "mcp__qcc-operation__get_telecom_license": 5,
    "mcp__qcc-operation__get_company_announcement": 5,
    "mcp__qcc-operation__get_ranking_list_info": 5,
    "mcp__qcc-operation__get_bidding_info": 5,
    "mcp__qcc-operation__get_recruitment_info": 5,
    "mcp__qcc-operation__get_news_sentiment": 5,
    "mcp__qcc-operation__get_credit_evaluation": 5,
    "mcp__qcc-operation__get_import_export_credit": 5,
    # qcc-ipr
    "mcp__qcc-ipr__get_patent_info": 5,
    "mcp__qcc-ipr__get_trademark_info": 5,
    "mcp__qcc-ipr__get_software_copyright_info": 5,
    "mcp__qcc-ipr__get_copyright_work_info": 5,
    "mcp__qcc-ipr__get_internet_service_info": 5,
    # qcc-risk
    "mcp__qcc-risk__get_business_exception": 5,
    "mcp__qcc-risk__get_tax_abnormal": 5,
    "mcp__qcc-risk__get_administrative_penalty": 5,
    "mcp__qcc-risk__get_dishonest_info": 5,
    "mcp__qcc-risk__get_equity_freeze": 5,
    "mcp__qcc-risk__get_equity_pledge_info": 5,
    "mcp__qcc-risk__get_chattel_mortgage_info": 5,
    "mcp__qcc-risk__get_guarantee_info": 5,
    # qcc-history
    "mcp__qcc-history__get_historical_shareholders": 20,
    "mcp__qcc-history__get_historical_registration": 5,
    "mcp__qcc-history__get_historical_legal_rep": 5,
    "mcp__qcc-history__get_historical_executives": 5,
    "mcp__qcc-history__get_historical_admin_license": 5,
    "mcp__qcc-history__get_historical_investments": 5,
    "mcp__qcc-history__get_historical_listing": 5,
    # qcc-executive
    "mcp__qcc-executive__get_personnel_positions": 5,
    "mcp__qcc-executive__get_personnel_controlled_companies": 5,
    "mcp__qcc-executive__get_personnel_beneficial_owner": 5,
    "mcp__qcc-executive__get_personnel_investments": 5,
    "mcp__qcc-executive__get_personnel_legal_rep_roles": 5,
    "mcp__qcc-executive__get_personnel_related_companies": 5,
}


# ---------------------------------------------------------------------------
# 档位工具清单
# ---------------------------------------------------------------------------

# 通用：所有档位都调（公司维度）
TIER_TOOL_PLAN: dict[str, list[str]] = {
    TIER_MICRO: [
        # 基础工商
        "mcp__qcc-company__get_company_registration_info",
        "mcp__qcc-company__get_change_records",
        "mcp__qcc-company__get_shareholder_info",
        "mcp__qcc-company__get_key_personnel",
        # 风险（触发式，有记录才输出）
        "mcp__qcc-risk__get_business_exception",
        "mcp__qcc-risk__get_tax_abnormal",
        # 历史信息（小微也拉，便于 §附录）
        "mcp__qcc-history__get_historical_registration",
        "mcp__qcc-history__get_historical_legal_rep",
        # V1.1 §8 发展综览（小微轻量）
        "mcp__qcc-operation__get_honor_info",
        "mcp__qcc-operation__get_qualifications",
    ],
    TIER_FINANCING: [
        "mcp__qcc-company__get_company_registration_info",
        "mcp__qcc-company__get_change_records",
        "mcp__qcc-company__get_shareholder_info",
        "mcp__qcc-company__get_key_personnel",
        "mcp__qcc-company__get_branches",
        "mcp__qcc-company__get_external_investments",
        "mcp__qcc-company__get_actual_controller",
        "mcp__qcc-company__get_beneficial_owners",
        # 历史信息（含 20c 股东历史）
        "mcp__qcc-history__get_historical_shareholders",
        "mcp__qcc-history__get_historical_registration",
        "mcp__qcc-history__get_historical_legal_rep",
        "mcp__qcc-history__get_historical_executives",
        "mcp__qcc-history__get_historical_investments",
        # 风险
        "mcp__qcc-risk__get_administrative_penalty",
        "mcp__qcc-risk__get_equity_pledge_info",
        "mcp__qcc-risk__get_equity_freeze",
        # V1.1 §8 发展综览（融资档全量）
        "mcp__qcc-operation__get_honor_info",
        "mcp__qcc-operation__get_ranking_list_info",
        "mcp__qcc-operation__get_qualifications",
        "mcp__qcc-operation__get_telecom_license",
        "mcp__qcc-operation__get_recruitment_info",
        "mcp__qcc-operation__get_credit_evaluation",
        "mcp__qcc-ipr__get_patent_info",
        "mcp__qcc-ipr__get_trademark_info",
        "mcp__qcc-ipr__get_software_copyright_info",
        "mcp__qcc-company__get_annual_reports",
    ],
    TIER_LISTED: [
        "mcp__qcc-company__get_company_registration_info",
        "mcp__qcc-company__get_change_records",
        "mcp__qcc-company__get_shareholder_info",
        "mcp__qcc-company__get_key_personnel",
        "mcp__qcc-company__get_branches",
        "mcp__qcc-company__get_external_investments",
        "mcp__qcc-company__get_actual_controller",
        "mcp__qcc-company__get_beneficial_owners",
        "mcp__qcc-company__get_financial_data",
        # 历史
        "mcp__qcc-history__get_historical_shareholders",
        "mcp__qcc-history__get_historical_registration",
        "mcp__qcc-history__get_historical_legal_rep",
        "mcp__qcc-history__get_historical_executives",
        "mcp__qcc-history__get_historical_investments",
        "mcp__qcc-history__get_historical_listing",
        "mcp__qcc-history__get_historical_admin_license",
        # 运营
        "mcp__qcc-operation__get_administrative_license",
        "mcp__qcc-operation__get_company_announcement",
        # 风险
        "mcp__qcc-risk__get_administrative_penalty",
        "mcp__qcc-risk__get_equity_pledge_info",
        "mcp__qcc-risk__get_equity_freeze",
        "mcp__qcc-risk__get_dishonest_info",
        # V1.1 §8 发展综览（上市档完整）
        "mcp__qcc-operation__get_honor_info",
        "mcp__qcc-operation__get_ranking_list_info",
        "mcp__qcc-operation__get_qualifications",
        "mcp__qcc-operation__get_telecom_license",
        "mcp__qcc-operation__get_recruitment_info",
        "mcp__qcc-operation__get_credit_evaluation",
        "mcp__qcc-operation__get_news_sentiment",
        "mcp__qcc-operation__get_import_export_credit",
        "mcp__qcc-ipr__get_patent_info",
        "mcp__qcc-ipr__get_trademark_info",
        "mcp__qcc-ipr__get_software_copyright_info",
        "mcp__qcc-ipr__get_copyright_work_info",
        "mcp__qcc-ipr__get_internet_service_info",
        "mcp__qcc-company__get_annual_reports",
        "mcp__qcc-risk__get_guarantee_info",
    ],
}


# 关键人展开配置（C 档位决策）
EXECUTIVE_EXPANSION_PLAN: dict[str, dict] = {
    TIER_MICRO: {"max_persons": 0, "tools": []},  # 不展开
    TIER_FINANCING: {
        "max_persons": 1,
        "tools": [
            "mcp__qcc-executive__get_personnel_positions",
            "mcp__qcc-executive__get_personnel_controlled_companies",
            "mcp__qcc-executive__get_personnel_investments",
        ],
    },
    TIER_LISTED: {
        "max_persons": 3,
        "tools": [
            "mcp__qcc-executive__get_personnel_positions",
            "mcp__qcc-executive__get_personnel_controlled_companies",
            "mcp__qcc-executive__get_personnel_investments",
        ],
    },
}


# ---------------------------------------------------------------------------
# 数据容器
# ---------------------------------------------------------------------------


@dataclass
class CompanySnapshot:
    keyword: str
    tier: str
    tier_reason: str = ""
    profile: dict[str, Any] = field(default_factory=dict)
    listing: dict[str, Any] = field(default_factory=dict)
    financing: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    cost_summary: dict[str, Any] = field(default_factory=dict)
    uncollected: list[str] = field(default_factory=list)

    def get(self, tool_name: str) -> Any:
        return self.raw.get(tool_name)


# ---------------------------------------------------------------------------
# 空返回判断（与 build_docx 共享）
# ---------------------------------------------------------------------------


def _is_empty(data: Any) -> bool:
    if data is None:
        return True
    if isinstance(data, (list, str, tuple)) and not data:
        return True
    if isinstance(data, dict):
        if data.get("_error"):
            return True
        search_result = data.get("搜索结果") or ""
        if any(k in search_result for k in ["未发现", "未找到", "暂无"]):
            return True
        meta = {"企业名称", "摘要", "搜索结果", "_error", "人员名称"}
        content_keys = [k for k in data if k not in meta]
        if not content_keys:
            return True
    return False


# ---------------------------------------------------------------------------
# 关键人挑选（按档位 max_persons）
# ---------------------------------------------------------------------------


def _select_key_persons(snapshot: CompanySnapshot, max_n: int) -> list[str]:
    """按"实控人 > 董事长/法人 > 董事/经理"优先级，取前 N 位唯一姓名。"""
    if max_n <= 0:
        return []

    names: list[str] = []

    # 优先级 1：实控人
    ac_data = snapshot.raw.get("mcp__qcc-company__get_actual_controller") or {}
    for a in ac_data.get("实际控制人信息") or []:
        n = a.get("实际控制人名称") or a.get("姓名")
        if n and n not in names:
            names.append(n)

    # 优先级 2：董监高（按职务优先级）
    kp_data = snapshot.raw.get("mcp__qcc-company__get_key_personnel") or {}
    employees = kp_data.get("主要人员信息") or []
    priority_titles = ["董事长", "总经理", "法定代表人", "执行董事", "经理"]

    def _priority_key(e: dict) -> int:
        title = e.get("职务") or ""
        for i, kw in enumerate(priority_titles):
            if kw in title:
                return i
        return len(priority_titles)

    sorted_emps = sorted(employees, key=_priority_key)
    for e in sorted_emps:
        n = e.get("姓名")
        if n and n not in names:
            names.append(n)

    return names[:max_n]


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def build_snapshot(
    company_keyword: str,
    *,
    call_mcp: Callable[[str, dict], Any],
    cost_counter: Optional[CostCounter] = None,
) -> CompanySnapshot:
    """从档位识别到批量拉取 → CompanySnapshot
    V1.1：初始 counter 用 180c（上市档封顶），档位识别后若为小微/融资档则压降 budget
    """
    from tier_detector import TIER_BUDGET
    counter = cost_counter or CostCounter(budget=180)

    # 1. 档位识别（15c）
    tier_result = detect_tier(
        company_keyword,
        call_mcp=call_mcp,
        cost_counter=counter,
    )

    snapshot = CompanySnapshot(
        keyword=company_keyword,
        tier=tier_result.tier,
        tier_reason=tier_result.reason,
        profile=tier_result.profile,
        listing=tier_result.listing,
        financing=tier_result.financing,
    )
    # V1.1：档位识别后压降 budget 到档位对应值
    tier_budget = TIER_BUDGET.get(tier_result.tier, 180)
    if counter.budget > tier_budget:
        counter.budget = tier_budget
        counter.soft_limit = max(counter.total, tier_budget - 10)

    snapshot.raw["mcp__qcc-company__get_company_profile"] = tier_result.profile
    snapshot.raw["mcp__qcc-company__get_listing_info"] = tier_result.listing
    snapshot.raw["mcp__qcc-operation__get_financing_records"] = tier_result.financing

    # 2. 公司维度工具批量调用
    tool_plan = TIER_TOOL_PLAN[tier_result.tier]
    for tool in tool_plan:
        cost = MCP_TOOL_COST.get(tool, 5)
        if not counter.can_call(cost):
            snapshot.uncollected.append(tool)
            continue
        try:
            res = call_mcp(tool, {"searchKey": company_keyword})
            counter.add(tool, cost)
            snapshot.raw[tool] = res
        except BudgetExceeded:
            snapshot.uncollected.append(tool)
        except Exception as exc:
            snapshot.raw[tool] = {"_error": str(exc)}

    # 3. 关键人展开（qcc-executive，双参数）
    exec_plan = EXECUTIVE_EXPANSION_PLAN[tier_result.tier]
    max_n = exec_plan["max_persons"]
    exec_tools = exec_plan["tools"]
    key_persons = _select_key_persons(snapshot, max_n) if max_n > 0 else []

    for tool in exec_tools:
        cost = MCP_TOOL_COST.get(tool, 5)
        aggregated: list[dict] = []
        for person in key_persons:
            if not counter.can_call(cost):
                snapshot.uncollected.append(f"{tool}[{person}]")
                break
            try:
                res = call_mcp(
                    tool,
                    {"searchKey": company_keyword, "personName": person},
                )
                counter.add(f"{tool}[{person}]", cost)
                aggregated.append({"person": person, "result": res})
            except BudgetExceeded:
                snapshot.uncollected.append(f"{tool}[{person}]")
                break
            except Exception as exc:
                aggregated.append({"person": person, "error": str(exc)})
        if aggregated:
            snapshot.raw[tool] = aggregated

    snapshot.cost_summary = counter.summary()
    return snapshot


# ---------------------------------------------------------------------------
# 条件子节渲染判断
# ---------------------------------------------------------------------------


def should_render_section(section_key: str, snap: CompanySnapshot) -> bool:
    r = snap.raw

    if section_key == "4.4":
        ac = r.get("mcp__qcc-company__get_actual_controller")
        return not _is_empty(ac)

    if section_key == "4.6":
        if snap.tier not in {TIER_LISTED, TIER_FINANCING}:
            return False
        hs = r.get("mcp__qcc-history__get_historical_shareholders")
        return not _is_empty(hs)

    if section_key == "5.4":
        if snap.tier == TIER_MICRO:
            return False
        kp = r.get("mcp__qcc-company__get_key_personnel")
        return not _is_empty(kp)

    if section_key == "5.5":
        if snap.tier == TIER_MICRO:
            return False
        for tool in EXECUTIVE_EXPANSION_PLAN[snap.tier]["tools"]:
            bucket = r.get(tool)
            if isinstance(bucket, list):
                for entry in bucket:
                    if not _is_empty(entry.get("result")):
                        return True
        return False

    if section_key == "5.6":
        for tool in [
            "mcp__qcc-risk__get_administrative_penalty",
            "mcp__qcc-risk__get_guarantee_info",
            "mcp__qcc-risk__get_equity_pledge_info",
            "mcp__qcc-risk__get_equity_freeze",
            "mcp__qcc-risk__get_dishonest_info",
        ]:
            if not _is_empty(r.get(tool)):
                return True
        return False

    if section_key == "7.fin":
        if snap.tier != TIER_LISTED:
            return False
        fi = r.get("mcp__qcc-company__get_financial_data")
        return not _is_empty(fi)

    return True


if __name__ == "__main__":
    # smoke test with mock
    def mock_mcp(tool: str, params: dict) -> dict:
        if tool.endswith("get_company_profile"):
            return {"企业名称": "测试企业", "简介": "test"}
        if tool.endswith("get_listing_info"):
            return {"搜索结果": "未发现任何记录"}
        if tool.endswith("get_financing_records"):
            return {"搜索结果": "未发现任何记录"}
        if tool.endswith("get_key_personnel"):
            return {"主要人员信息": [{"姓名": "张三", "职务": "董事长"}]}
        if tool.endswith("get_actual_controller"):
            return {"实际控制人信息": [{"实际控制人名称": "张三", "直接持股比例": "50%"}]}
        return {"搜索结果": "未发现任何记录"}

    cc = CostCounter(budget=100)
    snap = build_snapshot("测试企业", call_mcp=mock_mcp, cost_counter=cc)
    print(f"档位：{snap.tier}")
    print(f"成本：{snap.cost_summary['total_cent']}c")
    print(f"未采集：{snap.uncollected}")
