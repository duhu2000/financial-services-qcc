#!/usr/bin/env python3
"""
测试完整报告导出 - 使用 WorkBuddy 生成的详细内容
"""
import sys
sys.path.insert(0, '.')

from utils.report_exporter import ReportExporter


def test_kyb_full_export():
    """使用完整 KYB 报告内容测试导出"""
    print("=" * 70)
    print("测试: KYB 完整报告导出 - 郑州莱威装饰工程有限公司")
    print("=" * 70)

    # 读取 WorkBuddy 生成的完整报告
    with open('/Users/qcc/WorkBuddy/KYB核验报告-郑州莱威装饰工程有限公司-20260325.md', 'r', encoding='utf-8') as f:
        full_content = f.read()

    print(f"\n原始 Markdown 文件大小: {len(full_content)} 字符")
    print(f"行数: {len(full_content.split(chr(10)))} 行")

    # 使用完整内容导出
    exporter = ReportExporter(output_dir="./reports")

    # 构造 report_data，包含完整内容
    report_data = {
        "company_name": "郑州莱威装饰工程有限公司",
        "credit_code": "91410103MA9EYP5H0E",
        "status": "⚠️ 高风险 - 禁止准入",
        "kyb_rating": "D",
        "verification_suggestion": "🚫 建议禁止开户，拒绝准入",
        "full_content": full_content,  # 关键：传入完整内容
    }

    print("\n[导出 Word 格式...]")
    exported = exporter.export_kyb_report(report_data, "郑州莱威装饰工程有限公司", "docx")

    if exported.get("docx"):
        import os
        size = os.path.getsize(exported["docx"])
        print(f"   ✅ Word: {exported['docx']}")
        print(f"      文件大小: {size:,} bytes ({size/1024:.1f} KB)")

    print("\n[导出 PPT 大纲格式...]")
    exported = exporter.export_kyb_report(report_data, "郑州莱威装饰工程有限公司", "pptx")

    if exported.get("pptx"):
        import os
        size = os.path.getsize(exported["pptx"])
        print(f"   ✅ PPT 大纲: {exported['pptx']}")
        print(f"      文件大小: {size:,} bytes ({size/1024:.1f} KB)")

    print("\n" + "=" * 70)


def test_ic_memo_full_export():
    """使用完整 IC Memo 报告内容测试导出"""
    print("=" * 70)
    print("测试: IC Memo 完整报告导出 - 北京至格科技有限公司")
    print("=" * 70)

    # 读取 WorkBuddy 生成的完整报告
    with open('/Users/qcc/WorkBuddy/IC-Memo-投资尽调报告-北京至格科技有限公司-20260325.md', 'r', encoding='utf-8') as f:
        full_content = f.read()

    print(f"\n原始 Markdown 文件大小: {len(full_content)} 字符")
    print(f"行数: {len(full_content.split(chr(10)))} 行")

    # 使用完整内容导出
    exporter = ReportExporter(output_dir="./reports")

    report_data = {
        "company_name": "北京至格科技有限公司",
        "investment_round": "C轮",
        "sector": "制造业 - AR/光学显示",
        "full_content": full_content,  # 关键：传入完整内容
    }

    print("\n[导出 Word 格式...]")
    exported = exporter.export_ic_memo(report_data, "北京至格科技有限公司", "docx")

    if exported.get("docx"):
        import os
        size = os.path.getsize(exported["docx"])
        print(f"   ✅ Word: {exported['docx']}")
        print(f"      文件大小: {size:,} bytes ({size/1024:.1f} KB)")

    print("\n[导出 PPT 大纲格式...]")
    exported = exporter.export_ic_memo(report_data, "北京至格科技有限公司", "pptx")

    if exported.get("pptx"):
        import os
        size = os.path.getsize(exported["pptx"])
        print(f"   ✅ PPT 大纲: {exported['pptx']}")
        print(f"      文件大小: {size:,} bytes ({size/1024:.1f} KB)")

    print("\n" + "=" * 70)


def compare_files():
    """对比文件大小"""
    print("\n" + "=" * 70)
    print("文件对比")
    print("=" * 70)

    import os

    files = [
        ("WorkBuddy KYB", "/Users/qcc/WorkBuddy/KYB核验报告-郑州莱威装饰工程有限公司-20260325.md"),
        ("导出 KYB Markdown", "./reports/KYB核验报告-郑州莱威装饰工程有限公司-20260326.md"),
        ("导出 KYB Word", "./reports/KYB核验报告-郑州莱威装饰工程有限公司-20260326.docx"),
        ("", ""),
        ("WorkBuddy IC Memo", "/Users/qcc/WorkBuddy/IC-Memo-投资尽调报告-北京至格科技有限公司-20260325.md"),
        ("导出 IC Memo Markdown", "./reports/IC-Memo-投资尽调报告-北京至格科技有限公司-20260326.md"),
        ("导出 IC Memo Word", "./reports/IC-Memo-投资尽调报告-北京至格科技有限公司-20260326.docx"),
    ]

    for name, path in files:
        if not name:
            print()
            continue
        if os.path.exists(path):
            size = os.path.getsize(path)
            lines = len(open(path, 'r', encoding='utf-8', errors='ignore').read().split('\n'))
            print(f"{name:30s} {size:>10,} bytes ({lines:>3} 行)  {path}")
        else:
            print(f"{name:30s} {'文件不存在':>20}  {path}")


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    print("\n  企查查 MCP 金融插件 - 完整报告导出测试\n")
    print("🚀" * 35 + "\n")

    test_kyb_full_export()
    test_ic_memo_full_export()
    compare_files()

    print("\n✅ 测试完成！")
    print("\n生成的完整 Word 报告保存在: ./reports/")
