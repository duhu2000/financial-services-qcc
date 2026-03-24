# 项目结构说明

## 完整目录树

```
financial-services-qcc/
├── README.md                                    # 主文档
├── LICENSE                                      # Apache 2.0
├── CHANGES.md                                   # 变更对比（原版vs增强版）
├── PROJECT_STRUCTURE.md                         # 本文件
├── install_qcc_mcp_financial.sh                 # 一键安装脚本
│
├── investment-banking/                          # 投资银行模块
│   └── skills/
│       └── strip-profile/                       # 企业简况
│           ├── SKILL.original.md                # ✅ Anthropic原版
│           └── README.md                        # (可选)原版说明
│
├── private-equity/                              # 私募股权模块
│   └── skills/
│       └── ic-memo/                             # IC Memo
│           ├── SKILL.original.md                # ✅ Anthropic原版
│           └── README.md                        # (可选)原版说明
│
├── skills/                                      # 企查查MCP增强版
│   ├── kyb-verification-qcc/                    # 🆕 KYB自动化核验
│   │   └── SKILL.md
│   └── ic-memo-qcc/                             # 🆕 IC Memo全维度尽调
│       └── SKILL.md
│
├── scripts/                                     # 工具脚本
│   └── qcc_mcp_connector_financial.py           # 🆕 MCP连接器
│
└── docs/                                        # 文档
    ├── KYB_GUIDE.md                             # KYB使用指南
    └── IC_MEMO_GUIDE.md                         # IC Memo编写指南
```

---

## 文件说明

### 核心文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `README.md` | ~10KB | 用户友好主文档 |
| `LICENSE` | ~11KB | Apache 2.0 许可证 |
| `CHANGES.md` | ~10KB | 原版vs增强版对比 |
| `install_qcc_mcp_financial.sh` | ~8KB | 一键安装脚本 |

### 原版保留文件

| 文件 | 来源 | 说明 |
|------|------|------|
| `investment-banking/skills/strip-profile/SKILL.original.md` | Anthropic | 企业简况原版 |
| `private-equity/skills/ic-memo/SKILL.original.md` | Anthropic | IC Memo原版 |

### 增强版文件

| 文件 | 大小 | 说明 |
|------|------|------|
| `skills/kyb-verification-qcc/SKILL.md` | ~11KB | KYB自动化核验（基于strip-profile） |
| `skills/ic-memo-qcc/SKILL.md` | ~18KB | IC Memo全维度尽调（基于ic-memo） |
| `scripts/qcc_mcp_connector_financial.py` | ~33KB | MCP连接器 |

---

## 与原版的对应关系

```
Anthropic原版                        QCC MCP增强版
─────────────────────────────────────────────────────────────
investment-banking/                  skills/
└── skills/                              ├── kyb-verification-qcc/
    └── strip-profile/                   │   └── SKILL.md (30秒快检)
        └── SKILL.md                     │       ↑ 对应场景
                                          │       银行/金融机构KYB
                                          │
private-equity/                          └── ic-memo-qcc/
└── skills/                                  └── SKILL.md (全维度尽调)
    └── ic-memo/                                 ↑ 对应场景
        └── SKILL.md                             投资尽调/IC Memo

原版: strip-profile → 海外企业简况
增强: kyb-verification-qcc → 中国企业KYB核验

原版: ic-memo → 海外投资尽调
增强: ic-memo-qcc → 中国企业全维度背调
```

---

## 使用方式

### 海外企业
```bash
# 使用原版
/investment-banking/skills/strip-profile/SKILL.original.md
/private-equity/skills/ic-memo/SKILL.original.md
```

### 中国企业
```bash
# 使用增强版
/kyb-verification-qcc 企业名称
/ic-memo-qcc 企业名称
```

---

## 技术实现

### MCP连接器架构
```
qcc_mcp_connector_financial.py
├── QccMcpConnectorFinancial (主类)
│   ├── kyb_fast_verification()      # 30秒快检
│   │   ├── verify_entity()          # 实体锚定
│   │   ├── scan_judicial_risks()    # 司法风险扫描
│   │   ├── identify_ubo()           # 受益所有人识别
│   │   └── calculate_kyb_risk()     # 风险定级
│   │
│   └── ic_full_due_diligence()      # 全维度尽调
│       ├── populate_company_profile()   # 公司概况
│       ├── populate_ip_assets()         # 知识产权
│       ├── populate_judicial_risks()    # 法律风险
│       ├── populate_business_activity() # 经营动态
│       └── generate_ic_memo()           # 报告生成
│
└── MCP_SERVERS (4个Server)
    ├── qcc_company (12个工具)
    ├── qcc_risk (16个工具)
    ├── qcc_ipr (5个工具)
    └── qcc_operation (7个工具)
```

---

## 数据流

```
用户输入企业名称
      ↓
Claude Code 识别 SKILL
      ↓
调用 qcc_mcp_connector_financial.py
      ↓
并行调用 企查查MCP (4个Server)
      ↓
聚合数据 → 风险分析 → 生成报告
      ↓
输出 KYB报告 / IC Memo
```

---

## 安装后结构

```bash
~/.claude/
├── skills/
│   ├── kyb-verification-qcc/
│   │   └── SKILL.md
│   └── ic-memo-qcc/
│       └── SKILL.md
└── financial-services-qcc-scripts/
    └── qcc_mcp_connector_financial.py
```

---

## 贡献指南

### 新增功能
1. 在 `skills/` 目录下创建新SKILL
2. 在 `scripts/` 中添加对应连接器方法
3. 更新 `README.md` 文档
4. 更新 `CHANGES.md` 变更记录

### 更新MCP工具
1. 修改 `scripts/qcc_mcp_connector_financial.py`
2. 更新对应SKILL中的工具调用说明
3. 测试工具可用性

---

## 许可证

Apache License 2.0

原版代码: Copyright Anthropic
增强代码: Copyright 企查查MCP团队
