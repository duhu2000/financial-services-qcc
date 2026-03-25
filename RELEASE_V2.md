# V2 融合版发布说明

## 版本信息

- **版本**: 2.0.0
- **发布日期**: 2025-03-25
- **代号**: Fusion（融合版）

## 设计理念

V2融合版的核心设计原则是：**"不破坏原有SKILL结构，只是增强"**。

基于Manus版本的清晰架构，融入V1版本的开箱即用体验和业务逻辑，实现平滑升级。

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
| Commands模式 | ✅ | ❌ | ✅ **保留** |
| Skills兼容层 | ✅ | ✅ | ✅ **保留** |

## 文件结构对比

### V1版本结构
```
financial-services-qcc/
├── .mcp.json
├── README.md
├── skills/
│   ├── kyb-verification-qcc/SKILL.md
│   └── ic-memo-qcc/SKILL.md
└── scripts/
    └── install_qcc_mcp_financial.sh
```

### Manus版本结构
```
financial-services-plugins/
├── .mcp.json
├── README.md
├── utils/
│   ├── qcc_mcp_client.py
│   ├── kyb_verifier.py
│   └── dd_report_generator.py
├── investment-banking/skills/strip-profile/SKILL.md
├── private-equity/skills/ic-memo/SKILL.md
└── ...
```

### V2融合版结构
```
financial-services-qcc-v2/
├── .mcp.json                          # MCP配置（V1环境变量增强）
├── README.md                          # 英文文档（融合版）
├── README_zh-CN.md                    # 中文文档（V1保留）
├── UNINSTALL.md                       # 卸载指南（V1保留）
├── commands/                          # 命令定义（Manus方式+新增）
│   ├── qcc-kyb-profile.md            # KYB命令
│   └── qcc-full-dd-profile.md        # 尽调命令
├── utils/                             # Python工具类（Manus+V1增强）
│   ├── __init__.py
│   ├── qcc_mcp_client.py             # MCP客户端（多路径+重试）
│   ├── kyb_verifier.py               # KYB核验器（A/B/C/D评级）
│   ├── dd_report_generator.py        # 尽调报告（7章IC Memo）
│   └── config_manager.py             # 配置管理器（V1新增）
├── investment-banking/skills/         # 投行业务（兼容层）
│   └── strip-profile/SKILL.md        # 简况生成
├── private-equity/skills/             # PE业务（兼容层）
│   └── ic-memo/SKILL.md              # IC Memo生成
├── scripts/                           # 安装脚本（V1增强）
│   └── install_qcc_mcp_financial.sh  # 一键安装
└── docs/                              # 文档（V1保留）
    └── MCP_CONFIGURATION.md          # 配置故障排查
```

## 核心增强点

### 1. MCP客户端 (qcc_mcp_client.py)

**Manus基础**: SSE流式响应处理
**V1增强**:
- 多路径配置查找（当前目录 → ~/.claude/ → 父目录）
- 环境变量回退机制（支持${QCC_MCP_API_KEY}语法）
- 错误重试机制（默认2次重试）
- 服务健康检查

### 2. KYB核验器 (kyb_verifier.py)

**Manus基础**: 基础核验流程
**V1增强**:
- 4阶段工作流（实体锚定→股权穿透→风险扫描→评级）
- A/B/C/D四级评级系统
- 18类风险完整分类（CRITICAL/HIGH/MEDIUM/LOW）
- 受益所有人（UBO）识别（25%规则）
- 详细控制台输出

### 3. 尽调报告生成器 (dd_report_generator.py)

**Manus基础**: 基础数据收集
**V1增强**:
- 7章IC Memo结构
- 知识产权核心竞争力评估
- 法律风险分级摘要
- 投资建议与风险提示
- 执行摘要自动生成

### 4. 配置管理器 (config_manager.py)

**V2新增**（融合V1的自动配置理念）:
- 自动创建.mcp.json
- 配置验证
- 配置修复
- 诊断信息输出
- 环境变量检查

### 5. 安装脚本 (install_qcc_mcp_financial.sh)

**V1基础**: 一键安装
**V2增强**:
- 支持Commands安装
- 支持Utils安装
- 版本检测
- 详细安装报告

## 使用方式对比

### KYB核验

**V1方式**:
```
/kyb-verification-qcc 华为技术有限公司
```

