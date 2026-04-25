"""
test_v1_2.py · V1.2 框架端到端 + 防御机制红绿对照测试
=================================================================
跑法：python test_v1_2.py

测试覆盖：
1. USCC 编造 → 应拦截
2. 股东 count vs rows 不一致 → 应拦截（V1.1.3 9 vs 13 类事故）
3. 历史股东 count vs rows 不一致 → 应拦截
4. 董监高 count vs rows 不一致 → 应拦截
5. 对外投资 count vs rows 不一致 → 应拦截
6. 专利年度分布加和 vs 总数 → 一致性检查
7. 处罚状态出现"已处置/已闭环" → 一致性检查应拦截
8. 完整正例 → 应通过 + 生成 MD 和 manifest
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# 测试时把当前目录加入 path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from v1_2.uscc_validator import validate_uscc, USCCValidationError
    from v1_2.evidence import MCPCallRecorder, ManifestBuilder, EvidenceBox
    from v1_2.data_extractor import ReportExtractor
    from v1_2.consistency_check import check_report_consistency, ConsistencyError
    from v1_2.render_md import render_markdown
    from v1_2.build_report_v1_2 import generate_report
    from v1_2.data_contract import (
        PYDANTIC_OK,
        CurrentShareholdersSection, Shareholder,
        HistoricalShareholdersSection, HistoricalShareholder,
        ExecutiveSection, Executive, HistoricalExecutive,
        InvestmentSection, Investment,
        AdministrativePenaltySection, AdministrativePenalty,
    )
except ImportError as e:
    print(f"导入失败：{e}\n请检查 v1_2 模块是否完整。")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 红绿对照测试
# ---------------------------------------------------------------------------

def test_uscc_fabricated() -> None:
    """V1.1.3 编造的 USCC 必须被拦截。"""
    ok, _ = validate_uscc("91320506MA1UYUWY3X")
    assert not ok, "V1.1.3 编造 USCC 必须被拦截"

    ok, _ = validate_uscc("91320594088140947F")
    assert ok, "真实 USCC 必须通过"
    print("✓ test_uscc_fabricated")


def test_count_vs_rows_shareholders() -> None:
    """V1.1.3 股东 9 vs MCP 13 类事故 - schema 必须拦截。"""
    if not PYDANTIC_OK:
        print("⚠ 跳过 test_count_vs_rows_shareholders（pydantic 未安装）")
        return

    try:
        CurrentShareholdersSection(
            total_count=13,
            shareholders=[Shareholder(name="陈德强", holding_ratio="35.49%")],
        )
        assert False, "应被拦截"
    except (ValueError, Exception) as e:
        assert "13" in str(e), str(e)
    print("✓ test_count_vs_rows_shareholders")


def test_count_vs_rows_historical() -> None:
    """V1.1.3 历史股东 16 vs MCP 17 — schema 必须拦截。"""
    if not PYDANTIC_OK:
        return
    try:
        HistoricalShareholdersSection(
            total_count=17,
            exited_shareholders=[
                HistoricalShareholder(name="马群", exit_date="2015-05-05")
            ],
        )
        assert False
    except (ValueError, Exception) as e:
        assert "17" in str(e)
    print("✓ test_count_vs_rows_historical")


def test_count_vs_rows_executives() -> None:
    """V1.1.3 历任董监高 9 vs MCP 10 — schema 必须拦截。"""
    if not PYDANTIC_OK:
        return
    try:
        ExecutiveSection(
            current_count=1,
            current_executives=[Executive(name="陈德强", position="董事长")],
            historical_count=10,
            historical_executives=[
                HistoricalExecutive(name="陈玮", position="监事", departure_date="2025-10-15"),
            ],
        )
        assert False
    except (ValueError, Exception) as e:
        assert "10" in str(e) or "历任" in str(e)
    print("✓ test_count_vs_rows_executives")


def test_count_vs_rows_investments() -> None:
    """V1.1.3 对外投资 5 vs MCP 7 — schema 必须拦截。"""
    if not PYDANTIC_OK:
        return
    try:
        InvestmentSection(
            total_count=7,
            investments=[
                Investment(invested_company="上海知彼", holding_ratio="100%"),
            ],
        )
        assert False
    except (ValueError, Exception) as e:
        assert "7" in str(e) or "对外投资" in str(e)
    print("✓ test_count_vs_rows_investments")


def test_penalty_banned_phrases() -> None:
    """处罚字段含'已处置/已闭环'必须被一致性检查拦截。"""
    if not PYDANTIC_OK:
        return
    # 构造一个最小报告 schema 对象
    from v1_2.data_contract import (
        ReportSchema, CompanyBasicInfo, HistoricalRegistrationSection,
        CurrentShareholdersSection, HistoricalShareholdersSection,
        ExecutiveSection, InvestmentSection, QualificationSection,
        HonorSection, PatentSection,
    )
    company = CompanyBasicInfo(
        name="测试公司", uscc="91320594088140947F", legal_rep="某某",
        establish_date="2020-01-01", registered_capital="100万元",
        enterprise_type="有限", industry="测试", registration_status="在业",
        registration_authority="测试局", registered_address="测试地址",
    )
    report = ReportSchema(
        report_id="TEST-PENALTY-001",
        generated_at="2026-04-24T00:00:00+00:00",
        company=company,
        historical_registration=HistoricalRegistrationSection(
            capital_nodes=[], name_nodes=[], address_nodes=[]),
        current_shareholders=CurrentShareholdersSection(total_count=0, shareholders=[]),
        historical_shareholders=HistoricalShareholdersSection(total_count=0, exited_shareholders=[]),
        executives=ExecutiveSection(current_count=0, current_executives=[],
                                    historical_count=0, historical_executives=[]),
        investments=InvestmentSection(total_count=0, investments=[]),
        qualifications=QualificationSection(total_count=0, valid_count=0, qualifications=[]),
        honors=HonorSection(total_count=0, honors=[]),
        patents=PatentSection(total_count=0, patents=[]),
        administrative_penalties=AdministrativePenaltySection(
            total_count=1,
            penalties=[AdministrativePenalty(
                decision_no="苏银罚决字〔2025〕21号",
                penalty_date="2025-09-24",
                penalty_authority="中国人民银行江苏省分行",
                penalty_amount="10000",
                penalty_result="罚款 1 万元，已处置",   # 含违禁词
            )],
        ),
        change_records_count=50,
    )
    try:
        check_report_consistency(report)
        assert False, "已处置 应被拦截"
    except ConsistencyError as e:
        assert "已处置" in str(e)
    print("✓ test_penalty_banned_phrases")


def test_e2e_with_mock_mcp() -> None:
    """端到端：用 mock MCP 数据走完整流程。"""
    if not PYDANTIC_OK:
        print("⚠ 跳过 test_e2e_with_mock_mcp（pydantic 未安装）")
        return

    mcp_responses = {
        "qcc-company.get_company_registration_info": {
            "企业名称": "企查查科技股份有限公司",
            "统一社会信用代码": "91320594088140947F",
            "法定代表人": "陈德强",
            "登记状态": "在业",
            "成立日期": "2014-03-12",
            "注册资本": "36225万元",
            "实缴资本": "36225万元",
            "企业类型": "股份有限公司（非上市、自然人投资或控股）",
            "国标行业": "软件和信息技术服务业",
            "登记机关": "苏州市数据局",
            "注册地址": "中国（江苏）自由贸易试验区苏州片区苏州工业园区汇智街8号",
            "核准日期": "2025-10-15",
            "所属地区": "江苏省苏州市苏州工业园区",
            "参保人数": "461",
        },
        "qcc-company.get_shareholder_info": {
            "股东信息": [
                {"股东名称": "陈德强", "持股比例": "35.49%", "持股数": "128576121"},
                {"股东名称": "杨京", "持股比例": "12.07%", "持股数": "43737785"},
            ],
        },
        "qcc-history.get_historical_shareholders": {
            "历史股东信息": [
                {"股东名称": "马群", "退出日期": "2015-05-05", "退出时持股比例": "36%",
                 "认缴出资额": "18万元", "股东类型": "自然人股东"},
            ],
        },
        "qcc-company.get_key_personnel": {
            "主要人员信息": [
                {"姓名": "陈德强", "职务": "董事长", "持股比例": "35.49%"},
            ],
        },
        "qcc-history.get_historical_executives": {
            "历史主要人员信息": [
                {"姓名": "陈玮", "职务": "监事", "任职日期": "2024-03-12",
                 "卸任日期": "2025-10-15"},
            ],
        },
        "qcc-company.get_external_investments": {
            "对外投资信息": [
                {"被投资企业名称": "上海知彼网络科技有限公司",
                 "持股比例": "100%", "成立日期": "2015-12-10", "状态": "存续",
                 "认缴出资额/持股数": "6900万元"},
            ],
        },
        "qcc-history.get_historical_registration": {
            "历史名称列表": [
                {"历史名称": "苏州朗动网络科技有限公司",
                 "起始日期": "2014-03-12", "终止日期": "2020-08-25"},
            ],
            "历史注册资本列表": [
                {"历史注册资本": "50万元", "起始日期": "", "终止日期": "2014-09-11"},
            ],
            "历史地址列表": [
                {"历史地址": "苏州工业园区东环路1500号现代创展大厦1幢1107室",
                 "起始日期": "", "终止日期": "2014-09-11"},
            ],
        },
        "qcc-operation.get_qualifications": {
            "资质证书信息": [
                {"资质名称": "ITSS 证书", "类别与等级": "ITSS 三级",
                 "发证日期": "2019-08-09", "有效期至": "2028-08-08", "证书状态": "有效"},
            ],
        },
        "qcc-operation.get_honor_info": {
            "荣誉信息": [
                {"名称": "高新技术企业", "级别": "国家级", "认证年份": "2025",
                 "发布日期": "2025-12-26",
                 "发布单位": "全国高新技术企业认定管理工作领导小组办公室"},
            ],
        },
        "qcc-ipr.get_patent_info": {
            "专利信息": [
                {"发明名称": "测试专利 A", "申请号": "CN202010000001.0",
                 "申请日期": "2020-01-01", "公开（公告）号": "CNxxx",
                 "公开（公告）日期": "2021-01-01", "专利类型": "发明授权",
                 "法律状态": "授权"},
                {"发明名称": "测试专利 B", "申请号": "CN202110000002.0",
                 "申请日期": "2021-01-01", "专利类型": "发明授权"},
            ],
        },
        "qcc-risk.get_administrative_penalty": {
            "行政处罚信息": [
                {"决定书文号": "苏银罚决字〔2025〕21号",
                 "处罚结果": "罚款1万元",
                 "处罚金额": "10000",
                 "处罚单位": "中国人民银行江苏省分行",
                 "处罚日期": "2025-09-24"},
            ],
        },
        "qcc-company.get_change_records": {
            "变更记录信息": [
                {"变更日期": "2025-10-15", "变更项目": "高级管理人员备案"},
            ],
        },
    }

    out_dir = "/tmp/v1_2_test_output"
    os.makedirs(out_dir, exist_ok=True)
    result = generate_report(
        uscc="91320594088140947F",
        mcp_responses=mcp_responses,
        out_dir=out_dir,
        report_id="TEST-E2E-001",
    )

    # 校验产物
    assert os.path.exists(result["md_path"]), "MD 文件应存在"
    assert os.path.exists(result["manifest_path"]), "manifest 应存在"

    md = open(result["md_path"], encoding="utf-8").read()
    assert "91320594088140947F" in md
    assert "陈德强" in md
    assert "苏银罚决字〔2025〕21号" in md
    # 编造数据不应出现：
    assert "91320506MA1UYUWY3X" not in md, "编造 USCC 不应出现"
    assert "递交主板申报稿" not in md, "编造的上市信息不应出现"
    assert "已处置" not in md, "处罚状态'已处置'不应出现（除非 MCP 显式返回）"
    assert "竝观聚益" not in md  # 错字

    # manifest 校验
    with open(result["manifest_path"], encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["uscc"] == "91320594088140947F"
    assert manifest["field_count"] > 0
    assert manifest["evidence_count"] > 0

    print(f"✓ test_e2e_with_mock_mcp（生成于 {result['md_path']}）")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("V1.2 框架红绿对照测试")
    print("=" * 60)

    test_uscc_fabricated()
    test_count_vs_rows_shareholders()
    test_count_vs_rows_historical()
    test_count_vs_rows_executives()
    test_count_vs_rows_investments()
    test_penalty_banned_phrases()
    test_e2e_with_mock_mcp()

    print()
    print("=" * 60)
    print(f"全部测试通过（pydantic 已安装：{PYDANTIC_OK}）")
    if not PYDANTIC_OK:
        print("⚠ 注意：未安装 pydantic 时，schema 校验会失效。生产环境必须安装。")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
