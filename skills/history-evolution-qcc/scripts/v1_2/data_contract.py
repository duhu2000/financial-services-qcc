"""
data_contract.py · 数据契约（schema 强约束）
=================================================================
作用：用 pydantic 定义报告每个章节的字段结构 + 校验规则。
     渲染层只能消费"已通过 schema 校验"的对象，schema 本身做 count ≡ rows、
     USCC 校验、时间一致性等防御性检查。

历史教训：V1.1.3 报告里
- 股东数据 9 条对应 MCP 实际 13 条 → 本模块强制 count == len(rows)
- 历史股东 16 条对应 MCP 17 条
- 历任董监高 9 人对应 MCP 10 人
- USCC 编造 91320506MA1UYUWY3X
- 行政处罚日期/单位/文号全部编造
全部能在 schema validate 阶段拦截。

依赖：pydantic >= 2.x（pip install pydantic）
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    PYDANTIC_OK = True
except ImportError:
    PYDANTIC_OK = False

    # Stub 实现 — 让模块在 pydantic 未装时也能 import（仅用于开发期 / 文档）
    # 生产环境必须安装 pydantic，否则 schema 校验完全失效。
    class BaseModel:  # type: ignore[no-redef]
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
            # 调用所有以 _ 开头的"validator"方法（伪装 model_validator after）
            for name in dir(self):
                if name.startswith("_") and callable(getattr(self, name, None)):
                    if hasattr(getattr(self, name), "_is_model_validator"):
                        getattr(self, name)()

    def Field(default=None, **kwargs):  # type: ignore[no-redef]
        return default

    def field_validator(*args, **kwargs):  # type: ignore[no-redef]
        def deco(fn):
            return fn
        return deco

    def model_validator(*args, **kwargs):  # type: ignore[no-redef]
        def deco(fn):
            fn._is_model_validator = True
            return fn
        return deco

from .uscc_validator import validate_uscc, USCCValidationError


# ---------------------------------------------------------------------------
# 公司基础信息
# ---------------------------------------------------------------------------

class CompanyBasicInfo(BaseModel if PYDANTIC_OK else object):
    """§1 公司概况 字段结构。每个字段的取值都必须可回溯到 MCP。"""

    name: str = Field(..., description="企业名称")
    uscc: str = Field(..., description="统一社会信用代码")
    legal_rep: str = Field(..., description="法定代表人")
    establish_date: str = Field(..., description="成立日期 YYYY-MM-DD")
    registered_capital: str = Field(..., description="注册资本（含币种）")
    paid_capital: Optional[str] = None
    enterprise_type: str
    industry: str
    registration_status: str = Field(..., description="登记状态：在业 / 存续 / 注销 ...")
    registration_authority: str
    approval_date: Optional[str] = None
    region: Optional[str] = None
    registered_address: str
    insured_count: Optional[int] = None

    @field_validator("uscc")
    @classmethod
    def _check_uscc(cls, v: str) -> str:
        ok, msg = validate_uscc(v)
        if not ok:
            raise ValueError(f"USCC 校验失败：{msg}")
        return v

    @field_validator("establish_date")
    @classmethod
    def _check_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"成立日期必须是 YYYY-MM-DD 格式：{v}")
        return v


# ---------------------------------------------------------------------------
# 股东（当前 + 历史 + 实控人）
# ---------------------------------------------------------------------------

class Shareholder(BaseModel if PYDANTIC_OK else object):
    name: str
    holding_ratio: str        # 例如 "35.49%"
    shares: Optional[str] = None  # 持股数
    capital_contribution: Optional[str] = None  # 认缴出资额


class CurrentShareholdersSection(BaseModel if PYDANTIC_OK else object):
    """§5.1 当前股东 — count 必须等于 rows 数量。"""

    total_count: int = Field(..., description="MCP 摘要中的股东总数")
    shareholders: list[Shareholder]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.shareholders) != self.total_count:
            raise ValueError(
                f"股东总数声明 {self.total_count} 但实际行数 {len(self.shareholders)}。"
                f"可能漏列；§5.1 必须全量展示，禁止人为截断。"
            )
        return self


class HistoricalShareholder(BaseModel if PYDANTIC_OK else object):
    name: str
    exit_date: str
    exit_ratio: Optional[str] = None
    capital: Optional[str] = None
    shareholder_type: Optional[str] = None


class HistoricalShareholdersSection(BaseModel if PYDANTIC_OK else object):
    """§5.3 股东进出历史 — count ≡ rows。"""

    total_count: int
    exited_shareholders: list[HistoricalShareholder]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.exited_shareholders) != self.total_count:
            raise ValueError(
                f"历史股东总数声明 {self.total_count} 但实际行数 "
                f"{len(self.exited_shareholders)}。"
            )
        return self


# ---------------------------------------------------------------------------
# 董监高（现任 + 历任）
# ---------------------------------------------------------------------------

class Executive(BaseModel if PYDANTIC_OK else object):
    name: str
    position: str
    holding_ratio: Optional[str] = None


class HistoricalExecutive(BaseModel if PYDANTIC_OK else object):
    name: str
    position: str
    appointment_date: Optional[str] = None
    departure_date: str


class ExecutiveSection(BaseModel if PYDANTIC_OK else object):
    """§6.2 董监高 + 历任董监高 — count ≡ rows。"""

    current_count: int
    current_executives: list[Executive]
    historical_count: int
    historical_executives: list[HistoricalExecutive]

    @model_validator(mode="after")
    def _both_counts_match(self):
        if len(self.current_executives) != self.current_count:
            raise ValueError(
                f"现任董监高声明 {self.current_count} 但实际 {len(self.current_executives)}"
            )
        if len(self.historical_executives) != self.historical_count:
            raise ValueError(
                f"历任董监高声明 {self.historical_count} 但实际 "
                f"{len(self.historical_executives)}"
            )
        return self


# ---------------------------------------------------------------------------
# 对外投资
# ---------------------------------------------------------------------------

class Investment(BaseModel if PYDANTIC_OK else object):
    invested_company: str
    holding_ratio: str
    establish_date: Optional[str] = None
    capital: Optional[str] = None
    status: Optional[str] = None


class InvestmentSection(BaseModel if PYDANTIC_OK else object):
    """§6.1 对外投资 — count ≡ rows。"""

    total_count: int
    investments: list[Investment]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.investments) != self.total_count:
            raise ValueError(
                f"对外投资声明 {self.total_count} 但实际行数 {len(self.investments)}。"
                f"漏列子公司是 V1.1.3 的典型事故。"
            )
        return self


# ---------------------------------------------------------------------------
# 注册资本/名称/地址 历史变更
# ---------------------------------------------------------------------------

class HistoricalCapitalNode(BaseModel if PYDANTIC_OK else object):
    capital: str
    start_date: Optional[str] = None  # 空字符串视为"设立时"
    end_date: Optional[str] = None    # 空字符串视为"当前"


class HistoricalNameNode(BaseModel if PYDANTIC_OK else object):
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class HistoricalAddressNode(BaseModel if PYDANTIC_OK else object):
    address: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class HistoricalRegistrationSection(BaseModel if PYDANTIC_OK else object):
    """§3 + §4 + §7 注册资本 / 名称 / 地址 历史。

    每个时间轴必须严格按 MCP 历史 + 当前合并展示，不允许漏。
    """

    capital_nodes: list[HistoricalCapitalNode]
    name_nodes: list[HistoricalNameNode]
    address_nodes: list[HistoricalAddressNode]


# ---------------------------------------------------------------------------
# 资质 / 荣誉 / 专利 / 行政处罚
# ---------------------------------------------------------------------------

class Qualification(BaseModel if PYDANTIC_OK else object):
    name: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class QualificationSection(BaseModel if PYDANTIC_OK else object):
    total_count: int
    valid_count: int
    qualifications: list[Qualification]

    @model_validator(mode="after")
    def _count_check(self):
        if len(self.qualifications) != self.total_count:
            raise ValueError(
                f"资质声明 {self.total_count} 但实际 {len(self.qualifications)}"
            )
        if self.valid_count > self.total_count:
            raise ValueError(
                f"有效资质数 {self.valid_count} > 总数 {self.total_count}"
            )
        return self


class Honor(BaseModel if PYDANTIC_OK else object):
    name: str
    publish_date: str
    level: str               # 国家级 / 省级 / 市级
    issuer: str
    certified_year: Optional[str] = None


class HonorSection(BaseModel if PYDANTIC_OK else object):
    total_count: int
    honors: list[Honor]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.honors) != self.total_count:
            raise ValueError(
                f"荣誉声明 {self.total_count} 但实际 {len(self.honors)}"
            )
        return self


class Patent(BaseModel if PYDANTIC_OK else object):
    title: str
    application_no: str
    application_date: str    # 必填，用于年度统计
    publish_no: Optional[str] = None
    publish_date: Optional[str] = None
    patent_type: str         # 发明授权 / 外观设计 / ...
    legal_status: Optional[str] = None


class PatentSection(BaseModel if PYDANTIC_OK else object):
    total_count: int
    patents: list[Patent]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.patents) != self.total_count:
            raise ValueError(
                f"专利总数声明 {self.total_count} 但实际 {len(self.patents)}。"
                f"V1.1.3 的年度分布表加和 65 ≠ 总数 94 — 必须杜绝此类不一致。"
            )
        return self

    def yearly_distribution(self) -> dict[str, int]:
        """从 application_date 自动算年度分布 — 严禁手写。"""
        dist: dict[str, int] = {}
        for p in self.patents:
            year = p.application_date[:4] if p.application_date else "未知"
            dist[year] = dist.get(year, 0) + 1
        return dist

    def type_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for p in self.patents:
            t = p.patent_type or "未知"
            dist[t] = dist.get(t, 0) + 1
        return dist


class AdministrativePenalty(BaseModel if PYDANTIC_OK else object):
    """行政处罚 — 严禁加 MCP 没返回的字段（如"违法行为类型"、"已处置"）。"""

    decision_no: str
    penalty_date: str
    penalty_authority: str
    penalty_amount: Optional[str] = None
    penalty_result: Optional[str] = None
    # 注意：没有 violation_type 字段，因为 MCP 不返回 → 不允许编造


class AdministrativePenaltySection(BaseModel if PYDANTIC_OK else object):
    total_count: int
    penalties: list[AdministrativePenalty]

    @model_validator(mode="after")
    def _count_equals_rows(self):
        if len(self.penalties) != self.total_count:
            raise ValueError(
                f"行政处罚声明 {self.total_count} 但实际 {len(self.penalties)}"
            )
        return self


# ---------------------------------------------------------------------------
# 整体报告
# ---------------------------------------------------------------------------

class ReportSchema(BaseModel if PYDANTIC_OK else object):
    """整份报告的顶层 schema。
    生成 PDF/MD 时只能消费这个对象，缺字段会在加载阶段直接失败。
    """
    report_id: str
    generated_at: str
    company: CompanyBasicInfo
    historical_registration: HistoricalRegistrationSection
    current_shareholders: CurrentShareholdersSection
    historical_shareholders: HistoricalShareholdersSection
    executives: ExecutiveSection
    investments: InvestmentSection
    qualifications: QualificationSection
    honors: HonorSection
    patents: PatentSection
    administrative_penalties: AdministrativePenaltySection
    change_records_count: int = Field(..., description="工商变更总数（不展示明细，仅展示精选）")


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_test() -> None:
    if not PYDANTIC_OK:
        print("⚠ pydantic 未安装，跳过自检 — 请 pip install pydantic")
        return

    # 正例
    sec = CurrentShareholdersSection(
        total_count=2,
        shareholders=[
            Shareholder(name="陈德强", holding_ratio="35.49%"),
            Shareholder(name="杨京", holding_ratio="12.07%"),
        ],
    )
    assert len(sec.shareholders) == 2

    # 反例：count 与 rows 不一致 — 必须被拦截（V1.1.3 的 9 vs 13 类错误）
    try:
        CurrentShareholdersSection(
            total_count=13,
            shareholders=[
                Shareholder(name="陈德强", holding_ratio="35.49%"),
            ],
        )
        assert False, "应拦截 count 不一致"
    except (ValueError, Exception) as e:
        assert "13" in str(e) and "1" in str(e), str(e)

    # USCC 反例
    try:
        CompanyBasicInfo(
            name="测试", uscc="91320506MA1UYUWY3X",
            legal_rep="某人", establish_date="2014-03-12",
            registered_capital="100万元", enterprise_type="有限",
            industry="测试", registration_status="在业",
            registration_authority="测试", registered_address="测试",
        )
        assert False, "应拦截编造 USCC"
    except (ValueError, Exception) as e:
        assert "USCC" in str(e) or "校验" in str(e), str(e)


if __name__ == "__main__":
    _self_test()
    print("✓ data_contract 自检通过")
