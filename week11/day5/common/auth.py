SENSITIVE_KEYS = {"authorization", "cookie", "set-cookie", "x-api-key", "token"}

def mask_headers(headers:dict | None) -> dict:
     """把敏感请求头的值打码，只保留前 12 位和后 4 位。"""
     if not headers:
        return {}
     masked = {}
     for key, value in headers.items():
        if key.lower() in SENSITIVE_KEYS:
            text = str(value)
            masked[key] = f"{text[:12]}...{text[-4:]}" if len(text) > 20 else "***"
        else:
            masked[key] = value
     return masked


def bearer(token: str) -> dict:
    """生成 Bearer 认证头。"""
    return {"Authorization": f"Bearer {token}"}

import re

# 匹配 JSON / urlencoded 里的敏感字段（token、password、secret 等）
_SENSITIVE_FIELD = re.compile(
    r'(?i)("?(?:token|access_token|refresh_token|id_token|authorization|password|secret|api[_-]?key)"?\s*[:=]\s*"?)([^"&,\s}]+)'
)

# 匹配 "Bearer xxx" 形式
_BEARER = re.compile(r'(?i)(bearer\s+)([A-Za-z0-9._\-]+)')


def mask_text(text: str) -> str:
    """把文本里的敏感值打码，用于响应体、请求参数等自由文本。"""
    if not text:
        return text
    text = _SENSITIVE_FIELD.sub(lambda m: f"{m.group(1)}***", text)
    text = _BEARER.sub(lambda m: f"{m.group(1)}***", text)
    return text