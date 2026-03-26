# MCP 配置指南

## 问题说明

**现象**：安装 SKILL 后，Claude Code 没有调用企查查 MCP 服务，而是使用网页搜索。

**原因**：Claude Code 需要通过 `.mcp.json` 配置文件来识别可用的 MCP 服务器和工具。没有这个文件，Claude 不知道 MCP 工具的存在。

## 解决方案

### 方法1：自动安装（推荐）

重新运行安装脚本，它会自动创建 `.mcp.json`：

```bash
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
```

### 方法2：手动配置

如果已经安装了 SKILL，只需要手动创建 `.mcp.json` 文件：

**Step 1: 创建配置文件**

```bash
# 创建 .mcp.json 文件
cat > ~/.claude/.mcp.json << 'EOF'
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
EOF
```

**Step 2: 设置 API Key**

```bash
export QCC_MCP_API_KEY="your_api_key_here"
```

**Step 3: 重启 Claude Code**

```bash
# 完全退出 Claude Code
# 然后重新启动
claude
```

## 验证配置

重启 Claude Code 后，验证 MCP 是否配置成功：

### 验证方法1：查看可用工具

在 Claude Code 中输入任意命令，观察 Claude 是否显示可用的 MCP 工具。

如果配置成功，你应该能看到类似这样的输出：

```
我将使用企查查 MCP 工具来完成这个任务。

可用的 MCP 服务器：
- qcc-company: 企查查企业基座
- qcc-risk: 企查查风控大脑
- qcc-ipr: 企查查知产引擎
- qcc-operation: 企查查经营罗盘
```

### 验证方法2：测试 KYB 核验

```
/kyb-verification-qcc 华为技术有限公司
```

**正确输出**（使用 MCP）：
```
我将通过企查查 MCP 服务对"华为技术有限公司"进行 KYB 核验。

Phase 1: 实体锚定
调用 qcc-company/get_company_registration_info...
[直接返回企业数据]
```

**错误输出**（使用网页搜索）：
```
让我搜索一下这家公司的信息...
网页搜索
华为技术有限公司 工商信息
```

## 常见问题

### Q1: 为什么重启后还是没有 MCP 工具？

**可能原因**：
1. `.mcp.json` 文件路径不对 - 必须在 `~/.claude/.mcp.json`
2. JSON 格式错误 - 检查是否有语法错误
3. Claude Code 版本过旧 - 需要支持 MCP 的版本

**排查步骤**：
```bash
# 检查文件是否存在
ls -la ~/.claude/.mcp.json

# 检查 JSON 格式
python3 -m json.tool ~/.claude/.mcp.json

# 检查文件内容
cat ~/.claude/.mcp.json
```

### Q2: MCP 工具显示但调用失败？

**可能原因**：
1. `QCC_MCP_API_KEY` 未设置
2. API Key 无效
3. 网络问题

**排查步骤**：
```bash
# 检查环境变量
echo $QCC_MCP_API_KEY

# 测试 API 连通性
curl -H "Authorization: Bearer $QCC_MCP_API_KEY" \
  https://agent.qcc.com/mcp/company/stream
```

### Q3: 如何确认 Claude Code 支持 MCP？

```bash
# 查看 Claude Code 版本
claude --version

# MCP 功能需要较新版本
# 如果版本过旧，请更新
# macOS: brew upgrade claude-code
# Linux: 重新下载安装
```

## 配置文件说明

### `.mcp.json` 位置

```
~/.claude/
├── .mcp.json          # ← MCP 配置文件（必须放在这里）
├── skills/
│   ├── kyb-verification-qcc/
│   └── ic-memo-qcc/
└── financial-services-qcc-scripts/
```

### 配置文件结构

```json
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      },
      "description": "服务器描述"
    }
    // ... 其他服务器
  }
}
```

### 环境变量

```bash
# 必须设置
export QCC_MCP_API_KEY="your_api_key_here"

# 可选：设置 API 超时时间（秒）
export QCC_MCP_TIMEOUT="30"
```

## 完整安装流程

```bash
# 1. 安装 SKILL 和 MCP 配置
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)

# 2. 设置 API Key
export QCC_MCP_API_KEY="your_api_key_here"

# 3. 将 API Key 添加到 shell 配置文件（可选但推荐）
echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.zshrc  # macOS
echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.bashrc # Linux

# 4. 重启 Claude Code
# 完全退出后重新启动

# 5. 验证安装
# 在 Claude Code 中运行：
# /kyb-verification-qcc 华为技术有限公司
```

## 技术支持

如有问题，请联系：
- 邮箱：duhu@qcc.com
- 官网：https://mcp.qcc.com
- GitHub Issues：https://github.com/duhu2000/financial-services-qcc/issues
