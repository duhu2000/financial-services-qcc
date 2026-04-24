---
name: history-evolution-qcc
description: >
  企业历史沿革与发展历程分析 Skill — 企查查MCP驱动的KYB立体叙事报告生成器。
  基于企查查 MCP 146 个工具自动生成 9 章 + 附录的 KYB 历史沿革报告。

  核心功能：
  - 9 章结构：§0 里程碑总览 / §1 公司概况 / §2 注册资本 / §3 名称变更 / §4 股权演变
    / §5 经营轨迹 / §6 地址变迁 / §7 总结 / §8 发展综览 / §附录 工商变更大事年表
  - 立体叙事：许可资质矩阵、知识产权布局、业务扩张与员工规模、行业地位与荣誉
  - 档位自适应：小微（¥4.5）/ 融资（¥13）/ 上市（¥18）三档自动识别并差异化调用
  - 视觉风格：圆点+竖线时间轴 + kyb-opus 风格表格，可直接出 DOCX/PDF

  适用场景：投前尽调（PE/VC）、IC Memo 附件生成、银行授信 KYB、IPO 辅导前历史梳理、
  供应商主体背调、管理层背景与发展历程核查。

  使用方式：/history-evolution-qcc 企业名称 [统一社会信用代码]

license: Apache-2.0
metadata:
  author: Anthropic Financial Services (Enhanced with QCC MCP)
  version: "1.1.3"
  plugin-commands: "/history-evolution-qcc"
  mcp-integrations: "QCC MCP (Company/Risk/IPR/Operation/History/Executive)"
  industry: "Financial Services - Investment DD / Banking / Supply Chain"
---

# 企业历史沿革与发展历程分析 SKILL（V1.1.3）

## 定位（V1.0 硬约束）

- **数据源唯一**：企查查 MCP 共 138 个工具（`qcc-company` 14 + `qcc-risk` 34 + `qcc-ipr` 6 + `qcc-operation` 14+1 + `qcc-history` 34 + `qcc-executive` 35）
- **输出原则**：MCP 能拿到 → 写进章节；拿不到 → 章节不出现，**不留空占位、不要求客户补材料**
- **客户负担**：零。客户只需连接企查查 MCP，提供目标企业名称/统一社会信用代码即可
- **升级路径**：客户如需补充非公示数据（代持、承诺函、关联交易明细等），请参考 `references/06_V2.0客户自升级指引.md` 自行扩展至 V2.0，本 SKILL 作者不提供 V2.0 模板或支持

## 执行工作流（调用 SKILL 后 Claude 应遵循的步骤）

### 步骤 1 · 收集输入

从用户消息中识别：
- 目标企业名称 或 统一社会信用代码（必需）
- 报告用途（可选：信贷尽调 / IPO 辅导 / 投前尽调 / 合规 KYB）——仅用于语气调节，不影响字段清单

### 步骤 2 · 档位识别（先调用 3 个 5c 工具，共 15c）

按 `references/04_档位识别规则.md` 的决策树：
1. `mcp__qcc-company__get_company_profile`（5c）——获取基本信息
2. `mcp__qcc-company__get_listing_info`（5c）——判断上市状态
3. `mcp__qcc-operation__get_financing_records`（5c）——判断融资阶段

按以下规则判定档位：
- **上市档**：已上市 或 发债（A 股/港股/美股 或 有债券发行记录）
- **融资档**：未上市但有融资记录（天使—Pre-IPO 任一轮次）
- **小微档**：无上市、无融资记录、注册资本 ≤ 1000 万 或 人员规模 ≤ 50 人

### 步骤 3 · 按档位批量调用 MCP 工具

按 `references/05_工具调用清单.md` 中对应档位的工具清单，使用 `scripts/mcp_orchestrator.py` 的 `call_tools_by_tier()` 方法批量调用。

**成本控制**（由 `scripts/cost_counter.py` 自动强制）：
- 小微档：预算 15–30c
- 融资档：预算 50–80c
- 上市档：封顶 100c/企业（折合人民币 10 元）
- 累计达 95c：仅允许 ≤5c 工具
- 累计达 100c：停止一切调用，剩余字段标注「本次未采集（成本封顶）」

### 步骤 4 · 按 7 章模板组装报告

