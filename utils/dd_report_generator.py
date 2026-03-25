"""
Due Diligence Report Generator - V2 融合增强版
基于 Manus 版本 + V1 7章尽调结构
"""
import json
from typing import Dict, List, Any
from .qcc_mcp_client import QccMcpClient


class DDReportGenerator:
    """投融资尽调报告生成器 - V2 增强版

    生成标准化投资委员会备忘录(IC Memo)，包含7章结构:
    1. 执行摘要 (Executive Summary)
    2. 公司概况与股权结构 (Company Overview & Equity)
    3. 知识产权与核心竞争力 (IP & Core Competence)
    4. 法律与合规风险 (Legal & Compliance)
    5. 经营与市场分析 (Operation & Market)
    6. 财务分析 (Financial Analysis)
    7. 投资建议与风险提示 (Investment Recommendation)
    """

    def __init__(self, mcp_config_path="../.mcp.json"):
        self.qcc_client = QccMcpClient(mcp_config_path)

    def generate_full_dd_profile(self, company_name: str,
                                  user_api_key: str = None,
                                  investment_round: str = None,
                                  sector: str = None) -> dict:
        """
        生成投融资标的全维度背调报告

        :param company_name: 目标公司名称
        :param user_api_key: 用户提供的企查查 API Key
        :param investment_round: 投资轮次（可选）
        :param sector: 行业领域（可选）
        :return: 全维度背调报告字典
        """
        print(f"\n{'='*60}")
        print(f"[DDReportGenerator] 开始生成尽调报告")
        print(f"{'='*60}")
        print(f"目标公司: {company_name}")
        if investment_round:
            print(f"投资轮次: {investment_round}")
        if sector:
            print(f"行业领域: {sector}")
        print(f"{'='*60}\n")

        report = {
            "company_name": company_name,
            "investment_round": investment_round,
            "sector": sector,
            "status": "生成中",
            "generated_at": None,
            "chapters": {
                "chapter_1_executive_summary": {},
                "chapter_2_company_overview": {},
                "chapter_3_intellectual_property": {},
                "chapter_4_legal_compliance": {},
                "chapter_5_operation_market": {},
                "chapter_6_financial_analysis": {},
                "chapter_7_investment_recommendation": {}
            },
            "summary": "",
            "qcc_raw_data": {}
        }

        # Chapter 2: 公司概况与股权结构
        print("\n" + "="*60)
        print("[Chapter 2] 公司概况与股权结构")
        print("="*60)
        report["chapters"]["chapter_2_company_overview"] = \
            self._chapter_2_company_overview(company_name, user_api_key)

        # Chapter 3: 知识产权与核心竞争力
        print("\n" + "="*60")
        print("[Chapter 3] 知识产权与核心竞争力")
        print("="*60)
        report["chapters"]["chapter_3_intellectual_property"] = \
            self._chapter_3_intellectual_property(company_name, user_api_key)

        # Chapter 4: 法律与合规风险
        print("\n" + "="*60)
        print("[Chapter 4] 法律与合规风险")
        print("="*60)
        report["chapters"]["chapter_4_legal_compliance"] = \
            self._chapter_4_legal_compliance(company_name, user_api_key)

        # Chapter 5: 经营与市场分析
        print("\n" + "="*60)
        print("[Chapter 5] 经营与市场分析")
        print("="*60)
        report["chapters"]["chapter_5_operation_market"] = \
            self._chapter_5_operation_market(company_name, user_api_key)

        # Chapter 1: 执行摘要（基于前面章节生成）
        print("\n" + "="*60)
        print("[Chapter 1] 执行摘要")
        print("="*60)
        report["chapters"]["chapter_1_executive_summary"] = \
            self._chapter_1_executive_summary(report["chapters"])

        # Chapter 6: 财务分析（占位，需要外部数据）
        report["chapters"]["chapter_6_financial_analysis"] = {
            "note": "财务分析需要目标公司提供财务报表或使用第三方财务数据服务",
            "recommendation": "建议要求目标公司提供近3年审计报告及最新财务报表"
        }

        # Chapter 7: 投资建议与风险提示
        print("\n" + "="*60)
        print("[Chapter 7] 投资建议与风险提示")
        print("="*60)
        report["chapters"]["chapter_7_investment_recommendation"] = \
            self._chapter_7_investment_recommendation(report["chapters"])

        # 生成总结
        report["summary"] = self._generate_executive_summary(report)
        report["status"] = "完成"
        report["generated_at"] = self._get_timestamp()

        print(f"\n{'='*60}")
        print(f"[DDReportGenerator] 尽调报告生成完成")
        print(f"{'='*60}\n")

        return report

    def _chapter_1_executive_summary(self, chapters: Dict) -> Dict:
        """Chapter 1: 执行摘要"""
        company_overview = chapters.get("chapter_2_company_overview", {})
        legal_compliance = chapters.get("chapter_4_legal_compliance", {})
        ip_data = chapters.get("chapter_3_intellectual_property", {})

        basic_info = company_overview.get("basic_info", {})
        risk_summary = legal_compliance.get("risk_summary", {})

        highlights = []
        concerns = []

        # 亮点
        if basic_info.get("成立日期"):
            highlights.append(f"企业成立于{basic_info['成立日期']}，经营历史清晰")
        if ip_data.get("专利数量", 0) > 0:
            highlights.append(f"拥有{ip_data['专利数量']}项专利，具备一定技术壁垒")
        if ip_data.get("商标数量", 0) > 0:
            highlights.append(f"注册商标{ip_data['商标数量']}件，品牌建设有基础")

        # 关注点
        critical_count = risk_summary.get("critical_count", 0)
        high_count = risk_summary.get("high_count", 0)
        if critical_count > 0:
            concerns.append(f"存在{critical_count}项关键风险，需重点关注")
        if high_count > 0:
            concerns.append(f"存在{high_count}项高风险，需尽职调查")

        print(f"  ✅ 执行摘要生成完成")
        print(f"     亮点: {len(highlights)} 项")
        print(f"     关注点: {len(concerns)} 项")

        return {
            "highlights": highlights,
            "concerns": concerns,
            "investment_thesis": "",
            "key_metrics": {
                "注册资本": basic_info.get("注册资本"),
                "经营状态": basic_info.get("经营状态"),
                "专利数量": ip_data.get("专利数量", 0),
                "关键风险数": critical_count,
                "高风险数": high_count
            }
        }

    def _chapter_2_company_overview(self, company_name: str, api_key: str = None) -> Dict:
        """Chapter 2: 公司概况与股权结构"""
        print("[Chapter 2] 获取公司基本信息...")

        basic_info_res = self.qcc_client.call_mcp_service(
            "qcc-company", company_name, api_key
        )

        basic_info = {}
        shareholder_data = []

        if not basic_info_res.get("error"):
            data = basic_info_res.get("data", [])
            if data:
                main_info = data[0] if isinstance(data, list) else data
                basic_info = {
                    "注册名称": main_info.get("Name"),
                    "统一社会信用代码": main_info.get("CreditCode"),
                    "法定代表人": main_info.get("LegalPersonName"),
                    "注册资本": main_info.get("RegistCapi"),
                    "实缴资本": main_info.get("RecCap"),
                    "经营状态": main_info.get("Status"),
                    "成立日期": main_info.get("StartDate"),
                    "企业类型": main_info.get("EconKind"),
                    "经营范围": main_info.get("Scope"),
                    "注册地址": main_info.get("Address"),
                }
                shareholder_data = main_info.get("Partners", [])

        # 股权穿透分析
        shareholders = []
        ubo_list = []
        for s in shareholder_data:
            shareholder = {
                "名称": s.get("StockName"),
                "持股比例": s.get("StockRate"),
                "认缴出资额": s.get("ShouldCapi"),
                "股东类型": s.get("StockType")
            }
            shareholders.append(shareholder)

            # UBO识别
            rate_str = s.get("StockRate", "0%").replace("%", "")
            try:
                rate = float(rate_str)
                if rate >= 25 and s.get("StockType") == "自然人股东":
                    ubo_list.append({
                        "名称": s.get("StockName"),
                        "持股比例": s.get("StockRate")
                    })
            except ValueError:
                pass

        print(f"  ✅ 公司基本信息获取完成")
        print(f"     企业名称: {basic_info.get('注册名称')}")
        print(f"     股东数量: {len(shareholders)}")
        print(f"     UBO识别: {len(ubo_list)} 人")

        return {
            "basic_info": basic_info,
            "shareholders": shareholders,
            "ubo": ubo_list,
            "equity_analysis": {
                "股权集中度": "待分析",
                "实际控制人": ubo_list[0] if ubo_list else None
            }
        }

    def _chapter_3_intellectual_property(self, company_name: str, api_key: str = None) -> Dict:
        """Chapter 3: 知识产权与核心竞争力"""
        print("[Chapter 3] 获取知识产权信息...")

        # 分别获取专利、商标、著作权
        patent_res = self.qcc_client.call_mcp_service(
            "qcc-ipr", company_name, api_key
        )

        patents = []
        trademarks = []
        software_copyrights = []
        work_copyrights = []

        if not patent_res.get("error"):
            data = patent_res.get("data", {})
            if isinstance(data, dict):
                patents = data.get("patents", [])
                trademarks = data.get("trademarks", [])
                software_copyrights = data.get("software_copyrights", [])
                work_copyrights = data.get("work_copyrights", [])

        # 核心技术评估
        core_patents = [p for p in patents if p.get("Type") == "发明"]

        print(f"  ✅ 知识产权信息获取完成")
        print(f"     专利: {len(patents)} 项 (发明{len(core_patents)}项)")
        print(f"     商标: {len(trademarks)} 件")
        print(f"     软件著作权: {len(software_copyrights)} 项")

        return {
            "专利数量": len(patents),
            "发明专利": len(core_patents),
            "实用新型": len([p for p in patents if p.get("Type") == "实用新型"]),
            "外观设计": len([p for p in patents if p.get("Type") == "外观设计"]),
            "专利列表": [p.get("Title") for p in patents],
            "商标数量": len(trademarks),
            "商标列表": [t.get("Name") for t in trademarks],
            "软件著作权数量": len(software_copyrights),
            "作品著作权数量": len(work_copyrights),
            "core_assessment": {
                "技术壁垒": "高" if len(core_patents) >= 5 else "中" if len(core_patents) >= 1 else "低",
                "品牌保护": "良好" if len(trademarks) >= 3 else "一般"
            }
        }

    def _chapter_4_legal_compliance(self, company_name: str, api_key: str = None) -> Dict:
        """Chapter 4: 法律与合规风险"""
        print("[Chapter 4] 扫描法律合规风险...")

        risk_res = self.qcc_client.call_mcp_service(
            "qcc-risk", company_name, api_key
        )

        risks = {
            "critical": {},
            "high": {},
            "medium": {},
            "low": {}
        }

        if not risk_res.get("error"):
            data = risk_res.get("data", {})
            if isinstance(data, dict):
                # 解析风险数据
                critical_items = ["dishonest", "executed", "bankruptcy", "equity_freeze"]
                high_items = ["business_exception", "serious_violation", "administrative_penalty"]

                for item in critical_items:
                    if data.get(f"{item}_count", 0) > 0:
                        risks["critical"][item] = data.get(f"{item}_count", 0)

                for item in high_items:
                    if data.get(f"{item}_count", 0) > 0:
                        risks["high"][item] = data.get(f"{item}_count", 0)

        # 风险统计
        critical_count = len(risks["critical"])
        high_count = len(risks["high"])
        total_risks = critical_count + high_count + len(risks["medium"]) + len(risks["low"])

        # 合规结论
        if critical_count > 0:
            compliance_conclusion = "存在关键法律风险，建议审慎评估"
        elif high_count > 0:
            compliance_conclusion = "存在合规风险，需加强尽调"
        else:
            compliance_conclusion = "合规状况良好"

        print(f"  ✅ 法律风险扫描完成")
        print(f"     关键风险: {critical_count} 项")
        print(f"     高风险: {high_count} 项")
        print(f"     合规结论: {compliance_conclusion}")

        return {
            "risks": risks,
            "risk_summary": {
                "critical_count": critical_count,
                "high_count": high_count,
                "total_risks": total_risks
            },
            "compliance_conclusion": compliance_conclusion,
            "lawsuits": [],
            "judicial_documents": []
        }

    def _chapter_5_operation_market(self, company_name: str, api_key: str = None) -> Dict:
        """Chapter 5: 经营与市场分析"""
        print("[Chapter 5] 获取经营市场信息...")

        operation_res = self.qcc_client.call_mcp_service(
            "qcc-operation", company_name, api_key
        )

        bidding_count = 0
        qualifications = []
        news_sentiment = "正常"

        if not operation_res.get("error"):
            data = operation_res.get("data", {})
            if isinstance(data, dict):
                bidding = data.get("bidding", [])
                bidding_count = len(bidding)
                qualifications = data.get("qualifications", [])

        # 业务活跃度评估
        activity_level = "高" if bidding_count >= 10 else "中" if bidding_count >= 3 else "低"

        print(f"  ✅ 经营市场信息获取完成")
        print(f"     招投标数量: {bidding_count}")
        print(f"     资质证书: {len(qualifications)} 项")
        print(f"     业务活跃度: {activity_level}")

        return {
            "bidding_activity": {
                "count": bidding_count,
                "level": activity_level
            },
            "qualifications": [
                {"名称": q.get("Name"), "状态": q.get("Status")}
                for q in qualifications
            ],
            "news_sentiment": news_sentiment,
            "market_position": "待进一步调研"
        }

    def _chapter_7_investment_recommendation(self, chapters: Dict) -> Dict:
        """Chapter 7: 投资建议与风险提示"""
        legal_compliance = chapters.get("chapter_4_legal_compliance", {})
        company_overview = chapters.get("chapter_2_company_overview", {})

        risk_summary = legal_compliance.get("risk_summary", {})
        critical_count = risk_summary.get("critical_count", 0)
        high_count = risk_summary.get("high_count", 0)

        # 投资建议
        if critical_count > 0:
            recommendation = "建议暂缓投资，待关键风险消除后再评估"
            risk_level = "高"
        elif high_count > 0:
            recommendation = "建议谨慎投资，需充分尽调并设置保护性条款"
            risk_level = "中高"
        else:
            recommendation = "建议推进投资，按标准流程执行"
            risk_level = "中"

        # 关键风险提示
        key_risks = []
        if critical_count > 0:
            key_risks.append("存在关键法律风险，可能影响投资安全")
        if high_count > 0:
            key_risks.append("存在合规风险，需持续关注")

        print(f"  ✅ 投资建议生成完成")
        print(f"     风险等级: {risk_level}")
        print(f"     投资建议: {recommendation}")

        return {
            "investment_recommendation": recommendation,
            "risk_level": risk_level,
            "key_risks": key_risks,
            "recommended_terms": [
                "建议在投资协议中加入关键风险披露条款",
                "建议设置分期投资，根据风险整改进度释放后续资金"
            ],
            "post_investment_monitoring": [
                "定期跟踪企业风险变化",
                "关注关键风险整改进展"
            ]
        }

    def _generate_executive_summary(self, report: Dict) -> str:
        """生成执行摘要文本"""
        chapters = report.get("chapters", {})
        company_name = report.get("company_name", "")

        ch2 = chapters.get("chapter_2_company_overview", {})
        ch3 = chapters.get("chapter_3_intellectual_property", {})
        ch4 = chapters.get("chapter_4_legal_compliance", {})
        ch7 = chapters.get("chapter_7_investment_recommendation", {})

        basic_info = ch2.get("basic_info", {})
        risk_summary = ch4.get("risk_summary", {})

        parts = [
            f"## 尽调对象：{company_name}",
            "",
            "### 公司概况",
            f"- 注册名称：{basic_info.get('注册名称', 'N/A')}",
            f"- 法定代表人：{basic_info.get('法定代表人', 'N/A')}",
            f"- 注册资本：{basic_info.get('注册资本', 'N/A')}",
            f"- 成立日期：{basic_info.get('成立日期', 'N/A')}",
            f"- 经营状态：{basic_info.get('经营状态', 'N/A')}",
            "",
            "### 知识产权",
            f"- 专利数量：{ch3.get('专利数量', 0)} 项（发明{ch3.get('发明专利', 0)}项）",
            f"- 商标数量：{ch3.get('商标数量', 0)} 件",
            "",
            "### 法律风险",
            f"- 关键风险：{risk_summary.get('critical_count', 0)} 项",
            f"- 高风险：{risk_summary.get('high_count', 0)} 项",
            f"- 合规结论：{ch4.get('compliance_conclusion', 'N/A')}",
            "",
            "### 投资建议",
            f"- 风险等级：{ch7.get('risk_level', 'N/A')}",
            f"- 投资建议：{ch7.get('investment_recommendation', 'N/A')}",
        ]

        return "\n".join(parts)

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
