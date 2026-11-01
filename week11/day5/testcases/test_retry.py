"""第 7 课 Day 1：重试行为验证（不依赖网络，用 monkeypatch 造假响应）"""

import common.api_client as mod


class FakeResponse:
    def __init__(self, code):
        self.status_code = code
        self.text = ""
        self.elapsed_ms = 0


def test_get_retries_on_500_then_success(monkeypatch):
    calls = []

    def fake_request(method, url, **kw):
        calls.append(url)
        return FakeResponse(500 if len(calls) < 3 else 200)

    monkeypatch.setattr(mod.requests, "request", fake_request)

    client = mod.ApiClient(base_url="http://fake", retries=2, backoff_base=0.01)
    resp = client.get("/x")

    assert resp.status_code == 200
    assert len(calls) == 3
    assert resp.retry_count == 2


def test_post_is_not_retried(monkeypatch):
    calls = []

    def fake_request(method, url, **kw):
        calls.append(url)
        return FakeResponse(500)

    monkeypatch.setattr(mod.requests, "request", fake_request)

    client = mod.ApiClient(base_url="http://fake", retries=2, backoff_base=0.01)
    resp = client.post("/x", data={"a": 1})

    assert resp.status_code == 500
    assert len(calls) == 1
    assert resp.retry_count == 0