按 `references/02_报告模板.md` 的 7 章结构渲染内容：
- §1 公司概况（全档位）
- §2 注册资本（全档位）
- §3 名称变更（全档位）
- §4 股权演变：4.1 注资 / 4.2 设立 / 4.3 大股东更替（全档位）
- §5 经营轨迹：5.1 经营范围 / 5.2 分支与许可 / 5.3 风险记录（全档位）
- §6 地址变迁（全档位）
- §7 总结（全档位）

**条件扩展子节**（档位达标时自动启用；不达标时整节不输出，**不要**留空占位）：
| 子节 | 启用条件 |
|---|---|
| §4.4 实控人认定 | `get_actual_controller` 返回非空 |
| §4.6 申报前 12 月新增股东 | 档位 = 上市档 或 Pre-IPO |
| §5.4 董监高与治理 | 档位 ≥ 融资档 |
| §5.5 关联方网络（公开可查） | 档位 ≥ 融资档 且 `get_personnel_controlled_companies` 返回非空 |
| §5.6 处罚与担保 | `get_administrative_penalty` / `get_guarantee_info` / `get_equity_pledge_info` 任一返回非空 |
| §7 财务摘要 | 档位 = 上市档（A 股 + 发债） 且 `get_financial_key_indicators` 返回非空 |

### 步骤 5 · 生成 DOCX / PDF

调用 `scripts/build_docx.py`：
```bash
python scripts/build_docx.py --input report_data.json --output "企业历史沿革_{企业名}_{YYYYMMDD}.docx"
```

可选的 PDF 转换：
```bash
python scripts/build_docx.py --pdf
```

## 关键原则

1. **有数据就写，没数据就不写**——不要生成 "本次未采集" 类提示填满章节
2. **整体评价三档**：`clean_baseline` / `recovered` / `evasive_high_risk`（见 `references/02_报告模板.md`）
3. **穿透规则**：遇到合伙企业 / 持股平台 / SPV 等关键词，自动追加 `get_shareholder_info` 二级穿透，最多 3 层
4. **行级溯源**：每个写入章节的字段需附 `[来源: qcc-xxx/tool_name · snapshot=YYYY-MM-DD]` 标签（build_docx 自动处理）
5. **不得虚构**：如工具返回空，章节条目留空或不生成，不得补写"推测"、"可能"

## 文件结构

```
qcc-history-skill-v1.0/
├── SKILL.md                        # 本文件：入口与工作流
├── README.md                       # GitHub 落地页
├── CHANGELOG.md                    # 版本记录
├── mcp_config_example.json         # MCP 连接示例
├── references/
│   ├── 01_方案文档.md              # V1.0 方案全貌
│   ├── 02_报告模板.md              # 7 章报告模板
│   ├── 03_MCP字段映射表.md         # 字段→MCP 工具映射
│   ├── 04_档位识别规则.md          # 三档决策树
│   ├── 05_工具调用清单.md          # 按档位工具清单 + 成本
│   ├── 06_V2.0客户自升级指引.md    # 客户自扩展指南
│   └── 07_升级建议稿.md            # Part A–H 分析留档
├── scripts/
│   ├── tier_detector.py            # 档位识别
│   ├── cost_counter.py             # 100c 封顶保护
│   ├── mcp_orchestrator.py         # MCP 批量调用
│   ├── build_docx.py               # DOCX 生成
│   └── requirements.txt
└── assets/
    ├── 示例_企查查科技_报告.docx
    └── 示例_企查查科技_报告.pdf
```

## 快速开始

1. 在 Claude 环境中连接企查查 MCP（参考 `mcp_config_example.json`）
2. 向 Claude 提问：「帮我生成企查查科技股份有限公司的企业历史沿革报告」
3. Claude 自动按工作流执行，约 1–3 分钟产出 DOCX + PDF
4. 成本：小微 ¥1.5–3 / 融资 ¥5–8 / 上市 封顶 ¥10

## 版本策略

- **V1.0（本版本）**：MCP-only，Anthropic / 企查查 官方维护
- **V2.0（客户自升级）**：客户在私域追加尽调底稿 / 承诺函 / 关联交易明细等，参见 `references/06_V2.0客户自升级指引.md`
