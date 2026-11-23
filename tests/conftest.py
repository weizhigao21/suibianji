"""pytest 共享配置。

data_manager.py 使用绝对导入 (from models import ...),
需把 src 目录加入 sys.path,使测试能 import src 下模块。
"""
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from data_manager import DataManager


@pytest.fixture
def data_manager(tmp_path) -> DataManager:
    """提供使用临时 data 目录的 DataManager,不污染真实数据。"""
    return DataManager(data_dir=str(tmp_path))
