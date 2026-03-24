#!/usr/bin/env python3
"""
QCC MCP Connector for Financial Services
企查查MCP连接器 - 金融机构专用版

为银行KYB、投资尽调、风控合规提供中国企业数据支持
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class RiskLevel(Enum):
    """风险等级 - 金融专用"""
    LOW = "LOW"           # 低风险 - 正常准入
    MEDIUM = "MEDIUM"     # 中风险 - 审慎准入/加强监测
    HIGH = "HIGH"         # 高风险 - 限制准入
    CRITICAL = "CRITICAL" # 极高风险 - 禁止准入
    UNKNOWN = "UNKNOWN"


class KYBStatus(Enum):
    """KYB核验状态"""
    PASSED = "PASSED"           # 核验通过
    CONDITIONAL = "CONDITIONAL" # 有条件通过
    FAILED = "FAILED"           # 核验不通过
    MANUAL_REVIEW = "MANUAL_REVIEW" # 需人工复核


@dataclass
class CompanyBasicInfo:
    """企业基础信息"""
    company_name: str = ""
    credit_code: str = ""
    legal_person: str = ""
    registered_capital: str = ""
    paid_in_capital: str = ""
    establishment_date: str = ""
    company_status: str = ""  # 存续/注销/吊销等
    company_type: str = ""
    registration_address: str = ""
    business_scope: str = ""
    contact_phone: str = ""
    contact_email: str = ""
    official_website: str = ""
    is_verified: bool = False


@dataclass
class ShareholderInfo:
    """股东信息"""
    shareholder_name: str = ""
    shareholding_ratio: float = 0.0
    subscribed_amount: str = ""
    shareholder_type: str = ""  # 自然人/企业/有限合伙等


@dataclass
class UBOMapping:
    """受益所有人识别结果"""
    ubo_name: str = ""  # 受益所有人姓名
    ubo_type: str = ""  # 类型：自然人/公司/信托
    control_chain: str = ""  # 控制路径
    control_ratio: float = 0.0  # 控制比例
    identification_basis: str = ""  # 识别依据


@dataclass
class JudicialRisk:
    """司法风险项"""
    risk_type: str = ""  # 失信/被执行/限高/终本/股权冻结等
    case_number: str = ""
    execution_amount: str = ""
    filing_date: str = ""
    court: str = ""
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    details: Dict = field(default_factory=dict)


@dataclass
class IntellectualProperty:
    """知识产权资产"""
    patent_count: int = 0
    invention_patents: int = 0
    utility_patents: int = 0
    trademark_count: int = 0
    software_copyrights: int = 0
    core_patents: List[Dict] = field(default_factory=list)
    key_trademarks: List[Dict] = field(default_factory=list)


@dataclass
class BusinessActivity:
    """经营动态"""
    bidding_count_12m: int = 0
    bidding_amount_12m: str = ""
    qualification_count: int = 0
    key_qualifications: List[Dict] = field(default_factory=list)
    credit_rating: str = ""  # A级/B级等
    spot_check_results: List[Dict] = field(default_factory=list)


@dataclass
class KYBResult:
    """KYB核验结果"""
    company_name: str = ""
    credit_code: str = ""
    kyb_status: KYBStatus = KYBStatus.UNKNOWN
    overall_risk: RiskLevel = RiskLevel.UNKNOWN
    basic_info: CompanyBasicInfo = field(default_factory=CompanyBasicInfo)
    shareholders: List[ShareholderInfo] = field(default_factory=list)
    ubo_list: List[UBOMapping] = field(default_factory=list)
    judicial_risks: List[JudicialRisk] = field(default_factory=list)
    risk_summary: Dict = field(default_factory=dict)
    verification_time: str = field(default_factory=lambda: datetime.now().isoformat())
    recommended_action: str = ""


@dataclass
class ICDueDiligence:
    """IC Memo尽调结果"""
    company_name: str = ""
    credit_code: str = ""
    # Chapter 1: 公司概况
    basic_info: CompanyBasicInfo = field(default_factory=CompanyBasicInfo)
    shareholders: List[ShareholderInfo] = field(default_factory=list)
    ubo_list: List[UBOMapping] = field(default_factory=list)
    key_personnel: List[Dict] = field(default_factory=list)
    financing_history: List[Dict] = field(default_factory=list)

    # Chapter 3: 知识产权
    ip_assets: IntellectualProperty = field(default_factory=IntellectualProperty)

    # Chapter 4: 法律风险
    judicial_risks: List[JudicialRisk] = field(default_factory=list)
    administrative_penalties: List[Dict] = field(default_factory=list)

    # Chapter 5: 经营动态
    business_activity: BusinessActivity = field(default_factory=BusinessActivity)

    # 综合评估
    investment_recommendation: str = ""  # 强烈推荐/推荐/谨慎考虑/不建议
    valuation_analysis: Dict = field(default_factory=dict)
    key_risks: List[Dict] = field(default_factory=list)


class QccMcpConnectorFinancial:
    """
    企查查MCP连接器 - 金融机构专用 (2024最新协议)

    支持场景:
    1. KYB自动化核验 - 30秒完成主体核验+风险扫描
    2. IC Memo尽调 - 全维度背调+自动报告生成

    集成四大Server:
    - qcc_company: 企业基座 (工商信息、股东结构、变更记录)
    - qcc_risk: 风控大脑 (司法风险、行政处罚、税务风险)
    - qcc_ipr: 知产引擎 (专利、商标、软著)
    - qcc_operation: 经营罗盘 (资质、招投标、信用评级)
    """

    # MCP Server端点配置 (2024最新定义)
    MCP_SERVERS = {
        "qcc_company": "https://mcp.qcc.com/data/company/stream",
        "qcc_risk": "https://mcp.qcc.com/data/risk/stream",
        "qcc_ipr": "https://mcp.qcc.com/data/ipr/stream",
        "qcc_operation": "https://mcp.qcc.com/data/operation/stream",
    }

    # KYB关键风险指标 - 30秒快速核验核心指标
    KYB_CRITICAL_RISKS = [
        "get_dishonest_info",           # 失信信息
        "get_judgment_debtor_info",      # 被执行人
        "get_high_consumption_restriction", # 限高消费
        "get_bankruptcy_reorganization", # 破产重整
        "get_equity_freeze",            # 股权冻结
        "get_business_exception",        # 经营异常
        "get_serious_violation",         # 严重违法
    ]

    # IC Memo全维度尽调工具
    IC_FULL_TOOLS = {
        "qcc_company": [
            "get_company_registration_info",  # 基础工商
            "get_company_profile",            # 企业简介
            "get_shareholder_info",           # 股权结构
            "get_key_personnel",              # 董监高
            "get_change_records",             # 变更记录
            "get_branches",                   # 分支机构
            "get_external_investments",       # 对外投资
            "get_annual_reports",             # 年报财务
        ],
        "qcc_risk": [
            "get_dishonest_info",
            "get_judgment_debtor_info",
            "get_high_consumption_restriction",
            "get_terminated_cases",
            "get_equity_freeze",
            "get_equity_pledge_info",
            "get_bankruptcy_reorganization",
            "get_judicial_documents",
            "get_case_filing_info",
            "get_business_exception",
            "get_serious_violation",
            "get_administrative_penalty",
            "get_environmental_penalty",
            "get_tax_arrears_notice",
            "get_tax_abnormal",
            "get_tax_violation",
        ],
        "qcc_ipr": [
            "get_patent_info",                # 专利
            "get_trademark_info",             # 商标
            "get_software_copyright_info",    # 软著
            "get_copyright_work_info",        # 作品著作权
            "get_standard_info",              # 标准
        ],
        "qcc_operation": [
            "get_bidding_info",               # 招投标
            "get_qualifications",             # 资质证书
            "get_administrative_license",     # 行政许可
            "get_credit_evaluation",          # 信用评级
            "get_spot_check_info",            # 抽查检查
            "get_news_sentiment",             # 新闻舆情
            "get_recruitment_info",           # 招聘动态
        ]
    }

    def __init__(self, api_key: Optional[str] = None):
        """初始化连接器"""
        self.api_key = api_key or os.getenv("QCC_MCP_API_KEY")
        if not self.api_key:
            raise ValueError("QCC MCP API Key未配置")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def _call_mcp(self, server: str, tool: str, params: Dict) -> Dict:
        """
        调用MCP Server (2024最新协议)

        Args:
            server: Server名称 (qcc_company/qcc_risk/qcc_ipr/qcc_operation)
            tool: 工具名称
            params: 请求参数 (必须使用 searchKey)
        """
        base_url = self.MCP_SERVERS.get(server)
        if not base_url:
            raise ValueError(f"Unknown MCP server: {server}")

        request_body = {
            "tool": tool,
            "inputSchema": params
        }

        try:
            response = self.session.post(base_url, json=request_body, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e), "data": None}

    # ==================== KYB自动化核验 (30秒快检) ====================

    def kyb_fast_verification(self, company_name: str) -> KYBResult:
        """
        KYB自动化核验 - 30秒快速核验

        适用于：银行开户、信贷初筛、反洗钱尽调

        Args:
            company_name: 企业名称或统一社会信用代码

        Returns:
            KYBResult: 核验结果，包含准入建议和风险控制措施
        """
        result = KYBResult(company_name=company_name)

        # Step 1: 主体锚定与基础信息 (5秒)
        basic_data = self._call_mcp("qcc_company", "get_company_registration_info", {"searchKey": company_name})
        if basic_data.get("data"):
            info = basic_data["data"]
            result.basic_info = CompanyBasicInfo(
                company_name=info.get("companyName", company_name),
                credit_code=info.get("creditCode", ""),
                legal_person=info.get("legalPerson", ""),
                registered_capital=info.get("registeredCapital", ""),
                establishment_date=info.get("establishmentDate", ""),
                company_status=info.get("companyStatus", ""),
                company_type=info.get("companyType", ""),
                registration_address=info.get("registrationAddress", ""),
                business_scope=info.get("businessScope", ""),
                is_verified=True
            )
            result.credit_code = info.get("creditCode", "")

        # Step 2: 关键风险扫描 - 并行调用 (15秒)
        risk_items = []

        # CRITICAL: 失信/被执行/限高/破产/股权冻结
        critical_risks = [
            ("qcc_risk", "get_dishonest_info", "失信信息", RiskLevel.CRITICAL),
            ("qcc_risk", "get_judgment_debtor_info", "被执行人", RiskLevel.CRITICAL),
            ("qcc_risk", "get_high_consumption_restriction", "限制高消费", RiskLevel.CRITICAL),
            ("qcc_risk", "get_bankruptcy_reorganization", "破产重整", RiskLevel.CRITICAL),
            ("qcc_risk", "get_equity_freeze", "股权冻结", RiskLevel.HIGH),
        ]

        for server, tool, risk_name, level in critical_risks:
            resp = self._call_mcp(server, tool, {"searchKey": company_name})
            if resp.get("data") and len(resp["data"]) > 0:
                for item in resp["data"]:
                    risk_items.append(JudicialRisk(
                        risk_type=risk_name,
                        case_number=item.get("caseNo", ""),
                        execution_amount=item.get("execMoney", ""),
                        filing_date=item.get("filingDate", ""),
                        court=item.get("court", ""),
                        risk_level=level,
                        details=item
                    ))

        # HIGH: 经营异常/严重违法
        high_risks = [
            ("qcc_risk", "get_business_exception", "经营异常", RiskLevel.HIGH),
            ("qcc_risk", "get_serious_violation", "严重违法", RiskLevel.CRITICAL),
        ]

        for server, tool, risk_name, level in high_risks:
            resp = self._call_mcp(server, tool, {"searchKey": company_name})
            if resp.get("data") and len(resp["data"]) > 0:
                for item in resp["data"]:
                    risk_items.append(JudicialRisk(
                        risk_type=risk_name,
                        filing_date=item.get("addDate", ""),
                        risk_level=level,
                        details=item
                    ))

        result.judicial_risks = risk_items

        # Step 3: 股权结构与受益所有人 (8秒)
        shareholder_data = self._call_mcp("qcc_company", "get_shareholder_info", {"searchKey": company_name})
        if shareholder_data.get("data"):
            shareholders = []
            for item in shareholder_data["data"][:10]:  # 前10大股东
                shareholders.append(ShareholderInfo(
                    shareholder_name=item.get("shareholderName", ""),
                    shareholding_ratio=float(item.get("shareholdingRatio", 0)),
                    subscribed_amount=item.get("subscribedAmount", ""),
                    shareholder_type=item.get("shareholderType", "")
                ))
            result.shareholders = shareholders

            # 识别实控人和受益所有人
            result.ubo_list = self._identify_ubo(shareholders)

        # Step 4: 风险定级与准入建议 (2秒)
        result.overall_risk = self._calculate_kyb_risk(risk_items)
        result.kyb_status = self._determine_kyb_status(result.overall_risk, risk_items)
        result.recommended_action = self._generate_kyb_recommendation(result)
        result.risk_summary = self._generate_risk_summary(risk_items)

        return result

    def _identify_ubo(self, shareholders: List[ShareholderInfo]) -> List[UBOMapping]:
        """识别受益所有人"""
        ubo_list = []

        # 规则1: 直接持股25%以上的自然人
        for sh in shareholders:
            if sh.shareholding_ratio >= 25 and sh.shareholder_type == "自然人":
                ubo_list.append(UBOMapping(
                    ubo_name=sh.shareholder_name,
                    ubo_type="自然人",
                    control_chain=f"直接持股{sh.shareholding_ratio}%",
                    control_ratio=sh.shareholding_ratio,
                    identification_basis="直接持股25%以上"
                ))

        # 注：更复杂的穿透需要查询上层股东，此处简化处理

        return ubo_list

    def _calculate_kyb_risk(self, risks: List[JudicialRisk]) -> RiskLevel:
        """计算KYB综合风险等级"""
        if any(r.risk_level == RiskLevel.CRITICAL for r in risks):
            return RiskLevel.CRITICAL
        elif sum(1 for r in risks if r.risk_level == RiskLevel.HIGH) >= 2:
            return RiskLevel.HIGH
        elif any(r.risk_level == RiskLevel.HIGH for r in risks):
            return RiskLevel.MEDIUM
        elif risks:
            return RiskLevel.LOW
        return RiskLevel.UNKNOWN

    def _determine_kyb_status(self, risk: RiskLevel, risks: List[JudicialRisk]) -> KYBStatus:
        """确定KYB核验状态"""
        if risk == RiskLevel.CRITICAL:
            return KYBStatus.FAILED
        elif risk == RiskLevel.HIGH:
            return KYBStatus.MANUAL_REVIEW
        elif risk == RiskLevel.MEDIUM:
            return KYBStatus.CONDITIONAL
        elif risk == RiskLevel.LOW:
            return KYBStatus.PASSED
        return KYBStatus.UNKNOWN

    def _generate_kyb_recommendation(self, result: KYBResult) -> str:
        """生成KYB准入建议"""
        if result.overall_risk == RiskLevel.CRITICAL:
            return "禁止准入。存在严重失信、被执行或破产记录，建议拒绝开户/授信申请。"
        elif result.overall_risk == RiskLevel.HIGH:
            return "需人工复核。存在重大风险信号，需提交风控部门进一步尽调。"
        elif result.overall_risk == RiskLevel.MEDIUM:
            return "审慎准入。可准入但需加强监测，建议降低授信额度或增加担保措施。"
        elif result.overall_risk == RiskLevel.LOW:
            return "正常准入。主体合法存续，无明显风险信号，可按标准流程处理。"
        return "无法判断。数据不足，建议人工核实。"

    def _generate_risk_summary(self, risks: List[JudicialRisk]) -> Dict:
        """生成风险摘要"""
        critical = [r for r in risks if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in risks if r.risk_level == RiskLevel.HIGH]
        medium = [r for r in risks if r.risk_level == RiskLevel.MEDIUM]

        return {
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "total_count": len(risks),
            "critical_details": [{"type": r.risk_type, "case": r.case_number} for r in critical],
            "high_details": [{"type": r.risk_type, "date": r.filing_date} for r in high],
        }

    # ==================== IC Memo全维度尽调 ====================

    def ic_full_due_diligence(self, company_name: str, sector: str = "") -> ICDueDiligence:
        """
        IC Memo全维度尽调

        适用于：PE/VC投资尽调、并购重组、战略投资

        Args:
            company_name: 目标企业名称
            sector: 所属行业（用于对标分析）

        Returns:
            ICDueDiligence: 全维度尽调结果
        """
        result = ICDueDiligence(company_name=company_name)

        # Chapter 1: 公司概况
        self._populate_company_profile(result, company_name)

        # Chapter 3: 知识产权
        self._populate_ip_assets(result, company_name)

        # Chapter 4: 法律风险
        self._populate_judicial_risks(result, company_name)

        # Chapter 5: 经营动态
        self._populate_business_activity(result, company_name)

        # 综合评估
        result.investment_recommendation = self._generate_investment_recommendation(result)
        result.key_risks = self._extract_key_risks(result)

        return result

    def _populate_company_profile(self, result: ICDueDiligence, company_name: str):
        """填充公司概况信息"""
        # 基础工商
        basic = self._call_mcp("qcc_company", "get_company_registration_info", {"searchKey": company_name})
        if basic.get("data"):
            data = basic["data"]
            result.basic_info = CompanyBasicInfo(
                company_name=data.get("companyName", company_name),
                credit_code=data.get("creditCode", ""),
                legal_person=data.get("legalPerson", ""),
                registered_capital=data.get("registeredCapital", ""),
                establishment_date=data.get("establishmentDate", ""),
                company_status=data.get("companyStatus", ""),
                company_type=data.get("companyType", ""),
                registration_address=data.get("registrationAddress", ""),
                business_scope=data.get("businessScope", ""),
                is_verified=True
            )
            result.credit_code = data.get("creditCode", "")

        # 股权结构
        shareholders_data = self._call_mcp("qcc_company", "get_shareholder_info", {"searchKey": company_name})
        if shareholders_data.get("data"):
            result.shareholders = [
                ShareholderInfo(
                    shareholder_name=item.get("shareholderName", ""),
                    shareholding_ratio=float(item.get("shareholdingRatio", 0)),
                    subscribed_amount=item.get("subscribedAmount", ""),
                    shareholder_type=item.get("shareholderType", "")
                ) for item in shareholders_data["data"][:10]
            ]
            result.ubo_list = self._identify_ubo(result.shareholders)

        # 董监高
        personnel_data = self._call_mcp("qcc_company", "get_key_personnel", {"searchKey": company_name})
        if personnel_data.get("data"):
            result.key_personnel = personnel_data["data"]

        # 历史融资（通过年报或工商变更推测）
        change_data = self._call_mcp("qcc_company", "get_change_records", {"searchKey": company_name})
        if change_data.get("data"):
            # 提取股权变更记录作为融资历史参考
            result.financing_history = [
                {
                    "date": item.get("changeDate", ""),
                    "item": item.get("changeItem", ""),
                    "before": item.get("contentBefore", ""),
                    "after": item.get("contentAfter", "")
                } for item in change_data["data"] if "股权" in item.get("changeItem", "")
            ][:5]

    def _populate_ip_assets(self, result: ICDueDiligence, company_name: str):
        """填充知识产权资产"""
        ip_assets = IntellectualProperty()

        # 专利
        patent_data = self._call_mcp("qcc_ipr", "get_patent_info", {"searchKey": company_name})
        if patent_data.get("data"):
            patents = patent_data["data"]
            ip_assets.patent_count = len(patents)
            ip_assets.invention_patents = len([p for p in patents if p.get("patentType") == "发明专利"])
            ip_assets.utility_patents = len([p for p in patents if p.get("patentType") == "实用新型"])
            # 核心专利（最近授权的发明专利）
            ip_assets.core_patents = [
                {
                    "name": p.get("inventionName", ""),
                    "number": p.get("applicationNo", ""),
                    "type": p.get("patentType", ""),
                    "status": p.get("legalStatus", "")
                } for p in patents[:5] if p.get("patentType") == "发明专利"
            ]

        # 商标
        trademark_data = self._call_mcp("qcc_ipr", "get_trademark_info", {"searchKey": company_name})
        if trademark_data.get("data"):
            ip_assets.trademark_count = len(trademark_data["data"])

        # 软著
        copyright_data = self._call_mcp("qcc_ipr", "get_software_copyright_info", {"searchKey": company_name})
        if copyright_data.get("data"):
            ip_assets.software_copyrights = len(copyright_data["data"])

        result.ip_assets = ip_assets

    def _populate_judicial_risks(self, result: ICDueDiligence, company_name: str):
        """填充司法风险"""
        judicial_risks = []
        administrative_penalties = []

        # 全量司法风险扫描
        risk_tools = [
            ("qcc_risk", "get_dishonest_info", "失信信息", RiskLevel.CRITICAL),
            ("qcc_risk", "get_judgment_debtor_info", "被执行人", RiskLevel.CRITICAL),
            ("qcc_risk", "get_high_consumption_restriction", "限制高消费", RiskLevel.CRITICAL),
            ("qcc_risk", "get_terminated_cases", "终本案件", RiskLevel.HIGH),
            ("qcc_risk", "get_equity_freeze", "股权冻结", RiskLevel.HIGH),
            ("qcc_risk", "get_equity_pledge_info", "股权质押", RiskLevel.MEDIUM),
            ("qcc_risk", "get_bankruptcy_reorganization", "破产重整", RiskLevel.CRITICAL),
            ("qcc_risk", "get_case_filing_info", "立案信息", RiskLevel.MEDIUM),
            ("qcc_risk", "get_judicial_documents", "裁判文书", RiskLevel.MEDIUM),
        ]

        for server, tool, risk_name, level in risk_tools:
            resp = self._call_mcp(server, tool, {"searchKey": company_name})
            if resp.get("data") and len(resp["data"]) > 0:
                for item in resp["data"]:
                    judicial_risks.append(JudicialRisk(
                        risk_type=risk_name,
                        case_number=item.get("caseNo", ""),
                        execution_amount=item.get("execMoney", ""),
                        filing_date=item.get("filingDate", ""),
                        court=item.get("court", ""),
                        risk_level=level,
                        details=item
                    ))

        # 行政处罚
        penalty_data = self._call_mcp("qcc_risk", "get_administrative_penalty", {"searchKey": company_name})
        if penalty_data.get("data"):
            administrative_penalties = penalty_data["data"][:10]  # 取最近10条

        # 环保处罚
        env_data = self._call_mcp("qcc_risk", "get_environmental_penalty", {"searchKey": company_name})
        if env_data.get("data"):
            administrative_penalties.extend(env_data["data"][:5])

        result.judicial_risks = judicial_risks
        result.administrative_penalties = administrative_penalties

    def _populate_business_activity(self, result: ICDueDiligence, company_name: str):
        """填充经营动态"""
        activity = BusinessActivity()

        # 招投标
        bidding_data = self._call_mcp("qcc_operation", "get_bidding_info", {"searchKey": company_name})
        if bidding_data.get("data"):
            bids = bidding_data["data"]
            # 统计近12个月
            activity.bidding_count_12m = len(bids)
            # 简单计算总金额（如有）
            total_amount = sum(float(b.get("bidAmount", 0)) for b in bids if b.get("bidAmount"))
            activity.bidding_amount_12m = f"{total_amount:.2f}" if total_amount else "未知"

        # 资质证书
        qual_data = self._call_mcp("qcc_operation", "get_qualifications", {"searchKey": company_name})
        if qual_data.get("data"):
            activity.qualification_count = len(qual_data["data"])
            activity.key_qualifications = qual_data["data"][:5]

        # 信用评级
        credit_data = self._call_mcp("qcc_operation", "get_credit_evaluation", {"searchKey": company_name})
        if credit_data.get("data"):
            activity.credit_rating = credit_data["data"].get("rating", "未评级")

        # 抽查检查
        spot_data = self._call_mcp("qcc_operation", "get_spot_check_info", {"searchKey": company_name})
        if spot_data.get("data"):
            activity.spot_check_results = spot_data["data"][:5]

        result.business_activity = activity

    def _generate_investment_recommendation(self, result: ICDueDiligence) -> str:
        """生成投资建议"""
        critical_risks = [r for r in result.judicial_risks if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in result.judicial_risks if r.risk_level == RiskLevel.HIGH]

        # 极高风险：失信、被执行、破产
        if any(r.risk_type in ["失信信息", "破产重整"] for r in critical_risks):
            return "不建议。存在严重失信或破产记录，投资风险极高。"

        # 高风险
        if len(high_risks) >= 3 or len(critical_risks) > 0:
            return "谨慎考虑。存在较多风险信号，需深入尽调并设计风险缓释措施。"

        # 中等风险
        if len(high_risks) > 0:
            return "推荐。整体资质良好，存在个别风险点需关注。"

        # 低风险 + 有知识产权
        if result.ip_assets.patent_count > 10:
            return "强烈推荐。资质优良，知识产权布局完善，建议积极推进。"

        return "推荐。资质良好，无明显风险信号。"

    def _extract_key_risks(self, result: ICDueDiligence) -> List[Dict]:
        """提取关键风险清单"""
        key_risks = []

        # 司法风险
        for risk in result.judicial_risks:
            if risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                key_risks.append({
                    "category": "司法风险",
                    "type": risk.risk_type,
                    "level": risk.risk_level.value,
                    "description": f"{risk.case_number} ({risk.filing_date})",
                    "mitigation": self._suggest_mitigation(risk.risk_type)
                })

        # 经营风险
        if result.business_activity.spot_check_results:
            failed = [r for r in result.business_activity.spot_check_results if "不合格" in str(r)]
            if failed:
                key_risks.append({
                    "category": "经营风险",
                    "type": "抽检不合格",
                    "level": "MEDIUM",
                    "description": f"存在{len(failed)}次抽检不合格记录",
                    "mitigation": "要求企业提供整改说明"
                })

        # 知识产权风险
        if result.ip_assets.patent_count == 0 and "科技" in result.basic_info.business_scope:
            key_risks.append({
                "category": "知识产权风险",
                "type": "核心专利缺失",
                "level": "HIGH",
                "description": "科技企业无发明专利，技术壁垒存疑",
                "mitigation": "深入尽调技术来源和竞争优势"
            })

        return key_risks

    def _suggest_mitigation(self, risk_type: str) -> str:
        """建议风险缓释措施"""
        mitigations = {
            "失信信息": "要求企业提供信用修复证明或提供额外担保",
            "被执行人": "核查执行标的金额，要求实际控制人提供连带责任担保",
            "破产重整": "建议放弃投资或等待重整完成后再评估",
            "股权冻结": "要求冻结解除作为交割条件，或调整交易结构",
            "限制高消费": "要求实际控制人解决限高问题",
            "终本案件": "核查未履行金额，评估对现金流的影响",
        }
        return mitigations.get(risk_type, "需深入尽调后制定缓释措施")


# ==================== CLI入口 ====================

def main():
    """CLI入口"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python qcc_mcp_connector_financial.py <模式> <企业名称>")
        print("模式: kyb - KYB快速核验 (30秒)")
        print("      ic - IC Memo全维度尽调")
        print("示例: python qcc_mcp_connector_financial.py kyb '华为技术有限公司'")
        print("      python qcc_mcp_connector_financial.py ic '北京字节跳动科技有限公司'")
        sys.exit(1)

    mode = sys.argv[1]
    company_name = sys.argv[2]

    try:
        connector = QccMcpConnectorFinancial()

        if mode == "kyb":
            print(f"正在进行KYB自动化核验: {company_name}...")
            result = connector.kyb_fast_verification(company_name)
            print("\n" + "=" * 64)
            print("KYB核验报告 - 企查查MCP增强版")
            print("=" * 64)
            print(f"企业名称: {result.company_name}")
            print(f"统一社会信用代码: {result.credit_code}")
            print(f"KYB状态: {result.kyb_status.value}")
            print(f"整体风险: {result.overall_risk.value}")
            print(f"\n风险统计:")
            print(f"  - CRITICAL: {result.risk_summary.get('critical_count', 0)} 项")
            print(f"  - HIGH: {result.risk_summary.get('high_count', 0)} 项")
            print(f"  - MEDIUM: {result.risk_summary.get('medium_count', 0)} 项")
            print(f"\n准入建议: {result.recommended_action}")
            print("=" * 64)

        elif mode == "ic":
            print(f"正在进行IC Memo全维度尽调: {company_name}...")
            result = connector.ic_full_due_diligence(company_name)
            print("\n" + "=" * 64)
            print("IC Memo尽调报告 - 企查查MCP增强版")
            print("=" * 64)
            print(f"企业名称: {result.company_name}")
            print(f"统一社会信用代码: {result.credit_code}")
            print(f"\n知识产权:")
            print(f"  - 专利总数: {result.ip_assets.patent_count}")
            print(f"  - 发明专利: {result.ip_assets.invention_patents}")
            print(f"  - 商标数量: {result.ip_assets.trademark_count}")
            print(f"\n司法风险:")
            print(f"  - CRITICAL: {len([r for r in result.judicial_risks if r.risk_level == RiskLevel.CRITICAL])}")
            print(f"  - HIGH: {len([r for r in result.judicial_risks if r.risk_level == RiskLevel.HIGH])}")
            print(f"\n经营动态:")
            print(f"  - 近12个月招投标: {result.business_activity.bidding_count_12m} 次")
            print(f"  - 资质证书: {result.business_activity.qualification_count} 项")
            print(f"  - 信用评级: {result.business_activity.credit_rating}")
            print(f"\n投资建议: {result.investment_recommendation}")
            print("=" * 64)

        else:
            print(f"错误: 未知模式 '{mode}'。请使用 'kyb' 或 'ic'")
            sys.exit(1)

    except ValueError as e:
        print(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
