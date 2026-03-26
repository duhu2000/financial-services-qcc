# 企查查MCP金融插件 V2 融合版

基于Manus架构 + V1增强的金融机构企查查MCP插件

## 概述

本插件为银行、券商、信托、PE/VC等金融机构提供企业客户自动化核验(KYB)和投融资尽调(IC Memo)能力，通过企查查MCP服务获取实时、权威的企业工商信息、风险信号、知识产权和经营动态。

**V2版本特性：**
- ✅ 基于Manus架构的清晰目录结构 (commands/utils/skills)
- ✅ 保留V1的开箱即用体验 (一键安装、中文文档)
- ✅ 支持Commands和Skills双模式 (向前兼容)
- ✅ A/B/C/D四级KYB评级 (V1业务逻辑)
- ✅ 7章IC Memo尽调报告 (V1业务逻辑)
- ✅ 18类风险全面扫描
- ✅ 自动配置管理器 (config_manager.py)

## 架构对比

| 特性 | Manus版本 | V1版本 | **V2融合版** |
|------|-----------|--------|--------------|
| 架构清晰度 | ✅ | ⚠️ | ✅ **增强** |
| 开箱即用 | ⚠️ | ✅ | ✅ **保留** |
| 中文文档 | ⚠️ | ✅ | ✅ **保留** |
| 业务逻辑完整度 | ⚠️基础 | ✅完整 | ✅ **完整** |
| Python工具封装 | ✅ | ⚠️ | ✅ **保留** |
| 自动配置 | ⚠️ | ✅ | ✅ **增强** |
| 错误处理 | ⚠️ | ✅ | ✅ **融合** |

## 目录结构

```
financial-services-qcc-v2/
├── .mcp.json                          # MCP服务配置（支持环境变量）
├── README.md                          # 英文文档
├── README_zh-CN.md                    # 中文文档（本文档）
├── UNINSTALL.md                       # 卸载指南
├── commands/                          # 命令定义（主推方式）
│   ├── qcc-kyb-profile.md            # KYB核验命令
│   └── qcc-full-dd-profile.md        # 全维度尽调命令
├── utils/                             # Python工具类
│   ├── __init__.py
│   ├── qcc_mcp_client.py             # MCP客户端（多路径配置+重试机制）
│   ├── kyb_verifier.py               # KYB核验器（4阶段+A/B/C/D评级）
│   ├── dd_report_generator.py        # 尽调报告生成器（7章IC Memo）
│   └── config_manager.py             # 配置管理器（自动创建/修复配置）
├── investment-banking/skills/         # 投行业务技能（兼容层）
│   └── strip-profile/SKILL.md        # 公司简况生成
├── private-equity/skills/             # PE业务技能（兼容层）
│   └── ic-memo/SKILL.md              # IC Memo生成
├── scripts/                           # 脚本
│   └── install_qcc_mcp_financial.sh  # 一键安装脚本
└── docs/                              # 文档
    └── MCP_CONFIGURATION.md          # MCP配置故障排查
```

## 快速安装

### 方式一：一键安装（推荐）

```bash
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
```

### 方式二：本地安装

```bash
git clone https://github.com/duhu2000/financial-services-qcc.git
cd financial-services-qcc
bash scripts/install_qcc_mcp_financial.sh
```

### 安装前准备

