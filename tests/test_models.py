"""models 模块测试:数据模型默认值、时间戳、序列化往返。"""
from models import AccountPassword, Idea, WalletAddress, AIPrompt, RecordManager


def test_account_password_defaults():
    acc = AccountPassword(id="1", website="w", username="u", password="p")
    assert acc.created_at
    assert acc.updated_at == acc.created_at
    assert acc.account_type == ""
    assert acc.url is None
    assert acc.notes is None


def test_idea_default_tags_is_empty_list():
    """确保 tags 默认值不是共享可变对象。"""
    idea1 = Idea(id="1", title="t", content="c")
    idea2 = Idea(id="2", title="t", content="c")
    assert idea1.tags == []
    idea1.tags.append("x")
    assert idea2.tags == []


def test_wallet_and_prompt_defaults():
    w = WalletAddress(id="1", name="n", address="0x", wallet_type="ETH")
    assert w.notes is None
    assert w.created_at

    p = AIPrompt(id="1", title="t", content="c")
    assert p.category == ""
    assert p.tags == []


def test_record_manager_roundtrip():
    rm = RecordManager()
    rm.accounts.append(AccountPassword(
        id="a1", website="w", username="u", password="secret",
        account_type="邮箱", url="http://x", notes="n"))
    rm.ideas.append(Idea(id="i1", title="t", content="c", tags=["x", "y"]))
    rm.wallets.append(WalletAddress(id="w1", name="n", address="0xabc", wallet_type="ETH"))
    rm.prompts.append(AIPrompt(id="p1", title="t", content="c", category="写作"))

    restored = RecordManager.from_dict(rm.to_dict())

    assert len(restored.accounts) == 1
    acc = restored.accounts[0]
    assert acc.password == "secret"
    assert acc.account_type == "邮箱"
    assert acc.url == "http://x"
    assert acc.notes == "n"

    assert restored.ideas[0].tags == ["x", "y"]
    assert restored.wallets[0].address == "0xabc"
    assert restored.prompts[0].category == "写作"


def test_record_manager_from_dict_empty():
    rm = RecordManager.from_dict({})
    assert rm.accounts == []
    assert rm.ideas == []
    assert rm.wallets == []
    assert rm.prompts == []
