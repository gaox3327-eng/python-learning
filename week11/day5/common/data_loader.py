"""YAML 用例数据加载器。

三条纪律：
    1. 文件不存在 → 立刻报错，不要静默返回空列表（否则 0 个用例还能"全绿"）
    2. 结构不对 → 立刻报错，不要返回半个字典
    3. 编码固定 utf-8（Windows 默认是 GBK，中文会炸）
"""

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_cases(filename: str, section: str) -> list[dict]:
    """读取某个 yaml 里的一个 section，返回用例列表。"""
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

    # 逐条校验必备字段，缺了立刻报错——不要等到用例跑起来才发现
    for i, case in enumerate(cases):
        missing = {"id", "desc"} - set(case)
        if missing:
            raise ValueError(f"{filename}:{section}[{i}] 缺少字段 {missing}")

    return cases