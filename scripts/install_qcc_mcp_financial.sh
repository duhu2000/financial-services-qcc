#!/bin/bash
# Financial Services QCC MCP Plugin V2 Installation Script
# 金融机构企查查MCP插件V2融合版安装脚本
#
# V2特性:
# - 基于Manus架构 + V1增强
# - 支持commands/命令定义
# - 支持utils/ Python工具类
# - 保留SKILL.md兼容层
#
# 一键安装命令:
#   bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
#
# 本地安装命令:
#   bash install_qcc_mcp_financial.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Financial Services QCC MCP Installer"
echo "  金融机构企查查MCP插件V2融合版安装程序"
echo "  Version: 2.0.0"
echo "=========================================="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    CLAUDE_DIR="$HOME/.claude"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
    CLAUDE_DIR="$HOME/.claude"
else
    echo -e "${RED}Unsupported platform: $OSTYPE${NC}"
    echo "This script supports macOS and Linux only."
    exit 1
fi

echo -e "${BLUE}Detected platform: $PLATFORM${NC}"
echo ""

# Check installation mode
SCRIPT_SOURCE="${BASH_SOURCE[0]}"
INSTALL_MODE="local"
SOURCE_DIR=""

# Detect curl mode
if [[ "$SCRIPT_SOURCE" == /dev/fd/* ]] || [[ "$SCRIPT_SOURCE" == /proc/*/fd/* ]] || [ ! -f "$SCRIPT_SOURCE" ]; then
    INSTALL_MODE="curl"
    echo -e "${BLUE}Installation mode: curl (downloading from GitHub)${NC}"

    # Download from GitHub
    TEMP_DIR=$(mktemp -d)
    echo -e "${BLUE}Downloading from GitHub...${NC}"

    if command -v curl &> /dev/null; then
        curl -sL https://github.com/duhu2000/financial-services-qcc/archive/refs/heads/main.tar.gz | tar -xz -C "$TEMP_DIR" --strip-components=1
    elif command -v wget &> /dev/null; then
        wget -qO- https://github.com/duhu2000/financial-services-qcc/archive/refs/heads/main.tar.gz | tar -xz -C "$TEMP_DIR" --strip-components=1
    else
        echo -e "${RED}Error: curl or wget is required${NC}"
        exit 1
    fi

    SOURCE_DIR="$TEMP_DIR"
else
    echo -e "${BLUE}Installation mode: local${NC}"
    SOURCE_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
fi

# Check for QCC MCP API Key
if [ -z "$QCC_MCP_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  QCC_MCP_API_KEY not found in environment${NC}"
    echo ""
    echo "To use QCC MCP enhanced features, you need an API key."
    echo "Get your key at: https://agent.qcc.com"
    echo ""
    echo "Options:"
    echo "1. Continue without QCC MCP (demo mode only)"
    echo "2. Enter API key now"
    echo "3. Exit and configure later"
    echo ""
    read -p "Select option (1/2/3): " choice

    case $choice in
        1)
            echo -e "${YELLOW}Continuing without QCC MCP. Chinese enterprise verification will be limited.${NC}"
            ;;
        2)
            read -p "Enter your QCC MCP API Key: " api_key
            export QCC_MCP_API_KEY="$api_key"
            echo -e "${GREEN}✓ API key set for this session${NC}"
            echo ""
            echo "To make this permanent, add to your shell profile:"
            if [[ "$PLATFORM" == "macOS" ]]; then
                echo "  echo 'export QCC_MCP_API_KEY=\"$api_key\"' >> ~/.zshrc"
                echo "  source ~/.zshrc"
            else
                echo "  echo 'export QCC_MCP_API_KEY=\"$api_key\"' >> ~/.bashrc"
                echo "  source ~/.bashrc"
            fi
            ;;
        3)
            echo "Exiting. Please set QCC_MCP_API_KEY and run again."
            exit 0
            ;;
        *)
            echo "Invalid option. Exiting."
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}✓ QCC_MCP_API_KEY found${NC}"
fi

echo ""
echo "=========================================="
echo "  Step 1: Installing MCP Configuration"
echo "=========================================="

# Install .mcp.json configuration
echo ""
echo -e "${BLUE}Installing MCP server configuration...${NC}"
MCP_CONFIG_DEST="$CLAUDE_DIR/.mcp.json"

if [ -f "$MCP_CONFIG_DEST" ]; then
    echo -e "${YELLOW}  Existing .mcp.json found, backing up...${NC}"
    cp "$MCP_CONFIG_DEST" "${MCP_CONFIG_DEST}.backup.$(date +%Y%m%d%H%M%S)"
fi

# Create MCP config with API key placeholder
cat > "$MCP_CONFIG_DEST" << 'MCPJSONEOF'
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      },
      "description": "企查查企业基座 - 提供工商登记、股东信息、变更记录等企业基础信息服务"
    },
    "qcc-risk": {
      "url": "https://agent.qcc.com/mcp/risk/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      },
      "description": "企查查风控大脑 - 提供失信、被执行、限高、破产等18类风险信息"
    },
    "qcc-ipr": {
      "url": "https://agent.qcc.com/mcp/ipr/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      },
      "description": "企查查知产引擎 - 提供专利、商标、软件著作权等知识产权信息"
    },
    "qcc-operation": {
      "url": "https://agent.qcc.com/mcp/operation/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      },
      "description": "企查查经营罗盘 - 提供招投标、资质证书、信用评级等经营信息"
    }
  }
}
MCPJSONEOF

echo -e "${GREEN}  ✓ MCP configuration installed to: $MCP_CONFIG_DEST${NC}"

echo ""
echo "=========================================="
echo "  Step 2: Installing Commands"
echo "=========================================="

# Define destination
COMMANDS_DIR="$CLAUDE_DIR/commands"

# Create commands directory if it doesn't exist
mkdir -p "$COMMANDS_DIR"

# Install command definitions
echo ""
echo -e "${BLUE}Installing command definitions...${NC}"

# qcc-kyb-profile command
if [ -f "$SOURCE_DIR/commands/qcc-kyb-profile.md" ]; then
    cp "$SOURCE_DIR/commands/qcc-kyb-profile.md" "$COMMANDS_DIR/"
    echo -e "${GREEN}  ✓ qcc-kyb-profile command installed${NC}"
fi

# qcc-full-dd-profile command
if [ -f "$SOURCE_DIR/commands/qcc-full-dd-profile.md" ]; then
    cp "$SOURCE_DIR/commands/qcc-full-dd-profile.md" "$COMMANDS_DIR/"
    echo -e "${GREEN}  ✓ qcc-full-dd-profile command installed${NC}"
fi

echo ""
echo "=========================================="
echo "  Step 3: Installing Skills (Compatibility Layer)"
echo "=========================================="

# Define destination
SKILLS_DIR="$CLAUDE_DIR/skills"

# Create skills directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Install investment banking skills
echo ""
echo -e "${BLUE}Installing investment banking skills...${NC}"
IB_SKILLS_DEST="$SKILLS_DIR/investment-banking-qcc"

if [ -d "$IB_SKILLS_DEST" ]; then
    echo -e "${YELLOW}  Existing investment-banking-qcc found, backing up...${NC}"
    mv "$IB_SKILLS_DEST" "${IB_SKILLS_DEST}.backup.$(date +%Y%m%d%H%M%S)"
fi

mkdir -p "$IB_SKILLS_DEST/strip-profile"
if [ -d "$SOURCE_DIR/investment-banking/skills/strip-profile" ]; then
    cp "$SOURCE_DIR/investment-banking/skills/strip-profile/SKILL.md" "$IB_SKILLS_DEST/strip-profile/"
    echo -e "${GREEN}  ✓ strip-profile skill installed${NC}"
fi

# Install private equity skills
echo ""
echo -e "${BLUE}Installing private equity skills...${NC}"
PE_SKILLS_DEST="$SKILLS_DIR/private-equity-qcc"

if [ -d "$PE_SKILLS_DEST" ]; then
    echo -e "${YELLOW}  Existing private-equity-qcc found, backing up...${NC}"
    mv "$PE_SKILLS_DEST" "${PE_SKILLS_DEST}.backup.$(date +%Y%m%d%H%M%S)"
fi

mkdir -p "$PE_SKILLS_DEST/ic-memo"
if [ -d "$SOURCE_DIR/private-equity/skills/ic-memo" ]; then
    cp "$SOURCE_DIR/private-equity/skills/ic-memo/SKILL.md" "$PE_SKILLS_DEST/ic-memo/"
    echo -e "${GREEN}  ✓ ic-memo skill installed${NC}"
fi

echo ""
echo "=========================================="
echo "  Step 4: Installing Python Utils"
echo "=========================================="

UTILS_DEST="$CLAUDE_DIR/financial-services-qcc/utils"
SCRIPTS_DEST="$CLAUDE_DIR/financial-services-qcc/scripts"

if [ -d "$CLAUDE_DIR/financial-services-qcc" ]; then
    echo -e "${YELLOW}Existing financial-services-qcc directory found, backing up...${NC}"
    mv "$CLAUDE_DIR/financial-services-qcc" "$CLAUDE_DIR/financial-services-qcc.backup.$(date +%Y%m%d%H%M%S)"
fi

# Install utils
mkdir -p "$UTILS_DEST"
if [ -d "$SOURCE_DIR/utils" ]; then
    cp "$SOURCE_DIR/utils/"*.py "$UTILS_DEST/"
    echo -e "${GREEN}✓ Python utils installed to: $UTILS_DEST${NC}"
fi

# Install scripts
mkdir -p "$SCRIPTS_DEST"
if [ -d "$SOURCE_DIR/scripts" ]; then
    cp "$SOURCE_DIR/scripts/"*.sh "$SCRIPTS_DEST/" 2>/dev/null || true
    echo -e "${GREEN}✓ Scripts installed to: $SCRIPTS_DEST${NC}"
fi

echo ""
echo "=========================================="
echo "  Step 5: Verifying Installation"
echo "=========================================="

# Check MCP config
echo ""
echo -e "${BLUE}Checking MCP configuration...${NC}"
if [ -f "$MCP_CONFIG_DEST" ]; then
    echo -e "${GREEN}  ✓ MCP configuration file installed${NC}"
else
    echo -e "${RED}  ✗ MCP configuration file not found${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 not found. Please install Python 3.9+${NC}"
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
fi

# Check required Python packages
echo ""
echo -e "${BLUE}Checking Python dependencies...${NC}"
python3 -c "import requests" 2>/dev/null && echo -e "${GREEN}  ✓ requests${NC}" || echo -e "${YELLOW}  ⚠️  requests not installed (pip3 install requests)${NC}"

# Verify command installation
echo ""
echo -e "${BLUE}Verifying command installation...${NC}"
if [ -f "$COMMANDS_DIR/qcc-kyb-profile.md" ]; then
    echo -e "${GREEN}  ✓ qcc-kyb-profile command installed${NC}"
else
    echo -e "${RED}  ✗ qcc-kyb-profile command not found${NC}"
fi

if [ -f "$COMMANDS_DIR/qcc-full-dd-profile.md" ]; then
    echo -e "${GREEN}  ✓ qcc-full-dd-profile command installed${NC}"
else
    echo -e "${RED}  ✗ qcc-full-dd-profile command not found${NC}"
fi

# Verify skill installation
echo ""
echo -e "${BLUE}Verifying skill installation...${NC}"
if [ -f "$IB_SKILLS_DEST/strip-profile/SKILL.md" ]; then
    echo -e "${GREEN}  ✓ strip-profile skill installed${NC}"
else
    echo -e "${RED}  ✗ strip-profile skill not found${NC}"
fi

if [ -f "$PE_SKILLS_DEST/ic-memo/SKILL.md" ]; then
    echo -e "${GREEN}  ✓ ic-memo skill installed${NC}"
else
    echo -e "${RED}  ✗ ic-memo skill not found${NC}"
fi

# Verify utils installation
echo ""
echo -e "${BLUE}Verifying utils installation...${NC}"
if [ -f "$UTILS_DEST/qcc_mcp_client.py" ]; then
    echo -e "${GREEN}  ✓ qcc_mcp_client.py installed${NC}"
else
    echo -e "${RED}  ✗ qcc_mcp_client.py not found${NC}"
fi

if [ -f "$UTILS_DEST/kyb_verifier.py" ]; then
    echo -e "${GREEN}  ✓ kyb_verifier.py installed${NC}"
else
    echo -e "${RED}  ✗ kyb_verifier.py not found${NC}"
fi

if [ -f "$UTILS_DEST/dd_report_generator.py" ]; then
    echo -e "${GREEN}  ✓ dd_report_generator.py installed${NC}"
else
    echo -e "${RED}  ✗ dd_report_generator.py not found${NC}"
fi

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Financial Services QCC MCP Plugin V2 has been installed successfully!${NC}"
echo ""
echo "Installed Components:"
echo "  Commands:"
echo "    • qcc-kyb-profile       - 企业KYB自动化核验"
echo "    • qcc-full-dd-profile   - 投融资全维度尽调"
echo "  Skills:"
echo "    • strip-profile         - 投行简况生成"
echo "    • ic-memo               - 投资委员会备忘录"
echo "  Utils:"
echo "    • qcc_mcp_client.py     - MCP客户端"
echo "    • kyb_verifier.py       - KYB核验器"
echo "    • dd_report_generator.py - 尽调报告生成器"
echo ""
echo "Location:"
echo "  Commands:   $COMMANDS_DIR"
echo "  Skills:     $IB_SKILLS_DEST, $PE_SKILLS_DEST"
echo "  Utils:      $UTILS_DEST"
echo "  Scripts:    $SCRIPTS_DEST"
echo ""

if [ -n "$QCC_MCP_API_KEY" ]; then
    echo -e "${GREEN}QCC MCP Status: CONFIGURED${NC}"
    echo "Chinese enterprise verification: ENABLED"
else
    echo -e "${YELLOW}QCC MCP Status: NOT CONFIGURED${NC}"
    echo "To enable Chinese enterprise verification:"
    echo "  export QCC_MCP_API_KEY='your_key_here'"
fi

echo ""
echo "=========================================="
echo "  ⚠️  IMPORTANT: Post-Installation Steps"
echo "=========================================="
echo ""
echo -e "${YELLOW}You MUST restart Claude Code to load the MCP configuration!${NC}"
echo ""
echo "Step 1: Completely exit Claude Code"
echo "Step 2: Ensure QCC_MCP_API_KEY is set:"
echo "       export QCC_MCP_API_KEY='your_api_key_here'"
echo "Step 3: Restart Claude Code"
echo "Step 4: Verify MCP servers are loaded:"
echo "       You should see 'qcc-company', 'qcc-risk', 'qcc-ipr', 'qcc-operation' in available tools"
echo ""
echo "=========================================="
echo "  Quick Start"
echo "=========================================="
echo ""
echo "After restarting Claude Code, use these commands:"
echo ""
echo "1. Verify MCP tools are available:"
echo "   Check if Claude shows available MCP tools from qcc-company, qcc-risk, etc."
echo ""
echo "2. Use the V2 commands:"
echo ""
echo "   # KYB自动化核验（银行开户/信贷审批）- A/B/C/D评级"
echo "   /qcc-kyb-profile 华为技术有限公司"
echo ""
echo "   # 全维度尽调（投资尽调）- 7章IC Memo"
echo "   /qcc-full-dd-profile 北京字节跳动科技有限公司 --round Series B"
echo ""
echo "3. Use the skills (backward compatible):"
echo ""
echo "   # 投行简况生成"
echo "   /strip-profile 目标公司"
echo ""
echo "   # 投资委员会备忘录"
echo "   /ic-memo 目标公司"
echo ""
echo "4. For programmatic use:"
echo "   python3 -c \"from utils.kyb_verifier import KYBVerifier; v = KYBVerifier(); print(v.verify_company('企业名称'))\""
echo ""
echo "=========================================="
echo "  Documentation"
echo "=========================================="
echo ""
echo "• README.md              - 详细文档"
echo "• SKILL.md (each skill)  - 使用指南"
echo "• https://agent.qcc.com    - QCC MCP官网"
echo ""
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo ""

# Cleanup temp directory if curl mode
if [ "$INSTALL_MODE" == "curl" ]; then
    rm -rf "$TEMP_DIR"
fi
