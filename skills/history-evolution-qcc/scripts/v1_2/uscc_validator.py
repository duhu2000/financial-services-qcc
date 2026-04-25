"""
uscc_validator.py · 统一社会信用代码校验（GB 32100-2015）
=================================================================
作用：在数据契约层拦截"编造的 USCC"。

历史教训：V1.1.3 示例报告里的 USCC `91320506MA1UYUWY3X` 是编造的，
        过不了校验位 → 本模块即可在 schema validate 阶段直接报错。

标准：
- 国家标准 GB 32100-2015《法人和其他组织统一社会信用代码编码规则》
- 共 18 位
- 第 1 位：登记管理部门代码（1=工商, 9=工商, ...）
- 第 2 位：机构类别代码
- 第 3-8 位：登记管理机关行政区划码（GB/T 2260）
- 第 9-17 位：主体标识码（组织机构代码，含其内部校验位）
- 第 18 位：USCC 整体校验位（mod 31）
"""

from __future__ import annotations

# 字符集（注意：不含 I/O/S/V/Z 这五个易混淆字符；共 31 个字符）
USCC_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"

# 加权因子（GB 32100-2015 表 2）
USCC_WEIGHTS = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]


class USCCValidationError(ValueError):
    """统一社会信用代码校验失败"""


def compute_uscc_checksum(uscc_first_17: str) -> str:
    """计算 USCC 第 18 位校验位。

    Args:
        uscc_first_17: 前 17 位字符串

    Returns:
        计算出的第 18 位校验字符
    """
    if len(uscc_first_17) != 17:
        raise USCCValidationError(f"USCC 前缀必须 17 位，收到 {len(uscc_first_17)} 位")

    s = 0
    for i, ch in enumerate(uscc_first_17):
        if ch not in USCC_CHARS:
            raise USCCValidationError(
                f"位置 {i+1} 出现非法字符 '{ch}'（不在 {USCC_CHARS} 中）"
            )
        s += USCC_CHARS.index(ch) * USCC_WEIGHTS[i]

    return USCC_CHARS[(31 - s % 31) % 31]


def validate_uscc(uscc: str) -> tuple[bool, str]:
    """完整校验 USCC。

    Returns:
        (是否合法, 错误说明) — 合法时错误说明为空字符串
    """
    if not uscc:
        return False, "USCC 为空"

    if len(uscc) != 18:
        return False, f"USCC 长度应为 18，收到 {len(uscc)}"

    # 字符集检查
    for i, ch in enumerate(uscc):
        if ch not in USCC_CHARS:
            return False, f"位置 {i+1} 出现非法字符 '{ch}'"

    # 校验位
    expected = compute_uscc_checksum(uscc[:17])
    if expected != uscc[17]:
        return False, (
            f"校验位错误：第 18 位应为 '{expected}' 但实际是 '{uscc[17]}'"
            f"（USCC 可能被编造或抄录错误）"
        )

    return True, ""


def assert_valid_uscc(uscc: str, *, field_name: str = "uscc") -> None:
    """断言 USCC 合法，否则抛 USCCValidationError。"""
    ok, msg = validate_uscc(uscc)
    if not ok:
        raise USCCValidationError(f"{field_name} 校验失败：{msg} · 实际值：{uscc}")


def parse_uscc_admin_division(uscc: str) -> dict:
    """解析 USCC 中的登记管理机关行政区划码（第 3-8 位）。

    返回：{"division_code": "320594", "registration_authority_code": "9", ...}
    """
    ok, _ = validate_uscc(uscc)
    if not ok:
        return {}
    return {
        "registration_dept": uscc[0],          # 登记管理部门
        "entity_category": uscc[1],            # 机构类别
        "division_code": uscc[2:8],            # 行政区划（GB/T 2260，需另外查表）
        "organization_code": uscc[8:17],       # 组织机构代码（含内部校验位）
        "checksum_char": uscc[17],
    }


# ---------------------------------------------------------------------------
# 自检（导入即跑）
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """开发期自检 — 已知正确的 USCC 应通过、已知错误应被拦截。"""
    # 真实有效（企查查科技）
    ok, _ = validate_uscc("91320594088140947F")
    assert ok, "真实 USCC 应通过校验"

    # 编造（V1.1.3 报告里的错误值，应该被拦截）
    ok, msg = validate_uscc("91320506MA1UYUWY3X")
    assert not ok, "编造的 USCC 应被拦截"
    assert "校验位" in msg, f"应明确指出校验位错误：{msg}"

    # 长度错
    ok, _ = validate_uscc("9132")
    assert not ok

    # 含非法字符（I 不在字符集里）
    ok, _ = validate_uscc("9132059408814094II")
    assert not ok


if __name__ == "__main__":
    _self_test()
    print("✓ uscc_validator 自检通过")
    print()
    # Demo
    test_codes = [
        ("91320594088140947F", "企查查科技（真实）"),
        ("91320506MA1UYUWY3X", "V1.1.3 编造的 USCC"),
        ("91110000100000xxxx", "随手编的 18 位"),
    ]
    for code, label in test_codes:
        ok, msg = validate_uscc(code)
        status = "✓ 合法" if ok else f"✗ 非法（{msg}）"
        print(f"  {code}  [{label}] {status}")
