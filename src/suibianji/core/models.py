from dataclasses import asdict, dataclass, fields
from datetime import datetime


@dataclass
class AccountPassword:
    id: str
    website: str
    username: str
    password: str
    account_type: str = ""
    url: str | None = None
    notes: str | None = None
    totp_secret: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class Idea:
    id: str
    title: str
    content: str
    tags: list[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class WalletAddress:
    id: str
    name: str
    address: str
    wallet_type: str
    notes: str | None = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class AIPrompt:
    id: str
    title: str
    content: str
    category: str = ""
    tags: list[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at


class RecordManager:
    def __init__(self):
        self.accounts: list[AccountPassword] = []
        self.ideas: list[Idea] = []
        self.wallets: list[WalletAddress] = []
        self.prompts: list[AIPrompt] = []
    
    def to_dict(self):
        return {
            'accounts': [asdict(acc) for acc in self.accounts],
            'ideas': [asdict(idea) for idea in self.ideas],
            'wallets': [asdict(wallet) for wallet in self.wallets],
            'prompts': [asdict(prompt) for prompt in self.prompts]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        manager = cls()
        # 只接收模型已知字段:旧数据缺字段走默认值,未来新增字段不会让旧版本崩溃
        def build(model, raw):
            known = {f.name for f in fields(model)}
            return model(**{k: v for k, v in raw.items() if k in known})

        manager.accounts = [build(AccountPassword, acc) for acc in data.get('accounts', [])]
        manager.ideas = [build(Idea, idea) for idea in data.get('ideas', [])]
        manager.wallets = [build(WalletAddress, wallet) for wallet in data.get('wallets', [])]
        manager.prompts = [build(AIPrompt, prompt) for prompt in data.get('prompts', [])]
        return manager