**V2方式（Commands推荐）**:
```
/qcc-kyb-profile 华为技术有限公司
/qcc-kyb-profile 华为技术有限公司 9144030019237xxxxx
```

**V2方式（Skills兼容）**:
```
/strip-profile 华为技术有限公司  # 内部调用KYB
```

**Python API**:
```python
from utils.kyb_verifier import KYBVerifier

verifier = KYBVerifier()
results = verifier.verify_company("华为技术有限公司")
# 返回: {kyb_rating: "A", verification_suggestion: "...", ...}
```

### 尽调报告

**V1方式**:
```
/ic-memo-qcc 北京字节跳动科技有限公司
```

**V2方式（Commands推荐）**:
```
/qcc-full-dd-profile 北京字节跳动科技有限公司
/qcc-full-dd-profile 宁德时代 --round Pre-IPO --sector 新能源
```

**V2方式（Skills兼容）**:
```
/ic-memo 北京字节跳动科技有限公司
```

**Python API**:
```python
from utils.dd_report_generator import DDReportGenerator

generator = DDReportGenerator()
report = generator.generate_full_dd_profile(
    company_name="北京字节跳动科技有限公司",
    investment_round="Series B"
)
# 返回: {chapters: {...}, summary: "...", ...}
```

## 升级指南

### 从V1升级到V2

1. **备份现有配置**
   ```bash
   cp ~/.claude/.mcp.json ~/.claude/.mcp.json.backup
   cp -r ~/.claude/skills/kyb-verification-qcc ~/.claude/skills/kyb-verification-qcc.backup
   cp -r ~/.claude/skills/ic-memo-qcc ~/.claude/skills/ic-memo-qcc.backup
   ```

2. **运行V2安装脚本**
   ```bash
   bash <(curl -sL https://raw.githubusercontent.com/duhu2000/financial-services-qcc/main/install_qcc_mcp_financial.sh)
   ```

3. **重启Claude Code**

4. **验证安装**
   ```
   /qcc-kyb-profile 华为技术有限公司
   ```

### 回滚到V1

```bash
# 恢复备份
mv ~/.claude/.mcp.json.backup ~/.claude/.mcp.json
rm -rf ~/.claude/skills/kyb-verification-qcc
rm -rf ~/.claude/skills/ic-memo-qcc
mv ~/.claude/skills/kyb-verification-qcc.backup ~/.claude/skills/kyb-verification-qcc
mv ~/.claude/skills/ic-memo-qcc.backup ~/.claude/skills/ic-memo-qcc
```

## 技术亮点

### 1. 多层级配置查找
```python
config_paths = [
    mcp_config_path,                      # 指定路径
    os.path.expanduser("~/.claude/.mcp.json"),  # 推荐路径
    "./.mcp.json",                        # 当前目录
    "../.mcp.json"                        # 父目录
]
```

### 2. 环境变量回退
当配置文件不存在时，自动从环境变量加载配置，确保服务可用性。

### 3. SSE响应完整处理
完整解析MCP服务的SSE流式响应，支持错误事件检测。

### 4. 智能重试机制
网络异常时自动重试，提高服务稳定性。

## 性能指标

| 操作 | 时间 | 说明 |
|------|------|------|
| KYB核验 | ~30秒 | 4阶段完整流程 |
| 实体锚定 | ~5秒 | 工商信息查询 |
| 股权穿透 | ~8秒 | 股东+UBO识别 |
| 风险扫描 | ~15秒 | 18类风险 |
| 尽调报告 | ~60秒 | 7章完整报告 |

## 后续规划

### V2.1（计划）
- [ ] asyncio异步支持（并行调用提速）
- [ ] 缓存机制（减少重复查询）
- [ ] 批量核验支持
- [ ] 报告导出格式（PDF/Word）

### V2.2（计划）
- [ ] Web界面
- [ ] 数据库持久化
- [ ] 定时监控任务
- [ ] API服务封装

## 贡献指南

欢迎贡献代码！请遵循以下规范：

1. 保持Manus架构风格
2. 保留V1的健壮性特性
3. 添加适当的错误处理
4. 更新中英文文档
5. 添加测试用例

## 许可证

Apache License 2.0

---

**致谢**: 感谢Manus版本和V1版本的贡献者们！
