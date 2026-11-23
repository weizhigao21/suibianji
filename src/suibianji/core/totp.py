"""TOTP(RFC 6238)一次性验证码,仅用标准库实现。"""

import base64
import hashlib
import hmac
import struct
import time

PERIOD = 30
DIGITS = 6


def normalize_secret(secret: str) -> str:
    """去掉空格/短横线,补齐 Base32 填充。"""
    cleaned = "".join(str(secret or "").split()).replace("-", "").upper().rstrip("=")
    if not cleaned:
        raise ValueError("TOTP 密钥为空")
    pad = (-len(cleaned)) % 8
    return cleaned + "=" * pad


def generate_code(secret: str, at: float | None = None, period: int = PERIOD, digits: int = DIGITS) -> str:
    """生成指定时刻的验证码,默认当前时间。"""
    key = base64.b32decode(normalize_secret(secret))
    timestamp = int(time.time() if at is None else at)
    counter = timestamp // period
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10 ** digits)).zfill(digits)


def remaining_seconds(at: float | None = None, period: int = PERIOD) -> int:
    """当前验证码还剩多少秒失效(1..period)。"""
    timestamp = int(time.time() if at is None else at)
    return period - (timestamp % period)


def totp_code(secret: str, at: float | None = None) -> tuple[str, int]:
    """返回 (验证码, 剩余秒数)。"""
    return generate_code(secret, at), remaining_seconds(at)
