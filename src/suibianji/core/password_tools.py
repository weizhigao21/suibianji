"""密码生成与强度评估(不依赖 UI,便于单测)。"""

import math
import secrets
import string

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

STRENGTH_LABELS = ["很弱", "较弱", "一般", "较强", "很强"]
STRENGTH_PERCENTS = [15, 35, 60, 80, 100]


def generate_password(length: int = 20, *, lower: bool = True, upper: bool = True,
                      digits: bool = True, symbols: bool = True) -> str:
    """生成随机密码,保证每个启用的字符集至少出现一次。"""
    if not 8 <= length <= 128:
        raise ValueError("密码长度需在 8~128 之间")
    pools = [pool for pool, enabled in (
        (LOWER, lower), (UPPER, upper), (DIGITS, digits), (SYMBOLS, symbols)
    ) if enabled]
    if not pools:
        raise ValueError("至少选择一种字符类型")

    chars = [secrets.choice(pool) for pool in pools]
    alphabet = "".join(pools)
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
    # Fisher-Yates,避免"每类字符固定在开头"
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def password_strength(password: str) -> tuple[int, str, int]:
    """返回 (等级 0~4, 文案, 百分比)。按字符池大小估算熵值。"""
    if not password:
        return 0, "未填写", 0

    pool_size = 0
    if any(c in LOWER for c in password):
        pool_size += 26
    if any(c in UPPER for c in password):
        pool_size += 26
    if any(c in DIGITS for c in password):
        pool_size += 10
    if any(c in SYMBOLS for c in password):
        pool_size += len(SYMBOLS)
    if pool_size == 0:
        pool_size = 26

    entropy = len(password) * math.log2(pool_size)
    if entropy < 28:
        level = 0
    elif entropy < 36:
        level = 1
    elif entropy < 60:
        level = 2
    elif entropy < 80:
        level = 3
    else:
        level = 4
    return level, STRENGTH_LABELS[level], STRENGTH_PERCENTS[level]
