import logging
import time

import requests

from config.config import BASE_URL

logger = logging.getLogger(__name__)


class ApiClient:
    """底层 HTTP 客户端：只负责「发请求 + 记日志 + 计时」，不碰业务逻辑。"""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, url: str, **kwargs):
        """所有方法都汇聚到这里：加固逻辑只写一遍，以后加新方法只要一行。"""
        full_url = f"{self.base_url}{url}"
        kwargs.setdefault("timeout", self.timeout)

        started = time.perf_counter()
        logger.info(
            "→ %s %s  params=%s json=%s",
            method, full_url, kwargs.get("params"), kwargs.get("json"),
        )

        try:
            response = requests.request(method, full_url, **kwargs)
        except requests.Timeout:
            cost = (time.perf_counter() - started) * 1000
            logger.error("✗ 超时 %s %s（%.0f ms）", method, full_url, cost)
            raise
        except requests.RequestException as exc:
            cost = (time.perf_counter() - started) * 1000
            logger.error("✗ 请求失败 %s %s：%s（%.0f ms）", method, full_url, exc, cost)
            raise

        cost = (time.perf_counter() - started) * 1000
        logger.info(
            "← %s %s  %.0f ms  %s",
            response.status_code, full_url, cost, response.text[:200],
        )

        # 挂到 response 上，用例里可以直接断言响应时间：
        #   assert response.elapsed_ms < 2000
        response.elapsed_ms = cost
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
