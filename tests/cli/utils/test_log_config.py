from pathlib import Path
from typing import Optional

import pytest
import typer

from faststream.cli.utils.logs import check_log_config_path


@pytest.mark.parametrize(
    "path",
    [
        Path("a/b/c/e.json"),
        Path("config.json"),
        Path("config.yaml"),
        Path("config.yml"),
        None,
    ],
)
def test_valid(path: Optional[Path]):
    check_log_config_path(path)


@pytest.mark.parametrize(
    "path", ["empty", "json.txt", "yaml.txt", "yml.txt", "config.json.txt"]
)
def test_invalid(path: str):
    with pytest.raises(typer.BadParameter):
        check_log_config_path(Path(path))
