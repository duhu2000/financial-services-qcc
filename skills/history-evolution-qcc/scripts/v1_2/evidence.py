"""
evidence.py · MCP 工具调用证据锚点
=================================================================
作用：每个数据字段必须能回溯到唯一的 MCP 工具调用 + JSON 路径 + 时间戳。

历史教训：V1.1.3 报告里的"2010 年最早专利"、"2022-06-10 央行处罚"、
        "递交主板申报稿" 等编造内容，本质上是 LLM 在没有 MCP 数据时
        自行补全。本模块强制每个字段必须有 evidence 锚点 → 渲染时
        按 evidence 校验，缺锚点直接拒绝输出。

设计：
- Evidence 是一个不可变值对象（@dataclass(frozen=True)）
- 包含 tool_name / search_key / json_path / snapshot_ts / raw_value
- 在 MCP 调用层包装返回结果，建立"返回值 → evidence" 映射
- 渲染层的每个字段写入时，必须传 evidence 引用
- 最终产出 manifest.json，含字段级溯源链
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Evidence:
    """一条 MCP 字段证据。"""
    tool_name: str             # 例如 "qcc-company.get_shareholder_info"
    search_key: str            # 调用 MCP 时使用的 searchKey
    json_path: str             # JSONPath 风格，例如 "$.股东信息[0].持股比例"
    snapshot_ts: str           # ISO 8601 时间戳（含时区）
    raw_value: Any             # 原始字段值（不经任何加工）

    def __post_init__(self):
        # 时间戳格式校验
        try:
            datetime.fromisoformat(self.snapshot_ts.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"snapshot_ts 必须是 ISO 8601：{self.snapshot_ts}") from e

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def evidence_id(self) -> str:
        """生成稳定的 evidence ID（用于 manifest 和报告内交叉引用）。"""
        canonical = f"{self.tool_name}|{self.search_key}|{self.json_path}|{self.snapshot_ts}"
        return "ev_" + hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:12]


@dataclass
class EvidenceBox:
    """字段值 + 证据的封装容器（不可绕过 evidence 写值）。"""
    value: Any
    evidence: Evidence

    def __post_init__(self):
        if self.evidence is None:
            raise ValueError("EvidenceBox 必须传 evidence — 无锚点字段不得入报告")


class MCPCallRecorder:
    """记录一次 MCP 调用，并为返回 JSON 中的每个字段生成 Evidence。

    使用方式：
        recorder = MCPCallRecorder("qcc-company.get_shareholder_info",
                                    search_key="91320594088140947F")
        result = mcp_call(...)
        recorder.record_response(result)
        # 之后从 recorder 取证据对象：
        ev = recorder.evidence_for("$.股东信息[0].股东名称")
    """

    def __init__(self, tool_name: str, search_key: str):
        self.tool_name = tool_name
        self.search_key = search_key
        self.snapshot_ts = datetime.now(timezone.utc).isoformat()
        self._response: dict | None = None
        self._evidence_cache: dict[str, Evidence] = {}

    def record_response(self, response: dict) -> None:
        self._response = response

    def evidence_for(self, json_path: str) -> Evidence:
        """为某个 JSONPath 路径生成 Evidence 对象。"""
        if self._response is None:
            raise RuntimeError("先调用 record_response()")

        if json_path in self._evidence_cache:
            return self._evidence_cache[json_path]

        raw = _resolve_json_path(self._response, json_path)
        ev = Evidence(
            tool_name=self.tool_name,
            search_key=self.search_key,
            json_path=json_path,
            snapshot_ts=self.snapshot_ts,
            raw_value=raw,
        )
        self._evidence_cache[json_path] = ev
        return ev

    def box(self, json_path: str) -> EvidenceBox:
        """便捷方法：直接生成 (value, evidence) 封装。"""
        ev = self.evidence_for(json_path)
        return EvidenceBox(value=ev.raw_value, evidence=ev)


def _resolve_json_path(obj: Any, path: str) -> Any:
    """轻量 JSONPath 实现：支持 $.key.subkey[0].field"""
    if not path.startswith("$"):
        raise ValueError(f"JSONPath 必须以 $ 开头：{path}")

    cur = obj
    # 移除起始 $
    rest = path[1:]
    if rest.startswith("."):
        rest = rest[1:]

    # 解析 token 序列：a.b[0].c
    i = 0
    while i < len(rest):
        # key
        j = i
        while j < len(rest) and rest[j] not in ".[":
            j += 1
        key = rest[i:j]
        if key:
            if not isinstance(cur, dict):
                raise KeyError(f"路径 {path} 在 {key} 处期待 dict，实际 {type(cur).__name__}")
            if key not in cur:
                raise KeyError(f"路径 {path} 在 {key} 处不存在")
            cur = cur[key]
        i = j
        # 数组下标
        while i < len(rest) and rest[i] == "[":
            close = rest.index("]", i)
            idx = int(rest[i+1:close])
            if not isinstance(cur, list):
                raise KeyError(f"路径 {path} 期待 list 但实际 {type(cur).__name__}")
            cur = cur[idx]
            i = close + 1
        if i < len(rest) and rest[i] == ".":
            i += 1
    return cur


# ---------------------------------------------------------------------------
# Manifest 生成
# ---------------------------------------------------------------------------

class ManifestBuilder:
    """收集报告每个字段的证据链，最终输出 manifest.json。"""

    def __init__(self, *, report_id: str, company_name: str, uscc: str):
        self.report_id = report_id
        self.company_name = company_name
        self.uscc = uscc
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.fields: dict[str, dict] = {}        # field_path -> evidence summary
        self.evidence_pool: dict[str, dict] = {} # evidence_id -> full evidence

    def attach(self, field_path: str, ev: Evidence) -> None:
        """记录一个字段的来源 evidence。

        field_path 例如 "report.section_5_1.shareholders[0].holding_ratio"
        """
        self.fields[field_path] = {"evidence_id": ev.evidence_id}
        self.evidence_pool[ev.evidence_id] = ev.to_dict()

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "company_name": self.company_name,
            "uscc": self.uscc,
            "created_at": self.created_at,
            "field_count": len(self.fields),
            "evidence_count": len(self.evidence_pool),
            "fields": self.fields,
            "evidence_pool": self.evidence_pool,
        }

    def write(self, out_path: str) -> None:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

def _self_test() -> None:
    sample_response = {
        "企业名称": "企查查科技股份有限公司",
        "股东信息": [
            {"股东名称": "陈德强", "持股比例": "35.49%"},
            {"股东名称": "杨京", "持股比例": "12.07%"},
        ],
    }

    recorder = MCPCallRecorder(
        tool_name="qcc-company.get_shareholder_info",
        search_key="91320594088140947F",
    )
    recorder.record_response(sample_response)

    ev1 = recorder.evidence_for("$.股东信息[0].股东名称")
    assert ev1.raw_value == "陈德强"
    assert ev1.evidence_id.startswith("ev_")

    ev2 = recorder.evidence_for("$.企业名称")
    assert ev2.raw_value == "企查查科技股份有限公司"

    # 缺路径应抛 KeyError
    try:
        recorder.evidence_for("$.不存在的字段")
        assert False, "应抛 KeyError"
    except KeyError:
        pass

    # EvidenceBox 强制有 evidence
    box = EvidenceBox(value="test", evidence=ev1)
    assert box.value == "test"

    try:
        EvidenceBox(value="test", evidence=None)  # type: ignore[arg-type]
        assert False, "应拒绝无 evidence"
    except ValueError:
        pass

    # Manifest
    mf = ManifestBuilder(report_id="TEST-001", company_name="企查查", uscc="91320594088140947F")
    mf.attach("report.shareholder[0].name", ev1)
    mf.attach("report.shareholder[0].name_again", ev1)  # 同源应去重
    mf.attach("report.company_name", ev2)
    d = mf.to_dict()
    assert d["field_count"] == 3
    assert d["evidence_count"] == 2  # ev1 和 ev2，去重


if __name__ == "__main__":
    _self_test()
    print("✓ evidence 自检通过")
