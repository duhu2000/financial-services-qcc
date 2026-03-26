# 卸载与重新安装指南

## 方法一：一键卸载脚本（推荐）

### 1. 创建卸载脚本

```bash
cat > /tmp/uninstall_qcc_mcp.sh << 'EOF'
#!/bin/bash
# 企查查MCP插件卸载脚本

set -e

echo "========================================"
echo "  企查查MCP插件卸载程序"
echo "========================================"
echo ""

# 定义目录
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"

# 卸载 financial-services-qcc
echo "卸载 financial-services-qcc..."
if [ -d "$SKILLS_DIR/kyb-verification-qcc" ]; then
    rm -rf "$SKILLS_DIR/kyb-verification-qcc"
    echo "  ✓ 已删除 kyb-verification-qcc"
else
    echo "  - kyb-verification-qcc 不存在，跳过"
fi

if [ -d "$SKILLS_DIR/ic-memo-qcc" ]; then
    rm -rf "$SKILLS_DIR/ic-memo-qcc"
    echo "  ✓ 已删除 ic-memo-qcc"
else
    echo "  - ic-memo-qcc 不存在，跳过"
fi

if [ -d "$CLAUDE_DIR/financial-services-qcc-scripts" ]; then
    rm -rf "$CLAUDE_DIR/financial-services-qcc-scripts"
    echo "  ✓ 已删除 financial-services-qcc-scripts"
fi

# 卸载 vendor-assessment-qcc
echo ""
echo "卸载 vendor-assessment-qcc..."
if [ -d "$SKILLS_DIR/vendor-assessment-qcc" ]; then
    rm -rf "$SKILLS_DIR/vendor-assessment-qcc"
    echo "  ✓ 已删除 vendor-assessment-qcc"
else
    echo "  - vendor-assessment-qcc 不存在，跳过"
fi

if [ -d "$CLAUDE_DIR/vendor-assessment-qcc-scripts" ]; then
    rm -rf "$CLAUDE_DIR/vendor-assessment-qcc-scripts"
    echo "  ✓ 已删除 vendor-assessment-qcc-scripts"
fi

# 卸载 supply-chain-qcc
echo ""
echo "卸载 supply-chain-qcc..."
for skill in vendor-assessment-qcc supplier-risk-qcc invoice-reconciliation \
             spend-analysis logistics-brief supply-chain-brief \
             vendor-communication network-design; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        rm -rf "$SKILLS_DIR/$skill"
        echo "  ✓ 已删除 $skill"
    fi
done

if [ -d "$CLAUDE_DIR/supply-chain-qcc-scripts" ]; then
    rm -rf "$CLAUDE_DIR/supply-chain-qcc-scripts"
    echo "  ✓ 已删除 supply-chain-qcc-scripts"
fi

# 删除 MCP 配置（可选）
echo ""
read -p "是否删除 MCP 配置文件 ~/.claude/.mcp.json? (y/N): " delete_mcp
if [[ "$delete_mcp" =~ ^[Yy]$ ]]; then
    if [ -f "$CLAUDE_DIR/.mcp.json" ]; then
        rm -f "$CLAUDE_DIR/.mcp.json"
        echo "  ✓ 已删除 .mcp.json"
    fi
else
    echo "  - 保留 .mcp.json"
fi

echo ""
echo "========================================"
echo "  卸载完成"
echo "========================================"
echo ""
echo "请完全退出并重启 Claude Code 以生效"
echo ""
EOF

chmod +x /tmp/uninstall_qcc_mcp.sh
bash /tmp/uninstall_qcc_mcp.sh
```

## 方法二：手动卸载

### 1. 删除 SKILL 目录

