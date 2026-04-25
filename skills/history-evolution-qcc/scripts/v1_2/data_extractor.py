"""
data_extractor.py · MCP 调用 → ReportSchema 转换器
=================================================================
作用：把 MCP 工具的原始 JSON 返回，转换为 ReportSchema 对象 + 完整 evidence 链。

设计原则（针对 V1.1.3 事故）：
1. 所有"数字字段"（count、年度分布、级别统计）一律由本模块从原始 list 算出，
   不接受调用方手写。例如专利年度分布必须用 `yearly_distribution()` 自动生成。
2. 每个被消费的 MCP 字段都必须 record_evidence — 否则 manifest 不完整。
3. 严禁"基于经验补全" — 如果 MCP 没返回某字段，目标字段就为 None / 空字符串，
   绝不允许 LLM 风格的合理化。

调用方式（伪代码）：
    extractor = ReportExtractor(uscc="91320594088140947F")
    extractor.fetch_all(mcp_client)        # 调用所有需要的 MCP 工具
    report = extractor.build_report_schema()  # 输出已通过 schema 校验的对象
    extractor.manifest.write("manifest.json")
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Callable

from .evidence import Evidence, MCPCallRecorder, ManifestBuilder
from .uscc_validator import validate_uscc, USCCValidationError

# 注意：data_contract 在测试时可能无 pydantic — 用条件导入
try:
    from .data_contract import (
        ReportSchema, CompanyBasicInfo,
        CurrentShareholdersSection, Shareholder,
        HistoricalShareholdersSection, HistoricalShareholder,
        ExecutiveSection, Executive, HistoricalExecutive,
        InvestmentSection, Investment,
        HistoricalRegistrationSection,
        HistoricalCapitalNode, HistoricalNameNode, HistoricalAddressNode,
        QualificationSection, Qualification,
        HonorSection, Honor,
        PatentSection, Patent,
        AdministrativePenaltySection, AdministrativePenalty,
        PYDANTIC_OK,
    )
except ImportError:
    PYDANTIC_OK = False


class ReportExtractor:
    """
    从 MCP 工具返回原始数据出发，构造 ReportSchema 并记录 evidence。

    关键约束：
    - 必须先校验 USCC
    - 每个数字字段（count）必须从 list 长度直接算出，不能从摘要文本里 parse
    """

    # MCP 工具名常量（避免 typo）
    TOOL_REGISTRATION_INFO = "qcc-company.get_company_registration_info"
    TOOL_SHAREHOLDER_INFO = "qcc-company.get_shareholder_info"
    TOOL_HIST_SHAREHOLDERS = "qcc-history.get_historical_shareholders"
    TOOL_KEY_PERSONNEL = "qcc-company.get_key_personnel"
    TOOL_HIST_EXECUTIVES = "qcc-history.get_historical_executives"
    TOOL_EXTERNAL_INVESTMENTS = "qcc-company.get_external_investments"
    TOOL_HIST_REGISTRATION = "qcc-history.get_historical_registration"
    TOOL_QUALIFICATIONS = "qcc-operation.get_qualifications"
    TOOL_HONOR_INFO = "qcc-operation.get_honor_info"
    TOOL_PATENT_INFO = "qcc-ipr.get_patent_info"
    TOOL_ADMIN_PENALTY = "qcc-risk.get_administrative_penalty"
    TOOL_CHANGE_RECORDS = "qcc-company.get_change_records"

    def __init__(self, *, uscc: str, report_id: str | None = None):
        ok, msg = validate_uscc(uscc)
        if not ok:
            raise USCCValidationError(f"传入的 USCC 不合法：{msg} · 值：{uscc}")
        self.uscc = uscc
        self.report_id = report_id or self._auto_report_id()
        self.recorders: dict[str, MCPCallRecorder] = {}
        self.manifest: ManifestBuilder | None = None

    @staticmethod
    def _auto_report_id() -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"SKILL-HE-QCC-{ts}"

    def fetch_all(self, mcp_call: Callable[[str, str], dict]) -> None:
        """一次性拉取所有 MCP 工具数据。

        Args:
            mcp_call: 函数 (tool_name, search_key) -> json_response
        """
        for tool in [
            self.TOOL_REGISTRATION_INFO,
            self.TOOL_SHAREHOLDER_INFO,
            self.TOOL_HIST_SHAREHOLDERS,
            self.TOOL_KEY_PERSONNEL,
            self.TOOL_HIST_EXECUTIVES,
            self.TOOL_EXTERNAL_INVESTMENTS,
            self.TOOL_HIST_REGISTRATION,
            self.TOOL_QUALIFICATIONS,
            self.TOOL_HONOR_INFO,
            self.TOOL_PATENT_INFO,
            self.TOOL_ADMIN_PENALTY,
            self.TOOL_CHANGE_RECORDS,
        ]:
            recorder = MCPCallRecorder(tool_name=tool, search_key=self.uscc)
            response = mcp_call(tool, self.uscc)
            recorder.record_response(response)
            self.recorders[tool] = recorder

    def feed(self, tool_name: str, response: dict) -> None:
        """逐个工具喂数据（适合在 LLM 编排环境用，逐次拼装）。"""
        recorder = MCPCallRecorder(tool_name=tool_name, search_key=self.uscc)
        recorder.record_response(response)
        self.recorders[tool_name] = recorder

    # ------------------------------------------------------------------
    # 转换为 ReportSchema
    # ------------------------------------------------------------------

    def build_report_schema(self):
        """构造 ReportSchema 对象（同时填充 manifest）。"""
        if not PYDANTIC_OK:
            raise RuntimeError("需要安装 pydantic：pip install pydantic")

        company_name = self._extract_company_name()
        self.manifest = ManifestBuilder(
            report_id=self.report_id,
            company_name=company_name,
            uscc=self.uscc,
        )

        company = self._build_company()
        hist_reg = self._build_historical_registration()
        cur_sh = self._build_current_shareholders()
        hist_sh = self._build_historical_shareholders()
        executives = self._build_executives()
        investments = self._build_investments()
        qualifications = self._build_qualifications()
        honors = self._build_honors()
        patents = self._build_patents()
        penalties = self._build_penalties()
        change_count = self._extract_change_records_count()

        return ReportSchema(
            report_id=self.report_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            company=company,
            historical_registration=hist_reg,
            current_shareholders=cur_sh,
            historical_shareholders=hist_sh,
            executives=executives,
            investments=investments,
            qualifications=qualifications,
            honors=honors,
            patents=patents,
            administrative_penalties=penalties,
            change_records_count=change_count,
        )

    # ------------------------------------------------------------------
    # 各章节构造（每条字段都通过 recorder 取 evidence）
    # ------------------------------------------------------------------

    def _extract_company_name(self) -> str:
        rec = self.recorders.get(self.TOOL_REGISTRATION_INFO)
        if not rec:
            return "未知"
        ev = rec.evidence_for("$.企业名称")
        return ev.raw_value

    def _build_company(self) -> CompanyBasicInfo:
        rec = self.recorders[self.TOOL_REGISTRATION_INFO]
        # 取每个字段并记录 evidence
        def field(path: str, *, optional: bool = False):
            try:
                ev = rec.evidence_for(path)
                self.manifest.attach(f"company.{path[2:]}", ev)
                return ev.raw_value
            except KeyError:
                if optional:
                    return None
                raise

        capital = field("$.注册资本")
        # 例如 "36225万元"，统一保留完整字符串
        return CompanyBasicInfo(
            name=field("$.企业名称"),
            uscc=field("$.统一社会信用代码"),
            legal_rep=field("$.法定代表人"),
            establish_date=field("$.成立日期"),
            registered_capital=capital,
            paid_capital=field("$.实缴资本", optional=True),
            enterprise_type=field("$.企业类型"),
            industry=field("$.国标行业"),
            registration_status=field("$.登记状态"),
            registration_authority=field("$.登记机关"),
            approval_date=field("$.核准日期", optional=True),
            region=field("$.所属地区", optional=True),
            registered_address=field("$.注册地址"),
            insured_count=_safe_int(field("$.参保人数", optional=True)),
        )

    def _build_historical_registration(self) -> HistoricalRegistrationSection:
        rec = self.recorders[self.TOOL_HIST_REGISTRATION]
        cur_rec = self.recorders[self.TOOL_REGISTRATION_INFO]
        company_name = cur_rec.evidence_for("$.企业名称").raw_value
        cur_capital = cur_rec.evidence_for("$.注册资本").raw_value
        cur_address = cur_rec.evidence_for("$.注册地址").raw_value

        capital_nodes: list[HistoricalCapitalNode] = []
        # 当前
        capital_nodes.append(HistoricalCapitalNode(
            capital=cur_capital, start_date=None, end_date=None,  # None 即"当前"
        ))
        for i, item in enumerate(rec._response.get("历史注册资本列表", []) or []):
            ev = rec.evidence_for(f"$.历史注册资本列表[{i}].历史注册资本")
            self.manifest.attach(f"historical_capital[{i}]", ev)
            capital_nodes.append(HistoricalCapitalNode(
                capital=item.get("历史注册资本", ""),
                start_date=item.get("起始日期") or None,
                end_date=item.get("终止日期") or None,
            ))

        name_nodes: list[HistoricalNameNode] = []
        name_nodes.append(HistoricalNameNode(
            name=company_name, start_date=None, end_date=None,
        ))
        for i, item in enumerate(rec._response.get("历史名称列表", []) or []):
            ev = rec.evidence_for(f"$.历史名称列表[{i}].历史名称")
            self.manifest.attach(f"historical_name[{i}]", ev)
            name_nodes.append(HistoricalNameNode(
                name=item.get("历史名称", ""),
                start_date=item.get("起始日期") or None,
                end_date=item.get("终止日期") or None,
            ))

        address_nodes: list[HistoricalAddressNode] = []
        address_nodes.append(HistoricalAddressNode(
            address=cur_address, start_date=None, end_date=None,
        ))
        for i, item in enumerate(rec._response.get("历史地址列表", []) or []):
            ev = rec.evidence_for(f"$.历史地址列表[{i}].历史地址")
            self.manifest.attach(f"historical_address[{i}]", ev)
            address_nodes.append(HistoricalAddressNode(
                address=item.get("历史地址", ""),
                start_date=item.get("起始日期") or None,
                end_date=item.get("终止日期") or None,
            ))

        return HistoricalRegistrationSection(
            capital_nodes=capital_nodes,
            name_nodes=name_nodes,
            address_nodes=address_nodes,
        )

    def _build_current_shareholders(self) -> CurrentShareholdersSection:
        rec = self.recorders[self.TOOL_SHAREHOLDER_INFO]
        items = rec._response.get("股东信息", []) or []
        # 计数从 list 长度直接取，不从"摘要"字符串 parse
        count = len(items)
        shareholders = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.股东信息[{i}].股东名称")
            self.manifest.attach(f"shareholders[{i}].name", ev)
            shareholders.append(Shareholder(
                name=item.get("股东名称", ""),
                holding_ratio=item.get("持股比例", ""),
                shares=item.get("持股数") or None,
            ))
        return CurrentShareholdersSection(total_count=count, shareholders=shareholders)

    def _build_historical_shareholders(self) -> HistoricalShareholdersSection:
        rec = self.recorders[self.TOOL_HIST_SHAREHOLDERS]
        items = rec._response.get("历史股东信息", []) or []
        count = len(items)
        result = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.历史股东信息[{i}].股东名称")
            self.manifest.attach(f"historical_shareholders[{i}].name", ev)
            result.append(HistoricalShareholder(
                name=item.get("股东名称", ""),
                exit_date=item.get("退出日期", ""),
                exit_ratio=item.get("退出时持股比例") or None,
                capital=item.get("认缴出资额") or None,
                shareholder_type=item.get("股东类型") or None,
            ))
        return HistoricalShareholdersSection(total_count=count, exited_shareholders=result)

    def _build_executives(self) -> ExecutiveSection:
        cur_rec = self.recorders[self.TOOL_KEY_PERSONNEL]
        cur_items = cur_rec._response.get("主要人员信息", []) or []
        cur_executives = []
        for i, item in enumerate(cur_items):
            ev = cur_rec.evidence_for(f"$.主要人员信息[{i}].姓名")
            self.manifest.attach(f"current_executives[{i}].name", ev)
            cur_executives.append(Executive(
                name=item.get("姓名", ""),
                position=item.get("职务", ""),
                holding_ratio=item.get("持股比例") or None,
            ))

        hist_rec = self.recorders[self.TOOL_HIST_EXECUTIVES]
        hist_items = hist_rec._response.get("历史主要人员信息", []) or []
        hist_executives = []
        for i, item in enumerate(hist_items):
            ev = hist_rec.evidence_for(f"$.历史主要人员信息[{i}].姓名")
            self.manifest.attach(f"historical_executives[{i}].name", ev)
            hist_executives.append(HistoricalExecutive(
                name=item.get("姓名", ""),
                position=item.get("职务", ""),
                appointment_date=item.get("任职日期") or None,
                departure_date=item.get("卸任日期", ""),
            ))

        return ExecutiveSection(
            current_count=len(cur_items),
            current_executives=cur_executives,
            historical_count=len(hist_items),
            historical_executives=hist_executives,
        )

    def _build_investments(self) -> InvestmentSection:
        rec = self.recorders[self.TOOL_EXTERNAL_INVESTMENTS]
        items = rec._response.get("对外投资信息", []) or []
        result = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.对外投资信息[{i}].被投资企业名称")
            self.manifest.attach(f"investments[{i}].name", ev)
            result.append(Investment(
                invested_company=item.get("被投资企业名称", ""),
                holding_ratio=item.get("持股比例", ""),
                establish_date=item.get("成立日期") or None,
                capital=item.get("认缴出资额/持股数") or None,
                status=item.get("状态") or None,
            ))
        return InvestmentSection(total_count=len(items), investments=result)

    def _build_qualifications(self) -> QualificationSection:
        rec = self.recorders[self.TOOL_QUALIFICATIONS]
        items = rec._response.get("资质证书信息", []) or []
        result = []
        valid_count = 0
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.资质证书信息[{i}].资质名称")
            self.manifest.attach(f"qualifications[{i}].name", ev)
            status = item.get("证书状态", "")
            if status == "有效":
                valid_count += 1
            result.append(Qualification(
                name=item.get("资质名称", ""),
                issue_date=item.get("发证日期") or None,
                expiry_date=item.get("有效期至") or None,
                category=item.get("类别与等级") or None,
                status=status or None,
            ))
        return QualificationSection(
            total_count=len(items),
            valid_count=valid_count,
            qualifications=result,
        )

    def _build_honors(self) -> HonorSection:
        rec = self.recorders[self.TOOL_HONOR_INFO]
        items = rec._response.get("荣誉信息", []) or []
        result = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.荣誉信息[{i}].名称")
            self.manifest.attach(f"honors[{i}].name", ev)
            result.append(Honor(
                name=item.get("名称", ""),
                publish_date=item.get("发布日期", ""),
                level=item.get("级别", ""),
                issuer=item.get("发布单位", ""),
                certified_year=item.get("认证年份") or None,
            ))
        return HonorSection(total_count=len(items), honors=result)

    def _build_patents(self) -> PatentSection:
        rec = self.recorders[self.TOOL_PATENT_INFO]
        items = rec._response.get("专利信息", []) or []
        result = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.专利信息[{i}].申请号")
            self.manifest.attach(f"patents[{i}].application_no", ev)
            result.append(Patent(
                title=item.get("发明名称", ""),
                application_no=item.get("申请号", ""),
                application_date=item.get("申请日期", ""),
                publish_no=item.get("公开（公告）号") or None,
                publish_date=item.get("公开（公告）日期") or None,
                patent_type=item.get("专利类型", ""),
                legal_status=item.get("法律状态") or None,
            ))
        return PatentSection(total_count=len(items), patents=result)

    def _build_penalties(self) -> AdministrativePenaltySection:
        rec = self.recorders[self.TOOL_ADMIN_PENALTY]
        items = rec._response.get("行政处罚信息", []) or []
        result = []
        for i, item in enumerate(items):
            ev = rec.evidence_for(f"$.行政处罚信息[{i}].决定书文号")
            self.manifest.attach(f"penalties[{i}].decision_no", ev)
            result.append(AdministrativePenalty(
                decision_no=item.get("决定书文号", ""),
                penalty_date=item.get("处罚日期", ""),
                penalty_authority=item.get("处罚单位", ""),
                penalty_amount=item.get("处罚金额") or None,
                penalty_result=item.get("处罚结果") or None,
                # 注意：MCP 不返回的字段（如违法行为类型、处置状态）严禁补全
            ))
        return AdministrativePenaltySection(total_count=len(items), penalties=result)

    def _extract_change_records_count(self) -> int:
        rec = self.recorders.get(self.TOOL_CHANGE_RECORDS)
        if not rec or not rec._response:
            return 0
        items = rec._response.get("变更记录信息", []) or []
        return len(items)


def _safe_int(v) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return int(re.sub(r"\D", "", str(v)))
        except Exception:
            return None
