import os
from pathlib import Path

from dotenv import load_dotenv

# 把项目根目录的 .env 读进环境变量。
# load_dotenv 默认「不覆盖」已存在的环境变量，
# 所以优先级是：命令行设置 > .env 文件 > 代码里的默认值
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

ENV = os.getenv("ENV", "test")
TIMEOUT = float(os.getenv("TIMEOUT", "10"))

BASE_URLS = {
    "test": "https://jsonplaceholder.typicode.com",
    "dev": "http://dev.example.com",
    "prod": "http://prod.example.com",
}

# 环境名写错时立刻报错，而不是悄悄用一个错地址
if ENV not in BASE_URLS:
    raise ValueError(f"未知的 ENV={ENV!r}，可选值：{list(BASE_URLS)}")

BASE_URL = BASE_URLS[ENV]