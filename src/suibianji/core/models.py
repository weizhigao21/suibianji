from dataclasses import asdict, dataclass
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
        manager.accounts = [AccountPassword(**acc) for acc in data.get('accounts', [])]
        manager.ideas = [Idea(**idea) for idea in data.get('ideas', [])]
        manager.wallets = [WalletAddress(**wallet) for wallet in data.get('wallets', [])]
        manager.prompts = [AIPrompt(**prompt) for prompt in data.get('prompts', [])]
        return manager
