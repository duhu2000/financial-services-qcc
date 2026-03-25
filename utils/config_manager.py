"""
Config Manager - V2 新增
自动配置管理器，负责.mcp.json的创建、验证和修复
继承自V1的一键安装能力
"""
import json
import os
from typing import Dict, List, Optional, Tuple


class ConfigManager:
    """MCP 配置管理器

    功能:
    1. 自动创建 .mcp.json 配置文件
    2. 验证配置完整性
    3. 修复配置问题
    4. 环境变量管理
    """

    # 默认配置模板
    DEFAULT_CONFIG = {
        "mcpServers": {
            "qcc-company": {
                "url": "https://mcp.qcc.com/data/company/stream",
                "headers": {
                    "Authorization": "Bearer ${QCC_MCP_API_KEY}"
                },
                "description": "企查查企业基座 - 工商登记、股东信息、变更记录",
                "tools": [
                    "get_company_registration_info",
                    "get_shareholder_info",
                    "get_key_personnel",
                    "get_change_records",
                    "get_branches",
                    "get_external_investments",
                    "get_annual_reports",
                    "get_contact_info",
                    "verify_company_accuracy"
                ]
            },
            "qcc-risk": {
                "url": "https://mcp.qcc.com/data/risk/stream",
                "headers": {
                    "Authorization": "Bearer ${QCC_MCP_API_KEY}"
                },
                "description": "企查查风控大脑 - 18类风险扫描",
                "tools": [
                    "get_dishonest_info",
                    "get_judgment_debtor_info",
                    "get_executed_person_info",
                    "get_high_consumption_restriction",
                    "get_bankruptcy_reorganization",
                    "get_equity_freeze",
                    "get_equity_pledge",
                    "get_business_exception",
                    "get_serious_violation",
                    "get_administrative_penalty",
                    "get_environmental_penalty",
                    "get_tax_arrears_notice",
                    "get_tax_violation",
                    "get_abnormal_tax",
                    "get_lawsuit_info",
                    "get_judicial_document"
                ]
            },
            "qcc-ipr": {
                "url": "https://mcp.qcc.com/data/ipr/stream",
                "headers": {
                    "Authorization": "Bearer ${QCC_MCP_API_KEY}"
                },
                "description": "企查查知产引擎 - 专利、商标、软著",
                "tools": [
                    "get_patent_info",
                    "get_trademark_info",
                    "get_software_copyright_info",
                    "get_copyright_work_info",
                    "get_standard_info"
                ]
            },
            "qcc-operation": {
                "url": "https://mcp.qcc.com/data/operation/stream",
                "headers": {
                    "Authorization": "Bearer ${QCC_MCP_API_KEY}"
                },
                "description": "企查查经营罗盘 - 招投标、资质、舆情",
                "tools": [
                    "get_bidding_info",
                    "get_qualifications",
                    "get_administrative_license",
                    "get_credit_evaluation",
                    "get_spot_check_info",
                    "get_news_sentiment",
                    "get_recruitment_info"
                ]
            }
        },
        "configuration": {
            "setup_guide": "https://github.com/duhu2000/financial-services-qcc/blob/main/docs/MCP_CONFIGURATION.md",
            "required_env_vars": ["QCC_MCP_API_KEY"],
            "version": "2.0.0"
        }
    }

    def __init__(self, config_path: str = "~/.claude/.mcp.json"):
        self.config_path = os.path.expanduser(config_path)
        self.config_dir = os.path.dirname(self.config_path)

    def create_config(self, api_key: str = None, force: bool = False) -> Tuple[bool, str]:
        """
        创建 .mcp.json 配置文件

        :param api_key: API Key（可选，会从环境变量读取）
        :param force: 是否强制覆盖现有配置
        :return: (成功状态, 消息)
        """
        # 检查是否已存在
        if os.path.exists(self.config_path) and not force:
            return False, f"配置文件已存在: {self.config_path} (使用 force=True 覆盖)"

        # 确保目录存在
        os.makedirs(self.config_dir, exist_ok=True)

        # 如果没有提供api_key，尝试从环境变量读取
        if not api_key:
            api_key = os.getenv("QCC_MCP_API_KEY", "")

        # 创建配置
        config = self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # 设置适当的权限
            os.chmod(self.config_path, 0o600)

            return True, f"配置文件创建成功: {self.config_path}"
        except Exception as e:
            return False, f"配置文件创建失败: {e}"

    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        验证配置完整性

        :return: (是否有效, 错误列表)
        """
        errors = []

        # 检查文件是否存在
        if not os.path.exists(self.config_path):
            errors.append(f"配置文件不存在: {self.config_path}")
            return False, errors

        # 读取配置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"配置文件JSON格式错误: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"读取配置文件失败: {e}")
            return False, errors

        # 检查必要的键
        if "mcpServers" not in config:
            errors.append("缺少 'mcpServers' 配置项")
            return False, errors

        mcp_servers = config["mcpServers"]

        # 检查必需的server
        required_servers = ["qcc-company", "qcc-risk", "qcc-ipr", "qcc-operation"]
        for server in required_servers:
            if server not in mcp_servers:
                errors.append(f"缺少必要的MCP服务配置: {server}")

        # 检查每个server的配置
        for server_id, server_config in mcp_servers.items():
            if "url" not in server_config:
                errors.append(f"{server_id}: 缺少 'url' 配置")
            if "headers" not in server_config:
                errors.append(f"{server_id}: 缺少 'headers' 配置")
            elif "Authorization" not in server_config["headers"]:
                errors.append(f"{server_id}: 缺少 'Authorization' header")

        # 检查环境变量
        api_key = os.getenv("QCC_MCP_API_KEY")
        if not api_key:
            errors.append("环境变量 QCC_MCP_API_KEY 未设置")
        elif len(api_key) < 10:
            errors.append("环境变量 QCC_MCP_API_KEY 格式异常（长度过短）")

        return len(errors) == 0, errors

    def fix_config(self) -> Tuple[bool, str]:
        """
        修复配置问题

        :return: (是否成功, 消息)
        """
        is_valid, errors = self.validate_config()

        if is_valid:
            return True, "配置验证通过，无需修复"

        # 如果配置不存在或格式错误，重新创建
        if any("不存在" in e or "JSON格式错误" in e for e in errors):
            return self.create_config(force=True)

        # 否则尝试修复具体问题
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 确保有mcpServers
            if "mcpServers" not in config:
                config["mcpServers"] = {}

            mcp_servers = config["mcpServers"]

            # 添加缺失的server配置
            for server_id, server_config in self.DEFAULT_CONFIG["mcpServers"].items():
                if server_id not in mcp_servers:
                    mcp_servers[server_id] = server_config

            # 保存修复后的配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True, "配置修复完成"
        except Exception as e:
            return False, f"配置修复失败: {e}"

    def get_config(self) -> Optional[Dict]:
        """获取当前配置"""
        if not os.path.exists(self.config_path):
            return None

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

    def check_env_variables(self) -> Dict[str, Tuple[bool, str]]:
        """
        检查环境变量配置

        :return: {变量名: (是否设置, 值或错误信息)}
        """
        result = {}

        # 必需的环境变量
        api_key = os.getenv("QCC_MCP_API_KEY")
        if api_key:
            masked = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
            result["QCC_MCP_API_KEY"] = (True, masked)
        else:
            result["QCC_MCP_API_KEY"] = (False, "未设置")

        return result

    def generate_env_setup_script(self) -> str:
        """生成环境变量设置脚本"""
        script = """#!/bin/bash
