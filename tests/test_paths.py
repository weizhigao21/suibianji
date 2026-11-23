"""paths 模块测试:数据目录不再依赖当前工作目录。"""
import os
from pathlib import Path

import paths


def test_env_override_wins(tmp_path, monkeypatch):
    target = tmp_path / "vault"
    monkeypatch.setenv(paths.ENV_OVERRIDE, str(target))
    resolved = paths.resolve_data_dir()
    assert resolved == target
    assert resolved.is_dir()


def test_portable_dir_with_existing_data_is_reused(tmp_path, monkeypatch):
    monkeypatch.delenv(paths.ENV_OVERRIDE, raising=False)
    root = tmp_path / "app"
    data = root / paths.DATA_DIRNAME
    data.mkdir(parents=True)
    (data / "records.enc").write_bytes(b"encrypted")
    monkeypatch.setattr(paths, "app_dir", lambda: root)

    assert paths.resolve_data_dir() == data


def test_falls_back_to_appdata_when_app_dir_not_writable(tmp_path, monkeypatch):
    monkeypatch.delenv(paths.ENV_OVERRIDE, raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setattr(paths, "app_dir", lambda: tmp_path / "app")
    monkeypatch.setattr(paths, "_is_writable", lambda directory: False)

    resolved = paths.resolve_data_dir()
    assert resolved == tmp_path / "appdata" / paths.APP_NAME / paths.DATA_DIRNAME
    assert resolved.is_dir()


def test_result_is_independent_of_cwd(tmp_path, monkeypatch):
    """从任意工作目录调用,都返回同一路径(旧实现按 CWD 定位会漂移)。"""
    monkeypatch.delenv(paths.ENV_OVERRIDE, raising=False)
    root = tmp_path / "app"
    monkeypatch.setattr(paths, "app_dir", lambda: root)

    cwd = Path.cwd()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    try:
        os.chdir(elsewhere)
        first = paths.resolve_data_dir()
        os.chdir(cwd)
        second = paths.resolve_data_dir()
    finally:
        os.chdir(cwd)

    assert first == second
