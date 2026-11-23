"""TOTP 与模型向后兼容的测试。"""
from suibianji.core.data_manager import DataManager
from suibianji.core.models import AccountPassword, RecordManager
from suibianji.core.totp import generate_code, normalize_secret, remaining_seconds, totp_code


def test_rfc6238_test_vector():
    # RFC 6238 附录 B:种子 "12345678901234567890",T=59 时 8 位结果 94287082
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    assert generate_code(secret, at=59, digits=8) == "94287082"


def test_normalize_secret_accepts_spaces_and_case():
    assert normalize_secret("jbsw y3dp ehpk 3pxp") == normalize_secret("JBSWY3DPEHPK3PXP")


def test_totp_code_and_remaining_range():
    code, remain = totp_code("JBSWY3DPEHPK3PXP", at=120)
    assert len(code) == 6 and code.isdigit()
    assert 1 <= remain <= 30


def test_remaining_seconds_is_never_zero():
    assert remaining_seconds(at=29) == 1
    assert remaining_seconds(at=30) == 30


def test_record_manager_ignores_unknown_keys(tmp_path):
    data = {
        "accounts": [
            {
                "id": "a1",
                "website": "example.com",
                "username": "alice",
                "password": "secret",
                "future_field": "unknown",
            }
        ],
        "ideas": [{"id": "i1", "title": "t", "content": "c", "legacy_field": 1}],
        "wallets": [],
        "prompts": [],
    }
    manager = RecordManager.from_dict(data)
    assert manager.accounts[0].totp_secret == ""
    assert manager.accounts[0].website == "example.com"
    assert manager.ideas[0].content == "c"


def test_account_totp_secret_roundtrip(tmp_path):
    dm = DataManager(str(tmp_path))
    dm.initialize_first_time("pw123456")
    account = dm.add_account("邮箱", "example.com", "alice", "secret-a",
                             totp_secret="JBSWY3DPEHPK3PXP")
    assert account.totp_secret == "JBSWY3DPEHPK3PXP"
    dm.update_account(account.id, totp_secret="")
    assert dm.record_manager.accounts[0].totp_secret == ""
    assert isinstance(account, AccountPassword)
