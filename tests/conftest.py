"""pytest 公共 fixture"""

from collections.abc import Iterator
from pathlib import Path

import pytest

from app.utils import config as config_module


@pytest.fixture
def temp_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """将工作目录切换到临时目录, 避免污染仓库"""
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture
def clean_config() -> Iterator[dict]:
    """提供干净的 global_config, 测试结束后恢复原内容"""
    original = dict(config_module.global_config)
    config_module.global_config.clear()
    yield config_module.global_config
    config_module.global_config.clear()
    config_module.global_config.update(original)
