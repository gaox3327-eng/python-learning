import logging
import random
import time

import requests

from common.auth import mask_headers, mask_text
from config.config import BASE_URL, TIMEOUT

logger = logging.getLogger(__name__)


class ApiClient:
    """底层 HTTP 客户端：只负责「发请求 + 记日志 + 计时 + 重试」，不碰业务逻辑。"""

    # ── 类属性（必须在类里、缩进 4 格；写模块级会导致 self.XXX 找不到）
    RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})        # 可重试的状态码
    RETRYABLE_EXC = (requests.Timeout, requests.ConnectionError)    # 可重试的异常
    IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS"})

    def __init__(self, base_url: str = BASE_URL, timeout: float = TIMEOUT,
                 headers: dict | None = None, on_unauthorized=None,
                 retries: int = 2, backoff_base: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = dict(headers) if headers else {}
        self.on_unauthorized = on_unauthorized
        self.retries = retries            # 额外重试次数（0 = 不重试）
        self.backoff_base = backoff_base  # 退避基数（秒）

    def _backoff(self, attempt: int) -> float:
        """指数退避 + 抖动：base, 2×base, 4×base… 再在 ±50% 内随机浮动。

        attempt：当前是第几次尝试（从 1 开始）。
        """
        delay = self.backoff_base * (2 ** (attempt - 1))
        return delay * random.uniform(0.5, 1.5)

    def request(self, method: str, url: str, headers: dict | None = None,
                _retried: bool = False, **kwargs):
        """所有方法汇聚到这里。

        headers    ：调用方自带的头（与默认头合并，调用方优先）
        _retried   ：内部标记，只用于控制"401 只重试一次"，绝不传给 requests
        """
        full_url = f"{self.base_url}{url}"

        # 默认头在前、调用方头在后 → 调用方可以覆盖默认值
        merged = {**self.default_headers, **(headers or {})}

        # 用 send_kwargs 副本，不污染 kwargs（401 递归重试时还要用原始的）
        send_kwargs = dict(kwargs)
        if merged:
            send_kwargs["headers"] = merged
        send_kwargs.setdefault("timeout", self.timeout)

        started = time.perf_counter()
        logger.info(
            "→ %s %s  headers=%s params=%s json=%s",
            method, full_url, mask_headers(merged),
            mask_text(str(kwargs.get("params"))), mask_text(str(kwargs.get("json"))),
        )

        # ── 只有幂等方法才允许自动重试（POST 可能重复下单）
        max_attempts = 1 + (self.retries if method.upper() in self.IDEMPOTENT_METHODS else 0)

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.request(method, full_url, **send_kwargs)
            except self.RETRYABLE_EXC as exc:
                cost = (time.perf_counter() - started) * 1000
                logger.warning("网络异常（第 %d/%d 次）%s %s：%s（%.0f ms）",
                               attempt, max_attempts, method, full_url, exc, cost)
                if attempt == max_attempts:
                    logger.error("✗ 重试耗尽 %s %s：%s", method, full_url, exc)
                    raise
                time.sleep(self._backoff(attempt))
                continue

            # 可重试的状态码：还有次数就退避后再来
            if response.status_code in self.RETRYABLE_STATUS and attempt < max_attempts:
                logger.warning("可重试状态码 %s（第 %d/%d 次）%s %s",
                               response.status_code, attempt, max_attempts,
                               method, full_url)
                time.sleep(self._backoff(attempt))
                continue

            break

        # 记录重试了几次 —— 让"重试"这件事可观测
        response.retry_count = attempt - 1

        cost = (time.perf_counter() - started) * 1000
        logger.info("← %s %s  %.0f ms  %s",
                    response.status_code, full_url, cost, mask_text(response.text[:200]))
        response.elapsed_ms = cost

        # === 401 处理：刷新凭据后重试一次 ===
        if response.status_code == 401 and not _retried and self.on_unauthorized:
            logger.warning("401 未授权，刷新凭据后重试一次：%s %s", method, full_url)
            self.on_unauthorized(self)          # 把 client 传进去，回调才能改 default_headers

            # 关键：传原始 headers，不传 merged —— 否则旧 token 会覆盖新 token
            return self.request(method, url, headers=headers,
                                _retried=True, **kwargs)

        return response

    def get(self, url, params=None, headers=None):
        return self.request("GET", url, params=params, headers=headers)

    def post(self, url, data=None, headers=None):
        # 注意：POST 用 json=data（发 JSON 体），不是 data=data（表单）
        return self.request("POST", url, json=data, headers=headers)

    def put(self, url, data=None, headers=None):
        return self.request("PUT", url, json=data, headers=headers)

    def delete(self, url, headers=None):
        return self.request("DELETE", url, headers=headers)
