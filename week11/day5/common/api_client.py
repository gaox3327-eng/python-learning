import logging
import time

import requests
from common.auth import mask_headers, mask_text
from config.config import BASE_URL
from common.auth import mask_headers
logger = logging.getLogger(__name__)


class ApiClient:
    """底层 HTTP 客户端：只负责「发请求 + 记日志 + 计时」，不碰业务逻辑。"""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 10,headers: dict | None = None,on_unauthorized=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = dict(headers) if headers else {}
        self.on_unauthorized = on_unauthorized 
    def request(self, method: str, url: str, headers: dict | None = None,
                _retried: bool = False, **kwargs):
        """所有方法汇聚到这里。

        headers    ：调用方自带的头（与默认头合并，调用方优先）
        _retried   ：内部标记，只用于控制"401 只重试一次"，绝不传给 requests
        """
        full_url = f"{self.base_url}{url}"

        # 默认头在前、调用方头在后 → 调用方可以覆盖默认值
        merged = {**self.default_headers, **(headers or {})}

        # 注意：用 send_kwargs 副本，不污染 kwargs（重试时还要用原始的）
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

        try:
            response = requests.request(method, full_url, **send_kwargs)
        except requests.Timeout:
            cost = (time.perf_counter() - started) * 1000
            logger.error("✗ 超时 %s %s（%.0f ms）", method, full_url, cost)
            raise
        except requests.RequestException as exc:
            cost = (time.perf_counter() - started) * 1000
            logger.error("✗ 请求失败 %s %s：%s（%.0f ms）", method, full_url, exc, cost)
            raise

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
