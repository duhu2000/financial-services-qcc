#!/usr/bin/env python3
"""
测试报告导出功能 - 使用已有报告数据
"""
import sys
sys.path.insert(0, '.')

from utils.report_exporter import ReportExporter


def test_kyb_export():
    """测试 KYB 报告导出 - 郑州莱威装饰工程有限公司"""
    print("=" * 70)
    print("测试: KYB 报告导出 - 郑州莱威装饰工程有限公司")
    print("=" * 70)

    # 使用 WorkBuddy 目录下的报告数据
    kyb_report = {
        "company_name": "郑州莱威装饰工程有限公司",
        "credit_code": "91410103MA9EYP5H0E",
        "status": "⚠️ 高风险 - 禁止准入",
        "kyb_rating": "D",
        "verification_suggestion": "🚫 建议禁止开户，拒绝准入",
        "phase_results": {
            "entity": {
                "entity_info": {
                    "企业名称": "郑州莱威装饰工程有限公司",
                    "统一社会信用代码": "91410103MA9EYP5H0E",
                    "法定代表人": "朱威",
                    "企业类型": "有限责任公司（自然人独资）",
                    "注册资本": "500万元（认缴）",
                    "实缴资本": "未公示 ⚠️",
                    "成立日期": "2020-04-17",
                    "登记状态": "存续（在营、开业、在册）",
                    "注册地址": "河南省郑州市二七区鼎盛大道南、青铜西路西绿地滨湖国际城三区2号楼6层602",
                    "电话": "未登记 ⚠️",
                    "邮箱": "1079115033@qq.com",
                }
            },
            "shareholders": {
                "shareholders": [
                    {"名称": "朱威", "持股比例": "100%", "股东类型": "自然人股东"}
                ],
                "ubo": [
                    {"名称": "朱威", "持股比例": "100%", "识别依据": "自然人股东持股≥25%"}
                ]
            },
            "risks": {
                "critical": {
                    "失信被执行人": {"count": 1, "details": [{"案号": "（2025）豫0184执2906号", "涉案金额": "39,000元"}]},
                    "被执行人": {"count": 1, "details": [{"案号": "（2025）豫0103执12004号", "执行标的": "96,341.00元"}]},
                    "限制高消费": {"count": 2, "details": [{"限制对象": "朱威"}]},
                },
                "high": {
                    "经营异常": {"count": 5, "details": ["连续5年未公示年度报告"]},
                },
                "medium": {},
                "low": {}
            },
            "operation": {
                "招投标数量": 0,
                "资质证书数量": 0,
                "舆情信号": "正常",
                "持续经营能力": "⚠️ 存疑"
            }
        },
        "risk_summary": {
            "critical_count": 3,
            "high_count": 1,
            "medium_count": 0,
            "low_count": 0,
            "total_count": 4
        }
    }

    exporter = ReportExporter(output_dir="./reports")

    print("\n[1] 导出所有格式 (md + docx + pptx):")
    exported = exporter.export_kyb_report(kyb_report, "郑州莱威装饰工程有限公司", "all")

    for fmt, path in exported.items():
        if path:
            print(f"   ✅ {fmt.upper()}: {path}")
            # 检查文件大小
            import os
            size = os.path.getsize(path)
            print(f"      文件大小: {size:,} bytes")

    print("\n" + "=" * 70)


