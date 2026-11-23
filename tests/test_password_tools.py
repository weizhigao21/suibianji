"""密码生成与强度评估测试。"""
import pytest

from suibianji.core.password_tools import (
    DIGITS,
    LOWER,
    SYMBOLS,
    UPPER,
    generate_password,
    password_strength,
)


def test_generated_password_has_all_enabled_classes():
    password = generate_password(24)
    assert len(password) == 24
    assert any(c in LOWER for c in password)
    assert any(c in UPPER for c in password)
    assert any(c in DIGITS for c in password)
    assert any(c in SYMBOLS for c in password)


def test_generated_password_respects_disabled_classes():
    password = generate_password(16, upper=False, symbols=False)
    assert len(password) == 16
    assert not any(c in UPPER for c in password)
    assert not any(c in SYMBOLS for c in password)


def test_generated_passwords_are_unique():
    assert len({generate_password(20) for _ in range(30)}) == 30


@pytest.mark.parametrize("length", [4, 7, 129])
def test_invalid_length_rejected(length):
    with pytest.raises(ValueError):
        generate_password(length)


def test_all_classes_disabled_rejected():
    with pytest.raises(ValueError):
        generate_password(12, lower=False, upper=False, digits=False, symbols=False)


def test_strength_empty_and_weak():
    assert password_strength("")[1] == "未填写"
    assert password_strength("abcd")[0] <= 1


def test_strength_strong_random_password():
    level, label, percent = password_strength(generate_password(20))
    assert level >= 3
    assert percent >= 80
    assert label in ("较强", "很强")
