# 接口自动化测试项目

[![ci](https://github.com/gaox3327-eng/python-learning/actions/workflows/ci.yml/badge.svg)](https://github.com/gaox3327-eng/python-learning/actions/workflows/ci.yml)

基于 pytest + requests 的接口自动化测试框架，覆盖鉴权、契约校验、重试、幂等、错误码矩阵与缺陷复现。

## 快速开始

```bash
cd week11/day5
pip install -r requirements.txt
cp .env.example .env

pytest -m smoke        # 冒烟集：8 条，约 3 秒（提交前跑）
pytest -m "smoke or local"   # CI 跑这个（排除公网用例）
pytest                 # 全量：55 条，含公网用例
```

## 目录结构

```
week11/day5/
├─ config/            配置（.env 三级优先级）
├─ common/            api_client（重试/401续期/脱敏）、auth、validators、data_loader
├─ api/               业务层（post_api、products_api）
├─ data/              YAML 用例数据（error_matrix、products_cases）
├─ schemas/           JSON Schema
├─ testcases/         用例（55 条）
├─ server.py          本地 mock 商城后端（第 8 课靶子，含 6 个已知缺陷）
├─ 测试说明.md         测试设计与缺陷记录
└─ pytest.ini         markers / strict-markers / timeout
```

## markers

| marker | 含义 | 用途 |
|---|---|---|
| `smoke` | 核心快速用例，< 5 秒 | 提交前跑 |
| `local` | 依赖本地 mock 服务 | CI 跑 |
| `network` | 依赖公网服务，可能 flaky | 本地按需跑 |

## 已知缺陷（用 strict xfail 登记）

`pytest -m smoke -rx` 可看到 6 条 xfail 的原因；缺陷修复后会自动 XPASS 报警。