# 企查查 MCP 环境变量设置脚本
# 请将 YOUR_API_KEY 替换为您的实际 API Key

export QCC_MCP_API_KEY="YOUR_API_KEY"

echo "环境变量已设置:"
echo "  QCC_MCP_API_KEY=${QCC_MCP_API_KEY:0:4}****${QCC_MCP_API_KEY: -4}"

# 如需永久生效，请添加以下行到 ~/.bashrc 或 ~/.zshrc:
# echo 'export QCC_MCP_API_KEY="YOUR_API_KEY"' >> ~/.bashrc
"""
        return script

    def print_diagnostic(self):
        """打印诊断信息"""
        print("=" * 60)
        print("企查查 MCP 配置诊断")
        print("=" * 60)

        # 配置文件状态
        print("\n[配置文件]")
        print(f"  路径: {self.config_path}")
        print(f"  状态: {'✅ 存在' if os.path.exists(self.config_path) else '❌ 不存在'}")

        # 配置验证
        print("\n[配置验证]")
        is_valid, errors = self.validate_config()
        if is_valid:
            print("  ✅ 配置验证通过")
        else:
            print("  ❌ 配置验证失败:")
            for error in errors:
                print(f"     - {error}")

        # 环境变量
        print("\n[环境变量]")
        env_status = self.check_env_variables()
        for var, (is_set, value) in env_status.items():
            print(f"  {'✅' if is_set else '❌'} {var}: {value}")

        print("\n" + "=" * 60)


# 命令行工具
if __name__ == '__main__':
    import sys

    manager = ConfigManager()

    if len(sys.argv) < 2:
        manager.print_diagnostic()
        sys.exit(0)

    command = sys.argv[1]

    if command == "create":
        force = "--force" in sys.argv
        success, msg = manager.create_config(force=force)
        print(msg)
        sys.exit(0 if success else 1)

    elif command == "validate":
        is_valid, errors = manager.validate_config()
        if is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
        sys.exit(0 if is_valid else 1)

    elif command == "fix":
        success, msg = manager.fix_config()
        print(msg)
        sys.exit(0 if success else 1)

    elif command == "diagnostic":
        manager.print_diagnostic()
        sys.exit(0)

    elif command == "env-script":
        print(manager.generate_env_setup_script())
        sys.exit(0)

    else:
        print(f"未知命令: {command}")
        print("可用命令: create, validate, fix, diagnostic, env-script")
        sys.exit(1)
