# qcc-history-skill · 企业历史沿革 SKILL V1.1.3

> 纯企查查 MCP 驱动的 KYB 报告生成器。立体发展叙事，146 工具覆盖，档位预算 ¥4.5 / ¥13 / ¥18。
> **V1.1.3 修复**：移除中英混排 body 文字的 `italic=True`（LibreOffice 渲染时产生字形断裂黑条），同步修正 footer 版本字符串。样式仍对齐 kyb-opus 官方 KYB 范式。

## 核心特性

- **7 章自动化**：公司概况 / 注册资本 / 名称变更 / 股权演变 / 经营轨迹 / 地址变迁 / 总结
- **三档自适应**：上市 / 融资 / 小微档自动识别，不同档位启用不同工具组合与章节
- **成本可控**：封顶 100c/企业（约 ¥10），累计达 95c 触发保护模式
- **零客户负担**：MCP 能拿到什么写什么，拿不到的章节**整节不生成**（不留空占位、不向客户要材料）
- **穿透核查**：合伙企业/SPV 自动二级穿透，最多 3 层

## 适用场景

- 信贷尽调（银行、信托、小贷）
- 投前 KYB（PE/VC、产业资本）
- 供应链风控（应收应付方核查）
- IPO 辅导前快照（上市档自动启用完整 7 章 + 条件扩展 6 子节）

## 依赖

- Claude Code / Claude Desktop（支持 SKILL 机制）
- 企查查 MCP（[云聚接口](https://cloud.qcc.com/)），需连接以下服务：
  - `qcc-company`（工商基础）
  - `qcc-risk`（风险信息）
  - `qcc-ipr`（知识产权）
  - `qcc-operation`（经营信息 + 财务）
  - `qcc-history`（历史信息，规划中）
  - `qcc-executive`（董监高，规划中）
- Python 3.9+（仅执行脚本需要）
- `python-docx`、`pandoc`（可选，仅 PDF 转换需要）

## 快速开始

### 1. 安装

```bash
git clone https://github.com/<your-org>/qcc-history-skill.git
cd qcc-history-skill/qcc-history-skill-v1.0

# 配置 MCP（参考 mcp_config_example.json，替换 ${QCC_API_KEY}）
cp mcp_config_example.json ~/.config/claude/mcp.json

# 安装 Python 依赖（仅在本地生成 DOCX 时需要）
pip install -r scripts/requirements.txt
```

### 2. 放入 Claude 的 Skills 目录

```bash
# Claude Desktop（macOS）
mkdir -p ~/.claude/skills/
cp -r qcc-history-skill-v1.0 ~/.claude/skills/qcc-history
```

### 3. 使用

在 Claude 会话中：

```
帮我生成"企查查科技股份有限公司"的企业历史沿革报告
```

Claude 自动识别 SKILL，按工作流执行：档位识别（15c）→ 批量调用 MCP（15–100c）→ 7 章模板组装 → 生成 DOCX + PDF。

## 档位与成本

| 档位 | 识别特征 | MCP 调用量 | 成本 | 报告深度 |
|---|---|---|---|---|
| 小微档 | 无上市 / 无融资 / ≤1000 万 | 15–30c | ¥1.5–3 | 7 章基础版 |
| 融资档 | 有融资记录（天使—Pre-IPO） | 50–80c | ¥5–8 | 7 章 + §4.4/§5.4/§5.5 |
| 上市档 | 已上市或发债 | 封顶 100c | ¥10 | 7 章 + §4.4/§4.6/§5.4/§5.5/§5.6/§7 财务 |

## 文件结构

```
qcc-history-skill-v1.0/
├── SKILL.md                        # 入口 + 工作流
├── README.md                       # 本文件
├── CHANGELOG.md                    # 版本记录
├── mcp_config_example.json         # MCP 连接样例
├── references/                     # 供 Claude 加载的参考文档
│   ├── 01_方案文档.md
│   ├── 02_报告模板.md
│   ├── 03_MCP字段映射表.md
│   ├── 04_档位识别规则.md
│   ├── 05_工具调用清单.md
│   ├── 06_V2.0客户自升级指引.md
│   └── 07_升级建议稿.md
├── scripts/                        # 执行脚本
│   ├── tier_detector.py
│   ├── cost_counter.py
│   ├── mcp_orchestrator.py
│   ├── build_docx.py
│   └── requirements.txt
└── assets/                         # 示例报告
    ├── 示例_企查查科技_报告.docx
    └── 示例_企查查科技_报告.pdf
```

## V1.0 / V2.0 分层

**V1.0（本版本）**：纯 MCP 驱动，由 Anthropic + 企查查 官方维护。
**V2.0（客户自升级）**：客户用自有尽调底稿（代持还原 / 承诺函 / 关联交易明细 / 独立性评估等）扩展，参见 `references/06_V2.0客户自升级指引.md`。V2.0 由客户自行维护，本 SKILL 作者不承诺兼容性。

## 不覆盖的内容（归 V2.0）

以下 11 类内容 **V1.0 不输出**（MCP 拿不到），归客户 V2.0 自扩展：

1. 代持存在性声明与还原
2. 一致行动关系声明
3. 独立性五维定性评估
4. 股权激励细则（行权价 / 条件 / 回购）
5. 关联交易明细（对手方 / 金额 / 定价）
6. 对赌 / 回购 / 业绩承诺 / 优先清算
7. 同业竞争承诺 / 避免关联交易承诺
8. 股利分配政策 / 滚存利润安排
9. 上市锁定 / 减持 / 稳定股价 / 欺诈发行回购 / 填补即期回报承诺体系
10. 特别表决权 / AB 股 / VIE 架构
11. 亲属关系定性网络图

## 限制说明

- 财务摘要（§7）仅 A 股上市或发债企业可用（企查查 API 限制）
- 私募基金备案（中基协 AMAC 数据）当前 MCP 无工具覆盖
- 部分规划工具（`qcc-history` 34 个 / `qcc-executive` 35 个 / `get_financial_key_indicators` 1 个）尚未全量上线，V1.0 会在工具可用时自动启用

## 许可证

MIT License. 见 [LICENSE](LICENSE)（如存在）。

## 贡献与反馈

Issue / PR 请提交到 GitHub 仓库。

---

**版本**：V1.0.0
**发布日期**：2026-04-20
**基线工具集**：企查查 MCP 138 工具
