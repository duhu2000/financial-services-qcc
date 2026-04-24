"""
cost_counter.py · MCP 调用成本计数器
====================================
企查查 MCP 封顶 100c/企业（¥10）。本模块维护累计成本并强制封顶。

规则：
  - 累计 < 95c：可调用任意工具
  - 累计 ≥ 95c：仅允许 ≤5c 的工具
  - 累计 ≥ 100c：停止一切调用（抛 BudgetExceeded）
  - 封顶后剩余字段在报告中标注「本次未采集（成本封顶）」
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class BudgetExceeded(Exception):
    """当累计成本达到或超过预算时抛出。"""


@dataclass
class CostRecord:
    tool: str
    cost: int  # cent
    running_total: int


@dataclass
class CostCounter:
    budget: int = 180  # V1.1 默认封顶 180c（上市档）；实际按档位传入
    soft_limit: int = 170  # V1.1 保护阈值（budget - 10）
    total: int = 0
    history: list[CostRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        # 确保 soft_limit 永远 = budget - 10
        if self.soft_limit >= self.budget:
            self.soft_limit = max(0, self.budget - 10)

    def add(self, tool: str, cost: int) -> None:
        """登记一次调用。调用前应先 `can_call`。"""
        if cost < 0:
            raise ValueError("成本不能为负")

        if self.total + cost > self.budget:
            raise BudgetExceeded(
                f"预算超出：累计 {self.total}c + 本次 {cost}c > 预算 {self.budget}c"
            )

        if self.total >= self.soft_limit and cost > 5:
            raise BudgetExceeded(
                f"保护模式：累计 {self.total}c ≥ {self.soft_limit}c，仅允许 ≤5c 工具"
            )

        self.total += cost
        self.history.append(
            CostRecord(tool=tool, cost=cost, running_total=self.total)
        )

    def can_call(self, cost: int) -> bool:
        """预检：能否调用指定成本的工具。"""
        if self.total + cost > self.budget:
            return False
        if self.total >= self.soft_limit and cost > 5:
            return False
        return True

    def remaining(self) -> int:
        return max(0, self.budget - self.total)

    def is_capped(self) -> bool:
        return self.total >= self.budget

    def is_in_protection_mode(self) -> bool:
        return self.total >= self.soft_limit and self.total < self.budget

    def summary(self) -> dict:
        return {
            "total_cent": self.total,
            "total_rmb": round(self.total / 10, 2),
            "budget_cent": self.budget,
            "remaining_cent": self.remaining(),
            "capped": self.is_capped(),
            "protection_mode": self.is_in_protection_mode(),
            "call_count": len(self.history),
            "history": [
                {"tool": r.tool, "cost": r.cost, "running_total": r.running_total}
                for r in self.history
            ],
        }

    def __repr__(self) -> str:
        return (
            f"CostCounter(total={self.total}c/{self.budget}c, "
            f"calls={len(self.history)}, "
            f"{'CAPPED' if self.is_capped() else 'PROTECT' if self.is_in_protection_mode() else 'OK'})"
        )


if __name__ == "__main__":
    # 本地 smoke test
    cc = CostCounter(budget=100)

    cc.add("mcp__qcc-company__get_company_profile", 5)
    cc.add("mcp__qcc-company__get_listing_info", 5)
    cc.add("mcp__qcc-operation__get_financing_records", 5)
    print(cc)  # total=15c/100c

    # 模拟融资档多次调用
    for i in range(15):
        try:
            cc.add(f"mcp__tool_{i}", 5)
        except BudgetExceeded as exc:
            print(f"第 {i} 次调用被拒：{exc}")
            break

    print(cc)
    # 一次 20c 工具：historical_shareholders
    try:
        cc.add("mcp__qcc-history__get_historical_shareholders", 20)
        print("20c 工具调用成功")
    except BudgetExceeded as exc:
        print(f"20c 工具被拒：{exc}")

    import json
    print(json.dumps(cc.summary(), indent=2, ensure_ascii=False))