1. **获取API Key**
   - 访问 [企查查MCP平台](https://mcp.qcc.com)
   - 注册账号并获取API Key

2. **设置环境变量**

   ```bash
   # macOS/Linux
   export QCC_MCP_API_KEY="your_api_key_here"

   # 添加到配置文件永久生效
   echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.zshrc  # macOS
   echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.bashrc # Linux
   ```

3. **重启Claude Code**

   ⚠️ **必须完全退出并重新启动Claude Code才能加载MCP配置！**

## 使用方法

### Commands模式（V2推荐）

#### KYB企业核验

```
/qcc-kyb-profile 华为技术有限公司
/qcc-kyb-profile 北京字节跳动科技有限公司 91110108MA00xxxxxx
```

**执行流程：**
1. **Phase 1**: 实体锚定（5秒）
   - 验证企业名称与统一社会信用代码
   - 获取工商注册信息

2. **Phase 2**: 股权穿透与UBO识别（8秒）
   - 获取股东结构
   - 识别持股≥25%的自然人股东

3. **Phase 3**: 18类风险全面扫描（15秒）
   - CRITICAL级风险：失信、被执行、限高、破产、股权冻结
   - HIGH级风险：经营异常、严重违法、行政处罚
   - MEDIUM级风险：股权出质、动产抵押、欠税
   - LOW级风险：涉诉信息、裁判文书

4. **Phase 4**: 经营健康度与评级（2秒）
   - 生成A/B/C/D四级评级
   - 输出准入建议

**KYB评级标准：**

| 评级 | 含义 | 处理建议 |
|------|------|----------|
| **A** | 正常准入 | 主体合法存续，无明显风险信号，可按标准流程处理 |
| **B** | 审慎准入+加强监测 | 存在中等风险或经营异常，建议增加监测频率 |
| **C** | 需人工复核 | 存在高风险项，建议加强尽调，提交风险管理部门审批 |
| **D** | 禁止准入 | 存在关键风险项，建议立即启动风险预警流程，终止业务办理 |

#### 全维度尽调

```
/qcc-full-dd-profile 目标企业名称
/qcc-full-dd-profile 宁德时代新能源科技股份有限公司 --round Pre-IPO --sector 新能源
```

**生成7章IC Memo报告：**
1. **执行摘要** - 投资亮点、关注点、关键指标
2. **公司概况与股权结构** - 工商信息、股权穿透、UBO识别
3. **知识产权与核心竞争力** - 专利布局、商标品牌、技术壁垒
4. **法律与合规风险** - 涉诉情况、18类风险扫描、合规结论
5. **经营与市场分析** - 招投标活跃度、资质证书、舆情监控
6. **财务分析** - （需外部数据补充）
7. **投资建议与风险提示** - 投资建议、风险等级、关键条款

### Skills模式（兼容V1）

#### 投行简况生成

```
/strip-profile 目标公司
```

生成投资银行标准格式的公司简况（Strip Profile），适合pitch book使用。

#### IC Memo生成

```
/ic-memo 目标公司
```

生成投资委员会备忘录，自动整合企查查数据。

### Python API（程序化调用）

```python
from utils.kyb_verifier import KYBVerifier
from utils.dd_report_generator import DDReportGenerator

# KYB核验
verifier = KYBVerifier()
results = verifier.verify_company("华为技术有限公司")
print(f"KYB评级: {results['kyb_rating']}")
print(f"核验建议: {results['verification_suggestion']}")

# 尽调报告
generator = DDReportGenerator()
report = generator.generate_full_dd_profile(
    company_name="北京字节跳动科技有限公司",
    investment_round="Series B",
    sector="互联网"
)
```

## MCP服务说明

本插件使用企查查4个MCP服务：

| 服务ID | 名称 | 功能 | 工具数量 |
|--------|------|------|---------|
| **qcc-company** | 企业基座 | 工商登记、股东信息、变更记录、分支机构 | 10 |
| **qcc-risk** | 风控大脑 | 失信、被执行、限高、破产等18类风险 | 17 |
| **qcc-ipr** | 知产引擎 | 专利、商标、软件著作权、作品著作权 | 5 |
| **qcc-operation** | 经营罗盘 | 招投标、资质证书、信用评级、舆情 | 7 |

## 配置管理

### 自动配置

使用config_manager自动创建和修复配置：

```python
from utils.config_manager import ConfigManager

manager = ConfigManager()

# 创建配置
success, msg = manager.create_config()
print(msg)

# 验证配置
is_valid, errors = manager.validate_config()

# 修复配置
success, msg = manager.fix_config()
print(msg)

# 诊断信息
manager.print_diagnostic()
```

### 配置文件路径

V2支持多路径配置查找（按优先级）：
1. `./.mcp.json` （当前目录）
2. `~/.claude/.mcp.json` （推荐）
3. `../.mcp.json` （父目录）
4. 环境变量回退

### 环境变量支持

配置文件支持 `${QCC_MCP_API_KEY}` 语法：

```json
{
  "mcpServers": {
    "qcc-company": {
      "url": "https://agent.qcc.com/mcp/company/stream",
      "headers": {
        "Authorization": "Bearer ${QCC_MCP_API_KEY}"
      }
    }
  }
}
```

## 故障排查

详见 [docs/MCP_CONFIGURATION.md](docs/MCP_CONFIGURATION.md)

### 常见问题

**Q: MCP工具未加载**
```bash
# 1. 检查配置文件是否存在
ls -la ~/.claude/.mcp.json

# 2. 检查环境变量
echo $QCC_MCP_API_KEY

# 3. 验证配置
python3 -c "from utils.config_manager import ConfigManager; ConfigManager().print_diagnostic()"

# 4. 完全退出并重启Claude Code
```

**Q: 查询返回空数据**
- 确认企业名称准确（使用工商注册全称）
- 检查API Key是否有效
- 查看网络连接

**Q: 配置文件格式错误**
```bash
# 使用config_manager修复
python3 -c "from utils.config_manager import ConfigManager; ConfigManager().fix_config()"
```

## 卸载

详见 [UNINSTALL.md](UNINSTALL.md)

```bash
# 一键卸载
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/uninstall.sh)
```

或手动卸载：
```bash
# 删除安装目录
rm -rf ~/.claude/financial-services-qcc
rm -rf ~/.claude/skills/investment-banking-qcc
rm -rf ~/.claude/skills/private-equity-qcc
rm -rf ~/.claude/commands/qcc-kyb-profile.md
rm -rf ~/.claude/commands/qcc-full-dd-profile.md

# 可选：删除MCP配置
rm -f ~/.claude/.mcp.json
```

## 版本历史

- **V2.0.0** (2025-03-25) - 融合版发布
  - 基于Manus架构重构目录结构
  - 添加Commands模式（qcc-kyb-profile, qcc-full-dd-profile）
  - 保留Skills模式作为兼容层
  - 增强KYB评级逻辑（A/B/C/D四级）
  - 添加config_manager自动配置管理
  - 优化多路径配置查找
  - 增强错误处理和重试机制

- **V1.x** (2025-03) - 初始版本
  - 基础KYB核验
  - 基础IC Memo生成
  - 一键安装脚本
  - 中文文档

## 技术支持

- 企查查MCP平台: https://mcp.qcc.com
- GitHub Issues: https://github.com/duhu2000/financial-services-qcc/issues
- 邮箱: duhu@qcc.com

## 许可证

Apache License 2.0

---

**免责声明**: 本工具生成的报告仅供参考，最终业务决策请结合人工尽调和专业判断。