```bash
# 删除 financial-services-qcc SKILL
rm -rf ~/.claude/skills/kyb-verification-qcc
rm -rf ~/.claude/skills/ic-memo-qcc
rm -rf ~/.claude/financial-services-qcc-scripts

# 删除 vendor-assessment-qcc SKILL
rm -rf ~/.claude/skills/vendor-assessment-qcc
rm -rf ~/.claude/vendor-assessment-qcc-scripts

# 删除 supply-chain-qcc SKILL
rm -rf ~/.claude/skills/vendor-assessment-qcc
rm -rf ~/.claude/skills/supplier-risk-qcc
rm -rf ~/.claude/skills/invoice-reconciliation
rm -rf ~/.claude/skills/spend-analysis
rm -rf ~/.claude/skills/logistics-brief
rm -rf ~/.claude/skills/supply-chain-brief
rm -rf ~/.claude/skills/vendor-communication
rm -rf ~/.claude/skills/network-design
rm -rf ~/.claude/supply-chain-qcc-scripts

# 删除 legal-assistant-skills
rm -rf ~/.claude/skills/contract-review
rm -rf ~/.claude/legal-assistant-skills-scripts
```

### 2. 删除 MCP 配置（可选）

```bash
# 删除 MCP 配置文件
rm -f ~/.claude/.mcp.json
```

### 3. 重启 Claude Code

```bash
# 完全退出 Claude Code（重要！）
# 然后重新启动
claude
```

## 重新安装

### 方案一：全新安装（推荐）

```bash
# 1. 一键安装 financial-services-qcc
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)

# 2. 设置 API Key
export QCC_MCP_API_KEY="your_api_key_here"

# 3. ⚠️ 重启 Claude Code（关键！）

# 4. 测试
/kyb-verification-qcc 华为技术有限公司
```

### 方案二：仅更新 MCP 配置

如果 SKILL 本身没问题，只是 MCP 配置问题：

```bash
# 1. 重新创建 MCP 配置
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      }
    },
    "qcc-risk": {
      "url": "https://agent.qcc.com/mcp/risk/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      }
    },
    "qcc-ipr": {
      "url": "https://agent.qcc.com/mcp/ipr/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      }
    },
    "qcc-operation": {
      "url": "https://agent.qcc.com/mcp/operation/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      }
    }
  }
}
EOF

# 2. 重启 Claude Code
# 完全退出后重新启动

# 3. 验证 MCP 配置已加载
```

## 验证安装

### 检查文件是否存在

```bash
# 检查 SKILL
ls -la ~/.claude/skills/

# 检查 MCP 配置
ls -la ~/.claude/.mcp.json

# 查看 MCP 配置内容
cat ~/.claude/.mcp.json
```

### 在 Claude Code 中验证

重启 Claude Code 后，执行：

```
/kyb-verification-qcc 华为技术有限公司
```

**正确的输出**（使用 MCP）：
```
我将通过企查查 MCP 服务对"华为技术有限公司"进行 KYB 核验。
Phase 1: 实体锚定
调用 qcc-company/get_company_registration_info...
```

**错误的输出**（使用网页搜索）：
```
让我搜索一下这家公司的信息...
网页搜索
华为技术有限公司 工商信息
```

## 常见问题

### Q: 卸载后需要删除 API Key 吗？
A: 不需要。API Key 是环境变量，可以保留供重新安装使用。

### Q: 如何保留备份？

```bash
# 备份现有配置
mkdir -p ~/qcc-backup-$(date +%Y%m%d)
cp -r ~/.claude/skills ~/qcc-backup-$(date +%Y%m%d)/
cp ~/.claude/.mcp.json ~/qcc-backup-$(date +%Y%m%d)/ 2>/dev/null || true
```

### Q: 安装后如何验证版本？

```bash
# 查看 SKILL 版本
cat ~/.claude/skills/kyb-verification-qcc/SKILL.md | grep "version:"

# 查看 Git 提交记录
cd ~/.claude/skills/kyb-verification-qcc && git log --oneline -3 2>/dev/null || echo "Not a git repo"
```

## 完整重装流程

```bash
# 1. 卸载旧版本
bash /tmp/uninstall_qcc_mcp.sh

# 2. 完全退出 Claude Code
# (Cmd+Q 或 kill 进程)

# 3. 等待 5 秒确保进程完全退出
sleep 5

# 4. 重新安装
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)

# 5. 设置 API Key
export QCC_MCP_API_KEY="your_api_key_here"

# 6. 重启 Claude Code
claude

# 7. 测试
/kyb-verification-qcc 华为技术有限公司
```

---

如有问题，请联系：duhu@qcc.com
