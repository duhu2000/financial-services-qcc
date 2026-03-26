"""
KYB Verifier - V2 融合增强版
基于 Manus 版本 + V1 业务逻辑完整实现
支持 A/B/C/D 四级评级和 18类风险扫描
支持 Markdown/Word/PPT 三格式导出
"""
import json
from typing import Dict, List, Any, Tuple, Optional
from .qcc_mcp_client import QccMcpClient
from .report_exporter import ReportExporter


class KYBVerifier:
    """KYB 自动化核验器 - V2 增强版

    4阶段工作流:
    1. 实体锚定 (Entity Verification)
    2. 股权穿透与UBO识别 (Shareholder & UBO Analysis)
    3. 18类风险扫描 (Risk Scanning)
    4. 经营健康度评估 (Operation Health)

    评级规则:
    A级: 正常准入 - 主体合法存续，无明显风险信号
    B级: 审慎准入+加强监测 - 存在中等风险或经营异常
    C级: 需人工复核 - 存在高风险项
    D级: 禁止准入 - 存在关键风险项
    """

    def __init__(self, mcp_config_path: str = "../.mcp.json", output_dir: str = "./reports"):
        self.qcc_client = QccMcpClient(mcp_config_path)
        self.exporter = ReportExporter(output_dir)

    def verify_company(self, company_name: str,
                       credit_code: str = None,
                       user_api_key: str = None,
                       export_format: str = "all") -> Dict:
        """
        执行企业 KYB 自动化核验（30秒快检）
        基于 V1 4阶段工作流 + Manus 技术实现

        :param company_name: 企业名称
        :param credit_code: 统一社会信用代码（可选，用于交叉验证）
        :param user_api_key: 用户API Key（可选）
        :param export_format: 导出格式 (md/docx/pptx/all)
        :return: 完整核验结果，包含导出文件路径
        """
        print(f"\n{'='*60}")
        print(f"[KYBVerifier] 开始企业 KYB 自动化核验")
        print(f"{'='*60}")
        print(f"目标企业: {company_name}")
        if credit_code:
            print(f"统一社会信用代码: {credit_code}")
        print(f"{'='*60}\n")

        results = {
            "company_name": company_name,
            "credit_code": credit_code,
            "status": "未知",
            "kyb_rating": "D",  # A/B/C/D
            "phase_results": {},
            "verification_suggestion": "请人工复核",
            "risk_summary": {},
            "ubo": [],
            "raw_data": {}
        }

        # Phase 1: 实体锚定（5秒）
        print("\n" + "="*60)
        print("[Phase 1] 实体锚定 - 主体信息核验")
        print("="*60)
        entity_data = self._verify_entity(company_name, credit_code, user_api_key)
        results["phase_results"]["entity"] = entity_data

        if entity_data.get("error"):
            results["status"] = "实体锚定失败"
            results["verification_suggestion"] = entity_data["error"]
            return results

        # Phase 2: 股权与受益所有人识别（8秒）
        print("\n" + "="*60)
        print("[Phase 2] 股权穿透与UBO识别")
        print("="*60)
        shareholder_data = self._analyze_shareholders(company_name, user_api_key)
        results["phase_results"]["shareholders"] = shareholder_data
        results["ubo"] = shareholder_data.get("ubo", [])

        # Phase 3: 18类风险全面扫描（15秒）
        print("\n" + "="*60)
        print("[Phase 3] 18类风险全面扫描")
        print("="*60)
        risk_data = self._scan_all_risks(company_name, user_api_key)
        results["phase_results"]["risks"] = risk_data
        results["risk_summary"] = self._summarize_risks(risk_data)

        # Phase 4: 经营健康度与KYB评级（2秒）
        print("\n" + "="*60)
        print("[Phase 4] 经营健康度评估与评级")
        print("="*60)
        operation_data = self._check_operation(company_name, user_api_key)
        results["phase_results"]["operation"] = operation_data

        # 计算 KYB 评级
        print("\n" + "="*60)
        print("[评级计算]")
        print("="*60)
        rating, suggestion = self._calculate_kyb_rating(
            entity_data, risk_data, operation_data
        )
        results["kyb_rating"] = rating
        results["verification_suggestion"] = suggestion
        results["status"] = "核验完成"

        # 导出报告
        if export_format:
            print(f"\n{'='*60}")
            print("[导出] 生成报告文件...")
            print(f"{'='*60}")
            exported_files = self.exporter.export_kyb_report(results, company_name, export_format)
            results["exported_files"] = exported_files

            for fmt, path in exported_files.items():
                if path:
                    print(f"  ✅ {fmt.upper()}: {path}")

        print(f"\n{'='*60}")
        print(f"[KYBVerifier] 核验完成")
        print(f"企业名称: {company_name}")
        print(f"KYB评级: {rating}")
        print(f"核验结论: {suggestion}")
        print(f"{'='*60}\n")

        return results

    def _verify_entity(self, company_name: str, credit_code: str = None,
                       api_key: str = None) -> Dict:
        """Phase 1: 实体锚定 - 核验企业主体信息"""
        print(f"[Phase 1] 查询企业工商注册信息...")

        result = self.qcc_client.call_mcp_service(
            "qcc-company", company_name, api_key
        )

        if result.get("error"):
            print(f"  ❌ 查询失败: {result['error']}")
            return {"error": f"实体锚定失败: {result['error']}"}

        data = result.get("data", [])
        if not data:
            print(f"  ❌ 未找到企业主体信息")
            return {"error": "未找到企业主体信息，请核实企业名称"}

        # 提取第一个匹配的公司信息
        main_info = data[0] if isinstance(data, list) else data

        # 基础信息提取
        entity_info = {
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
            "联系电话": main_info.get("Phone"),
            "邮箱": main_info.get("Email"),
        }

        print(f"  ✅ 实体锚定成功")
        print(f"     企业名称: {entity_info['注册名称']}")
        print(f"     统一社会信用代码: {entity_info['统一社会信用代码']}")
        print(f"     法定代表人: {entity_info['法定代表人']}")
        print(f"     经营状态: {entity_info['经营状态']}")

        # 信用代码交叉验证（如果提供）
        if credit_code and entity_info.get("统一社会信用代码"):
            if credit_code != entity_info["统一社会信用代码"]:
                print(f"  ⚠️ 信用代码不匹配: 提供[{credit_code}] vs 查询[{entity_info['统一社会信用代码']}]")
                return {
                    "error": f"统一社会信用代码不匹配。提供:{credit_code}, 查询:{entity_info['统一社会信用代码']}",
                    "entity_info": entity_info
                }

        return {
            "success": True,
            "entity_info": entity_info,
            "raw_data": main_info
        }

    def _analyze_shareholders(self, company_name: str, api_key: str = None) -> Dict:
        """Phase 2: 股权穿透与UBO识别"""
        print(f"[Phase 2] 查询股东信息与股权结构...")

        # 获取股东信息
        shareholder_result = self.qcc_client.call_mcp_service(
            "qcc-company", company_name, api_key
        )

        shareholders = []
        ubo_list = []

        if not shareholder_result.get("error"):
            data = shareholder_result.get("data", [])
            raw_shareholders = data[0].get("Partners", []) if isinstance(data, list) and data else []

            for s in raw_shareholders:
                shareholder = {
                    "名称": s.get("StockName"),
                    "持股比例": s.get("StockRate"),
                    "认缴出资额": s.get("ShouldCapi"),
                    "实缴出资额": s.get("RealCapi"),
                    "股东类型": s.get("StockType")
                }
                shareholders.append(shareholder)

                # UBO识别: 自然人股东持股25%以上
                rate_str = s.get("StockRate", "0%").replace("%", "")
                try:
                    rate = float(rate_str)
                    if rate >= 25 and s.get("StockType") == "自然人股东":
                        ubo_list.append({
                            "名称": s.get("StockName"),
                            "持股比例": s.get("StockRate"),
                            "识别依据": "自然人股东持股≥25%"
                        })
                except ValueError:
                    pass

        print(f"  ✅ 股东数量: {len(shareholders)}")
        print(f"  ✅ 识别UBO: {len(ubo_list)} 人")
        for ubo in ubo_list:
            print(f"     - {ubo['名称']}: {ubo['持股比例']}")

        return {
            "shareholders": shareholders,
            "ubo": ubo_list,
            "external_investments": []
        }

    def _scan_all_risks(self, company_name: str, api_key: str = None) -> Dict:
        """
        Phase 3: 18类风险全面扫描
        V2: 完整风险分类与优先级
        """
        print(f"[Phase 3] 启动18类风险扫描...")

        # CRITICAL 级风险（<4小时响应）
        critical_risks = {
            "失信信息": "get_dishonest_info",
            "被执行人": "get_executed_person_info",
            "限制高消费": "get_high_consumption_restriction",
            "破产重整": "get_bankruptcy_reorganization",
            "股权冻结": "get_equity_freeze",
            "司法协助": "get_judgment_debtor_info",
        }

        # HIGH 级风险（<24小时响应）
        high_risks = {
            "经营异常": "get_business_exception",
            "严重违法": "get_serious_violation",
            "行政处罚": "get_administrative_penalty",
            "环保处罚": "get_environmental_penalty",
        }

        # MEDIUM 级风险
        medium_risks = {
            "股权出质": "get_equity_pledge",
            "动产抵押": "get_chattel_mortgage",
            "欠税公告": "get_tax_arrears_notice",
            "税务非正常": "get_abnormal_tax",
            "税收违法": "get_tax_violation",
        }

        # LOW 级风险
        low_risks = {
            "涉诉信息": "get_lawsuit_info",
            "裁判文书": "get_judicial_document",
        }

        # 调用风险扫描服务
        risk_result = self.qcc_client.call_mcp_service(
            "qcc-risk", company_name, api_key
        )

        if risk_result.get("error"):
            print(f"  ⚠️ 风险扫描服务调用失败: {risk_result['error']}")
            return {"error": risk_result['error']}

        # 解析风险数据
        risks_found = {
            "critical": {},
            "high": {},
            "medium": {},
            "low": {}
        }

        raw_data = risk_result.get("data", {})

        # 根据实际返回结构解析风险
        # 这里假设返回的是聚合的风险数据
        if isinstance(raw_data, dict):
            # CRITICAL风险检测
            for risk_name, tool in critical_risks.items():
                count = raw_data.get(f"{tool}_count", 0)
                if count > 0:
                    risks_found["critical"][risk_name] = {
                        "count": count,
                        "details": raw_data.get(tool, [])
                    }

            # HIGH风险检测
            for risk_name, tool in high_risks.items():
                count = raw_data.get(f"{tool}_count", 0)
                if count > 0:
                    risks_found["high"][risk_name] = {
                        "count": count,
                        "details": raw_data.get(tool, [])
                    }

            # MEDIUM风险检测
            for risk_name, tool in medium_risks.items():
                count = raw_data.get(f"{tool}_count", 0)
                if count > 0:
                    risks_found["medium"][risk_name] = {
                        "count": count,
                        "details": raw_data.get(tool, [])
                    }

            # LOW风险检测
            for risk_name, tool in low_risks.items():
                count = raw_data.get(f"{tool}_count", 0)
                if count > 0:
                    risks_found["low"][risk_name] = {
                        "count": count,
                        "details": raw_data.get(tool, [])
                    }

        # 打印风险摘要
        critical_count = len(risks_found["critical"])
        high_count = len(risks_found["high"])
        medium_count = len(risks_found["medium"])
        low_count = len(risks_found["low"])

        print(f"  ✅ 风险扫描完成")
        print(f"     🔴 关键风险: {critical_count} 项")
        if critical_count > 0:
            for risk in risks_found["critical"]:
                print(f"        - {risk}")
        print(f"     🟠 高风险: {high_count} 项")
        if high_count > 0:
            for risk in risks_found["high"]:
                print(f"        - {risk}")
        print(f"     🟡 中风险: {medium_count} 项")
        print(f"     🔵 低风险: {low_count} 项")

        return {
            "critical": risks_found["critical"],
            "high": risks_found["high"],
            "medium": risks_found["medium"],
            "low": risks_found["low"],
            "raw_data": raw_data
        }

    def _check_operation(self, company_name: str, api_key: str = None) -> Dict:
        """Phase 4: 经营健康度评估"""
        print(f"[Phase 4] 查询经营健康度信息...")

        # 获取经营相关数据
        operation_result = self.qcc_client.call_mcp_service(
            "qcc-operation", company_name, api_key
        )

        operation_info = {
            "招投标数量": 0,
            "资质证书数量": 0,
            "舆情信号": "正常"
        }

        if not operation_result.get("error"):
            data = operation_result.get("data", {})
            # 解析经营数据
            if isinstance(data, dict):
                operation_info["招投标数量"] = len(data.get("bidding", []))
                operation_info["资质证书数量"] = len(data.get("qualifications", []))

        print(f"  ✅ 经营健康度信息获取完成")
        print(f"     招投标数量: {operation_info['招投标数量']}")
        print(f"     资质证书: {operation_info['资质证书数量']}")

        return operation_info

    def _summarize_risks(self, risk_data: Dict) -> Dict:
        """V2 增强：风险摘要统计"""
        summary = {
            "critical_count": len(risk_data.get("critical", {})),
            "high_count": len(risk_data.get("high", {})),
            "medium_count": len(risk_data.get("medium", {})),
            "low_count": len(risk_data.get("low", {})),
            "total_count": 0,
            "risk_items": []
        }

        # 收集所有风险项
        for level in ["critical", "high", "medium", "low"]:
            items = risk_data.get(level, {})
            if isinstance(items, dict):
                for risk_name in items:
                    summary["risk_items"].append(f"{level.upper()}:{risk_name}")

        summary["total_count"] = (
            summary["critical_count"] +
            summary["high_count"] +
            summary["medium_count"] +
            summary["low_count"]
        )

        return summary

    def _calculate_kyb_rating(self, entity_data: Dict,
                              risk_data: Dict,
                              operation_data: Dict) -> Tuple[str, str]:
        """
        V2 增强：A/B/C/D 评级计算

        评级标准:
        A级: 正常准入 - 无关键/高风险，经营状态正常
        B级: 审慎准入+加强监测 - 存在中等风险或经营异常
        C级: 需人工复核 - 存在高风险项
        D级: 禁止准入 - 存在关键风险项
        """
        # 获取实体信息
        entity_info = entity_data.get("entity_info", {})
        status = entity_info.get("经营状态", "")

        # 获取风险统计
        critical_risks = risk_data.get("critical", {})
        high_risks = risk_data.get("high", {})
        medium_risks = risk_data.get("medium", {})

        # D级：存在 CRITICAL 风险
        if critical_risks:
            risk_list = ", ".join(critical_risks.keys())
            return "D", f"🔴 禁止准入 - 存在关键风险: {risk_list}。建议立即启动风险预警流程，终止业务办理。"

        # C级：存在 HIGH 风险
        if high_risks:
            risk_list = ", ".join(high_risks.keys())
            return "C", f"🟠 需人工复核 - 存在高风险: {risk_list}。建议加强尽调，提交风险管理部门审批。"

        # B级：存在 MEDIUM 风险或经营状态异常
        if medium_risks:
            risk_list = ", ".join(medium_risks.keys())
            return "B", f"🟡 审慎准入+加强监测 - 存在中等风险: {risk_list}。建议增加监测频率，定期复核。"

        # 检查经营状态
        if status and status not in ["存续", "在业", "开业", "正常"]:
            return "B", f"🟡 审慎准入 - 企业经营状态异常: {status}。建议核实经营状态后再办理。"

        # A级：无风险
        return "A", "🟢 正常准入 - 主体合法存续，无明显风险信号，可按标准流程处理。"
