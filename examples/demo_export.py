"""
报告导出功能演示
展示 KYB 和 IC Memo 的三格式导出
"""
import sys
sys.path.insert(0, '..')

from utils.kyb_verifier import KYBVerifier
from utils.dd_report_generator import DDReportGenerator


def demo_kyb_export():
    """演示 KYB 报告三格式导出"""
    print("=" * 70)
    print("演示: KYB 核验报告 - 三格式导出")
    print("=" * 70)

    verifier = KYBVerifier(output_dir="./output")

    # 示例数据（实际使用时调用 verify_company 方法）
    sample_report = {
        "company_name": "华为技术有限公司",
        "credit_code": "9144030019237XXXXX",
        "status": "核验完成",
        "kyb_rating": "A",
        "verification_suggestion": "🟢 正常准入 - 主体合法存续，无明显风险信号",
        "phase_results": {
            "entity": {
                "entity_info": {
                    "注册名称": "华为技术有限公司",
                    "统一社会信用代码": "9144030019237XXXXX",
                    "法定代表人": "赵明路",
                    "注册资本": "30000万元",
                    "经营状态": "存续",
                    "成立日期": "1987-09-15",
                }
            },
            "shareholders": {
                "ubo": [
                    {"名称": "任正非", "持股比例": "0.88%"},
                ]
            },
            "risks": {
                "critical": {},
                "high": {},
                "medium": {},
                "low": {}
            },
            "operation": {
                "招投标数量": 156,
                "资质证书数量": 42,
                "舆情信号": "正常"
            }
        },
        "risk_summary": {
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "total_count": 0
        }
    }

    # 导出所有格式
    print("\n[1] 导出所有格式 (md + docx + pptx):")
    exported = verifier.exporter.export_kyb_report(
        sample_report, "华为技术有限公司", "all"
    )
    print(f"   Markdown: {exported.get('md')}")
    print(f"   Word:     {exported.get('docx')}")
    print(f"   PPT:      {exported.get('pptx')}")

    # 仅导出 Word
    print("\n[2] 仅导出 Word 格式:")
    exported = verifier.exporter.export_kyb_report(
        sample_report, "华为技术有限公司", "docx"
    )
    print(f"   Word: {exported.get('docx')}")

    print("\n" + "=" * 70)


def demo_ic_memo_export():
    """演示 IC Memo 报告三格式导出"""
    print("=" * 70)
    print("演示: IC Memo 投资尽调报告 - 三格式导出")
    print("=" * 70)

    generator = DDReportGenerator(output_dir="./output")

    # 示例数据
    sample_report = {
        "company_name": "北京至格科技有限公司",
        "investment_round": "C轮",
        "sector": "制造业 - AR/光学显示",
        "chapters": {
            "chapter_1_executive_summary": {
                "highlights": [
                    "技术领先 - 64件专利，国内AR衍射光波导领域头部厂商",
                    "市场机遇 - AI眼镜爆发元年，小米/OPPO/阿里核心供应商",
                    "量产能力 - 建成国内首条AR衍射光波导全自动产线",
                ],
                "concerns": [
                    "技术路线竞争 - 衍射光波导面临Birdbath等技术竞争",
                    "客户集中 - 高度依赖小米、OPPO等头部客户",
                ],
            },
            "chapter_2_company_overview": {
                "basic_info": {
                    "注册名称": "北京至格科技有限公司",
                    "统一社会信用代码": "91110229MA01L7WH4R",
                    "法定代表人": "孟祥峰",
                    "注册资本": "6279.922万元",
                    "成立日期": "2019-07-04",
                }
            },
            "chapter_3_intellectual_property": {
                "专利数量": 64,
                "发明专利": 36,
                "商标数量": 31,
            },
            "chapter_4_legal_compliance": {
                "risk_summary": {
                    "critical_count": 0,
                    "high_count": 0,
                },
                "compliance_conclusion": "法律尽调通过，无重大法律障碍",
            },
            "chapter_5_operation_market": {
                "bidding_activity": {
                    "count": 2,
                    "level": "中"
                }
            },
            "chapter_7_investment_recommendation": {
                "risk_level": "中",
                "investment_recommendation": "推荐投资，建议设置对赌条款",
            }
        }
    }

    # 导出所有格式
    print("\n[1] 导出所有格式 (md + docx + pptx):")
    exported = generator.exporter.export_ic_memo(
        sample_report, "北京至格科技有限公司", "all"
    )
    print(f"   Markdown: {exported.get('md')}")
    print(f"   Word:     {exported.get('docx')}")
    print(f"   PPT:      {exported.get('pptx')}")

    print("\n" + "=" * 70)


def demo_usage_examples():
    """演示使用示例"""
    print("\n" + "=" * 70)
    print("使用示例代码")
    print("=" * 70)
    print("""
# 1. KYB 核验 - 生成所有格式（默认）
from utils.kyb_verifier import KYBVerifier

verifier = KYBVerifier()
results = verifier.verify_company(
    company_name="华为技术有限公司",
    credit_code="9144030019237XXXXX",
    export_format="all"  # 默认，可省略
)

# 2. KYB 核验 - 仅生成 Word
results = verifier.verify_company(
    company_name="华为技术有限公司",
    export_format="docx"
)

# 3. IC Memo - 生成所有格式
from utils.dd_report_generator import DDReportGenerator

generator = DDReportGenerator()
report = generator.generate_full_dd_profile(
    company_name="北京至格科技有限公司",
    investment_round="C轮",
    sector="制造业",
    export_format="all"  # 默认
)

# 4. IC Memo - 仅生成 PPT（适合路演）
report = generator.generate_full_dd_profile(
    company_name="北京至格科技有限公司",
    export_format="pptx"
)

# 获取生成的文件路径
exported_files = results.get("exported_files", {})
print(f"Word文件: {exported_files.get('docx')}")
print(f"PPT文件: {exported_files.get('pptx')}")
    """)
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    print("\n  企查查 MCP 金融插件 - 三格式导出功能演示\n")
    print("🚀" * 35 + "\n")

    demo_kyb_export()
    demo_ic_memo_export()
    demo_usage_examples()

    print("\n✅ 演示完成！")
    print("\n生成的文件保存在: ./output/")
    print("支持的格式:")
    print("  • Markdown (.md) - 原始文本，便于系统对接")
    print("  • Word (.docx)   - 专业排版，适合打印盖章")
    print("  • PPT (.pptx)    - 一页摘要，适合路演汇报")
