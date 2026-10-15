from pathlib import Path
from types import SimpleNamespace

import pytest

from cs_demo_analyzer.config import Settings
from cs_demo_analyzer.domain.contracts import AppError


def test_data_root_precedence_and_independent_install(tmp_path, monkeypatch):
    config = tmp_path / "config.toml"
    config.write_text(f'data_root = "{tmp_path / "configured"}"\n')
    monkeypatch.setenv("CSDA_DATA_ROOT", str(tmp_path / "environment"))
    assert Settings.load(config_path=str(config)).data_root == tmp_path / "environment"
    assert Settings.load(str(tmp_path / "explicit"), str(config)).data_root == tmp_path / "explicit"
    monkeypatch.delenv("CSDA_DATA_ROOT")
    assert Settings.load(config_path=str(config)).data_root == tmp_path / "configured"


def test_relative_data_root_is_rejected(monkeypatch):
    with pytest.raises(AppError, match="absolute"):
        Settings.load("relative/root")


def test_import_space_boundary_and_parse_allowance(tmp_path, monkeypatch):
    settings = Settings(tmp_path, reserve_bytes=8)
    free = [208]
    monkeypatch.setattr("cs_demo_analyzer.config.shutil.disk_usage", lambda _: SimpleNamespace(free=free[0]))
    settings.check_space(100, copying=True)
    free[0] = 207
    with pytest.raises(AppError) as failure:
        settings.check_space(100, copying=True)
    assert failure.value.code == "DISK_FULL"
    settings.check_space(100, copying=False)
