# GitHub 上传指南

## 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `financial-services-qcc`
   - **Description**: 金融机构企查查MCP增强版插件 - KYB自动化核验 & IC Memo全维度尽调
   - **Visibility**: Public
   - **Add README**: ❌ 不要勾选（已有 README）
   - **Add .gitignore**: ❌ 不要勾选
   - **Choose a license**: ❌ 不要勾选（已有 LICENSE）
3. 点击 **Create repository**

## 步骤 2: 推送代码

在终端执行以下命令：

```bash
cd /Users/qcc/.claude/legal-assistant-skills/financial-services-qcc-complete

# 添加远程仓库
git remote add origin https://github.com/duhu2000/financial-services-qcc.git

# 推送到 main 分支
git push -u origin main
```

## 步骤 3: 验证上传

推送完成后，访问：
```
https://github.com/duhu2000/financial-services-qcc
```

确认以下文件已上传：
- ✅ README.md
- ✅ LICENSE
- ✅ CHANGES.md
- ✅ PROJECT_STRUCTURE.md
- ✅ install_qcc_mcp_financial.sh
- ✅ investment-banking/skills/strip-profile/SKILL.original.md
- ✅ private-equity/skills/ic-memo/SKILL.original.md
- ✅ skills/kyb-verification-qcc/SKILL.md
- ✅ skills/ic-memo-qcc/SKILL.md
- ✅ scripts/qcc_mcp_connector_financial.py

## 一键安装命令

上传后，用户可以通过以下命令安装：

```bash
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
```

## 仓库地址

```
https://github.com/duhu2000/financial-services-qcc
```