def test_ic_memo_export():
    """测试 IC Memo 报告导出 - 北京至格科技有限公司"""
    print("=" * 70)
    print("测试: IC Memo 报告导出 - 北京至格科技有限公司")
    print("=" * 70)

    ic_memo_report = {
        "company_name": "北京至格科技有限公司",
        "investment_round": "C轮（跟进投资）",
        "sector": "制造业 - AR/光学显示",
        "chapters": {
            "chapter_1_executive_summary": {
                "highlights": [
                    "技术领先 - 64件专利（36项发明专利），国内AR衍射光波导领域头部厂商，牵头制定2项AR国家标准",
                    "市场机遇 - AI眼镜爆发元年，已成为小米、OPPO、阿里核心供应商，年交付目标百万片",
                    "量产能力 - 建成国内首条AR衍射光波导全自动产线，年交付能力百万片",
                    "融资活跃 - 一年内完成3轮亿级融资（2025年3月、8月、2026年3月），资本认可度高",
                    "清华基因 - 核心团队源自清华大学，长江学者、杰出青年领衔，产学研转化能力强",
                ],
                "concerns": [
                    "技术路线竞争 - 衍射光波导面临Birdbath等技术竞争，苹果未采用该路线",
                    "客户集中 - 高度依赖小米、OPPO等头部客户（占订单量大头）",
                    "估值风险 - 本轮估值未披露，可能存在泡沫",
                    "产能爬坡 - 百万片量产目标需验证",
                    "人才流失 - AR光学人才稀缺，核心人员流失风险",
                ],
                "investment_thesis": "推荐投资，建议设置对赌条款",
                "key_metrics": {
                    "注册资本": "6279.922万元",
                    "专利数量": 64,
                    "关键风险数": 0,
                    "高风险数": 0
                }
            },
            "chapter_2_company_overview": {
                "basic_info": {
                    "公司全称": "北京至格科技有限公司",
                    "统一社会信用代码": "91110229MA01L7WH4R",
                    "成立时间": "2019-07-04 (6.7年历史)",
                    "注册资本": "6,279.922万元",
                    "实缴资本": "562.351万元 (89.55%实缴)",
                    "法定代表人": "孟祥峰",
                    "注册地址": "北京市门头沟区石龙工业区桥园路1号1幢1层102室",
                    "员工人数": "47人（社保缴纳人数）",
                    "企业类型": "其他有限责任公司",
                    "纳税人资质": "一般纳税人",
                    "国标行业": "制造业",
                },
                "shareholders": [
                    {"名称": "孟祥峰", "持股比例": "22.76%", "股东类型": "自然人", "备注": "实控人"},
                    {"名称": "湖北小米长江产业基金", "持股比例": "4.68%", "股东类型": "有限合伙", "备注": "产业基金"},
                    {"名称": "清控银杏南通创投", "持股比例": "7.50%", "股东类型": "有限合伙", "备注": "VC/PE"},
                ],
                "ubo": [
                    {"名称": "孟祥峰", "持股比例": "22.76%", "识别依据": "自然人股东持股≥25%"}
                ],
                "equity_analysis": {
                    "股权集中度": "适中",
                    "实际控制人": "孟祥峰"
                }
            },
            "chapter_3_intellectual_property": {
                "专利数量": 64,
                "发明专利": 36,
                "实用新型": 26,
                "外观设计": 2,
                "PCT专利": 0,
                "商标数量": 31,
                "软件著作权数量": 10,
                "core_assessment": {
                    "技术壁垒": "高",
                    "品牌保护": "良好"
                }
            },
            "chapter_4_legal_compliance": {
                "risks": {
                    "critical": {},
                    "high": {},
                    "medium": {},
                    "low": {}
                },
                "risk_summary": {
                    "critical_count": 0,
                    "high_count": 0,
                    "total_risks": 0
                },
                "compliance_conclusion": "✅ **通过** - 法律尽调通过，无重大法律障碍",
                "lawsuits": [],
            },
            "chapter_5_operation_market": {
                "bidding_activity": {
                    "count": 2,
                    "level": "上升",
                    "recent_wins": [
                        "清华大学全息光栅制作系统采购 1479.6万元",
                        "南通智能感知研究院光刻加工项目 47万元"
                    ]
                },
                "qualifications": [
                    {"名称": "环境管理体系认证", "有效期": "2023-04-03 至 2026-04-02", "状态": "有效"},
                    {"名称": "质量管理体系认证", "有效期": "2023-04-03 至 2026-04-02", "状态": "有效"},
                ],
                "news_sentiment": "正面",
                "market_position": "挑战者（国内AR衍射光波导领域头部厂商之一）"
            },
            "chapter_6_financial_analysis": {
                "note": "非上市公司，无公开财务数据",
                "recommendation": "建议投前获取详细财务报表"
            },
            "chapter_7_investment_recommendation": {
                "investment_recommendation": "✅ **推荐**",
                "risk_level": "中",
                "key_risks": [
                    "技术路线竞争: 衍射光波导面临Birdbath等技术竞争",
                    "客户集中风险: 高度依赖小米、OPPO等头部客户",
                ],
                "recommended_terms": [
                    "对赌条款: 2026年营收≥2亿元，2027年营收≥5亿元",
                    "回购条款: 未能在2029年前完成IPO，实控人以年化10%回购",
                    "优先清算: 1.5倍清算优先权",
                    "董事席位: 有权委派1名董事"
                ],
                "拟投金额": "5,000万-1亿元",
                "投前估值": "10-15亿元",
                "持股比例": "3-5%"
            }
        }
    }

    exporter = ReportExporter(output_dir="./reports")

    print("\n[1] 导出所有格式 (md + docx + pptx):")
    exported = exporter.export_ic_memo(ic_memo_report, "北京至格科技有限公司", "all")

    for fmt, path in exported.items():
        if path:
            print(f"   ✅ {fmt.upper()}: {path}")
            # 检查文件大小
            import os
            size = os.path.getsize(path)
            print(f"      文件大小: {size:,} bytes")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    print("\n  企查查 MCP 金融插件 - 报告导出功能测试\n")
    print("🚀" * 35 + "\n")

    test_kyb_export()
    test_ic_memo_export()

    print("\n✅ 测试完成！")
    print(f"\n生成的文件保存在: ./reports/")
