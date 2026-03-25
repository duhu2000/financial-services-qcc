# Financial Services QCC MCP Plugin V2

企查查MCP金融插件V2融合版 - 基于Manus架构 + V1增强

## 概述

本插件为金融机构提供企业客户自动化核验(KYB)和投融资尽调(IC Memo)能力，通过企查查MCP服务获取实时、权威的企业工商信息、风险信号、知识产权和经营动态。

**V2版本特性：**
- ✅ 基于Manus架构的清晰目录结构
- ✅ 保留V1的开箱即用体验
- ✅ 支持Commands和Skills双模式
- ✅ A/B/C/D四级KYB评级
- ✅ 7章IC Memo尽调报告
- ✅ 18类风险全面扫描

## 架构设计

```
financial-services-qcc-v2/
├── .mcp.json                          # MCP服务配置
├── commands/                          # 命令定义（主推方式）
│   ├── qcc-kyb-profile.md            # KYB核验命令
│   └── qcc-full-dd-profile.md        # 全维度尽调命令
├── utils/                             # Python工具类
│   ├── __init__.py
│   ├── qcc_mcp_client.py             # MCP客户端
│   ├── kyb_verifier.py               # KYB核验器
│   ├── dd_report_generator.py        # 尽调报告生成器
│   └── config_manager.py             # 配置管理器
├── investment-banking/skills/         # 投行业务技能
│   └── strip-profile/SKILL.md        # 公司简况生成
├── private-equity/skills/             # PE业务技能
│   └── ic-memo/SKILL.md              # IC Memo生成
├── scripts/                           # 安装脚本
│   └── install_qcc_mcp_financial.sh  # 一键安装脚本
├── docs/                              # 文档
│   └── MCP_CONFIGURATION.md          # MCP配置指南
└── UNINSTALL.md                       # 卸载指南
```

## 快速安装

### 一键安装（推荐）

```bash
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
```

### 本地安装

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

   # 添加到配置文件使其永久生效
   echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.zshrc  # macOS
   echo 'export QCC_MCP_API_KEY="your_api_key_here"' >> ~/.bashrc # Linux
   ```

3. **重启Claude Code**

   完全退出并重新启动Claude Code以加载MCP配置。

## 使用方法

### 方式一：Commands（推荐）

#### KYB企业核验

```
/qcc-kyb-profile 华为技术有限公司
/qcc-kyb-profile 北京字节跳动科技有限公司 91110108MA00xxxxxx
```

**输出示例：**
```
========================================
[KYBVerifier] 开始企业 KYB 自动化核验
========================================
目标企业: 华为技术有限公司
========================================

========================================
[Phase 1] 实体锚定 - 主体信息核验
========================================
[Phase 1] 查询企业工商注册信息...
  ✅ 实体锚定成功
     企业名称: 华为技术有限公司
     统一社会信用代码: 9144030019237xxxxx
     法定代表人: 赵明路
     经营状态: 存续

========================================
[Phase 2] 股权穿透与UBO识别
========================================
  ✅ 股东数量: 2
  ✅ 识别UBO: 1 人
     - 华为投资控股有限公司: 100%

========================================
[Phase 3] 18类风险全面扫描
========================================
  ✅ 风险扫描完成
     🔴 关键风险: 0 项
     🟠 高风险: 0 项
     🟡 中风险: 0 项
     🔵 低风险: 0 项

========================================
[Phase 4] 经营健康度评估与评级
========================================

========================================
[评级计算]
========================================

========================================
[KYBVerifier] 核验完成
企业名称: 华为技术有限公司
KYB评级: A
核验结论: 🟢 正常准入 - 主体合法存续，无明显风险信号，可按标准流程处理。
========================================
```

#### 全维度尽调

```
/qcc-full-dd-profile 目标企业名称
/qcc-full-dd-profile 宁德时代新能源科技股份有限公司 --round Pre-IPO --sector 新能源
```

**生成7章IC Memo报告：**
1. 执行摘要
2. 公司概况与股权结构
3. 知识产权与核心竞争力
4. 法律与合规风险
5. 经营与市场分析
6. 财务分析（需外部数据补充）
7. 投资建议与风险提示

### 方式二：Skills（兼容模式）

#### 投行简况生成

```
/strip-profile 目标公司
```

生成投资银行标准格式的公司简况（Strip Profile），包含：
- 公司概况
- 业务与定位
- 关键财务数据
- 股东/最新动态

#### IC Memo生成

```
/ic-memo 目标公司
```

生成投资委员会备忘录，自动整合企查查数据：
- 工商注册信息
- 股权穿透分析
- 风险信号扫描
- 知识产权资产
- 经营动态

### 方式三：Python API

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

| 服务 | 功能 | 工具 |
|------|------|------|
| **qcc-company** | 企业基座 | 工商登记、股东信息、变更记录 |
| **qcc-risk** | 风控大脑 | 失信、被执行、限高、破产等18类风险 |
| **qcc-ipr** | 知产引擎 | 专利、商标、软件著作权 |
| **qcc-operation** | 经营罗盘 | 招投标、资质证书、舆情 |

## KYB评级标准

| 评级 | 含义 | 处理建议 |
|------|------|----------|
| **A** | 正常准入 | 主体合法存续，无明显风险信号 |
| **B** | 审慎准入+加强监测 | 存在中等风险，增加监测频率 |
| **C** | 需人工复核 | 存在高风险，加强尽调 |
| **D** | 禁止准入 | 存在关键风险，终止业务办理 |

## 18类风险扫描

**CRITICAL级（<4小时响应）：**
- 失信被执行人
- 被执行人
- 限制高消费
- 破产重整
- 股权冻结
- 司法协助

**HIGH级（<24小时响应）：**
- 经营异常
- 严重违法
- 行政处罚
- 环保处罚

**MEDIUM级（关注）：**
- 股权出质
- 动产抵押
- 欠税公告
- 税务非正常
- 税收违法

**LOW级（备案）：**
- 涉诉信息
- 裁判文书

## 故障排查

详见 [docs/MCP_CONFIGURATION.md](docs/MCP_CONFIGURATION.md)

### 常见问题

**Q: MCP工具未加载**
- 检查`~/.claude/.mcp.json`是否存在
- 检查`QCC_MCP_API_KEY`环境变量是否设置
- 完全退出并重启Claude Code

**Q: 查询返回空数据**
- 确认企业名称准确（使用工商注册全称）
- 检查API Key是否有效
- 查看网络连接

## 卸载

详见 [UNINSTALL.md](UNINSTALL.md)

```bash
# 一键卸载
bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/uninstall.sh)
```

## 版本历史

- **V2.0.0** (2025-03) - 融合版发布
  - 基于Manus架构重构
  - 添加Commands模式
  - 保留Skills兼容层
  - 增强KYB评级逻辑
  - 优化安装体验

- **V1.x** (2025-03) - 初始版本
  - 基础KYB核验
  - 基础IC Memo生成
  - 一键安装脚本

## 技术支持

- 企查查MCP平台: https://mcp.qcc.com
- GitHub Issues: https://github.com/duhu2000/financial-services-qcc/issues
- 邮箱: duhu@qcc.com

## 许可证

Apache License 2.0

---

**注意**: 本工具生成的报告仅供参考，最终业务决策请结合人工尽调和专业判断。
