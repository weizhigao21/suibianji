"""pytest 共享配置:包已安装/由 pyproject 的 pythonpath 提供,不再手工改 sys.path。"""
import pytest

from suibianji.core.data_manager import DataManager


@pytest.fixture
def data_manager(tmp_path) -> DataManager:
    """提供使用临时 data 目录的 DataManager,不污染真实数据。"""
    return DataManager(data_dir=str(tmp_path))
