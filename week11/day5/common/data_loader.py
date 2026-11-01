"""YAML 用例数据加载器。

纪律：
    1. 文件不存在 → 立刻报错，不要静默返回空列表（否则 0 个用例还能"全绿"）
    2. 结构不对 → 立刻报错，不要返回半个字典
    3. 编码固定 utf-8（Windows 默认是 GBK，中文会炸）
    4. 字段缺失/拼错 → 加载阶段就报，别等用例跑到那一行才 KeyError

2026-11-01 升级：从"只校验 id/desc"升级为"按 section 校验必填字段 + 拼写保护"。
"""

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── 所有用例都必须有的字段
BASE_REQUIRED = {"id", "desc"}

# ── 每个 section 额外必须有的字段
#    新增 section 时在这里登记；没登记的 section 只走 BASE_REQUIRED（向后兼容）
SECTION_REQUIRED = {
    "error_matrix":  {"expected_status"},
    "invalid_limit": {"params", "expected_status"},
    "invalid_order": {"params", "expected_status"},
    "not_found_id":  {"product_id", "expected_status"},
}

# ── 每个 section 允许出现的字段（拼写保护：不在白名单里的键说明大概率拼错了）
SECTION_ALLOWED = {
    "error_matrix":  {"id", "desc", "params", "path", "method",
                      "expected_status", "known_defect"},
    "invalid_limit": {"id", "desc", "params", "expected_status", "known_defect"},
    "invalid_order": {"id", "desc", "params", "expected_status", "known_defect"},
    "not_found_id":  {"id", "desc", "product_id", "expected_status", "known_defect"},
}

# ── 「至少要有其中一个」的字段组：防止写出"什么都没测"的空壳用例
#    结构是 tuple[set[str], ...]：每个 set 是一组"任选其一"的字段
SECTION_ONE_OF = {
    "error_matrix": ({"params", "path"},),    # query 参数 或 路径，二者之一
}


def _check_case(case, filename: str, section: str, index: int) -> None:
    """单条用例的结构校验。出错时抛 ValueError，信息里带定位。"""
    where = f"{filename}:{section}[{index}]"

    if not isinstance(case, dict):
        raise ValueError(f"{where} 必须是一条映射（dict），实际是 {type(case).__name__}")

    # ① 必填字段
    required = BASE_REQUIRED | SECTION_REQUIRED.get(section, set())
    missing = required - set(case)
    if missing:
        raise ValueError(f"{where} 缺少字段 {sorted(missing)}，现有 {sorted(case)}")

    # ② 拼写保护：只对已登记的 section 生效
    allowed = SECTION_ALLOWED.get(section)
    if allowed is not None:
        unknown = set(case) - allowed
        if unknown:
            raise ValueError(
                f"{where} 出现未登记字段 {sorted(unknown)}，"
                f"{section} 允许的是 {sorted(allowed)}（多半是拼错了）"
            )

    # ③ "至少有一个"的字段组合
    for group in SECTION_ONE_OF.get(section, ()):
        if not (group & set(case)):
            raise ValueError(f"{where} 至少需要 {sorted(group)} 中的一个")

    # ④ 类型校验
    if not isinstance(case["id"], str) or not case["id"].strip():
        raise ValueError(f"{where} 的 id 必须是非空字符串，实际是 {case['id']!r}")
    if not isinstance(case["desc"], str) or not case["desc"].strip():
        raise ValueError(f"{where} 的 desc 必须是非空字符串，实际是 {case['desc']!r}")

    if "expected_status" in case and not isinstance(case["expected_status"], int):
        raise ValueError(
            f"{where} 的 expected_status 必须是整数（不要加引号），"
            f"实际是 {case['expected_status']!r}"
        )
    if "params" in case and not isinstance(case["params"], dict):
        raise ValueError(f"{where} 的 params 必须是映射，实际是 {type(case['params']).__name__}")
    if "path" in case and not (isinstance(case["path"], str) and case["path"].startswith("/")):
        raise ValueError(f"{where} 的 path 必须以 / 开头，实际是 {case.get('path')!r}")
    if "method" in case and str(case["method"]).upper() not in {
        "GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"
    }:
        raise ValueError(f"{where} 的 method 不是合法的 HTTP 方法：{case['method']!r}")
    if "known_defect" in case and not isinstance(case["known_defect"], bool):
        raise ValueError(f"{where} 的 known_defect 必须是 true/false，实际是 {case['known_defect']!r}")


def load_cases(filename: str, section: str) -> list[dict]:
    """读取某个 yaml 里的一个 section，返回用例列表（校验不过直接抛错）。"""
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"用例数据文件不存在：{path}")

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{filename} 顶层必须是映射（section 名 → 用例列表）")

    if section not in data:
        raise KeyError(f"{filename} 里没有 section：{section}（现有：{list(data)}）")

    cases = data[section]
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{filename} 的 {section} 必须是非空列表")

    # 逐条校验，并顺手检查 id 是否重复
    seen: dict[str, int] = {}
    for i, case in enumerate(cases):
        _check_case(case, filename, section, i)

        cid = case["id"]
        if cid in seen:
            raise ValueError(
                f"{filename}:{section} 的 id 重复：{cid!r}"
                f"（第 {seen[cid]} 条和第 {i} 条），ids 会撞车"
            )
        seen[cid] = i

    return cases
