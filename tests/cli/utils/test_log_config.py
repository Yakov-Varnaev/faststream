from pathlib import Path

import pytest
import typer

from faststream.cli.utils.logs import check_log_config_path


@pytest.mark.parametrize(
    "path", ["a/b/c/e.json", "config.json", "config.yaml", "config.yml"]
)
def test_valid(path: str):
    check_log_config_path(Path(path))


@pytest.mark.parametrize(
    "path", ["empty", "json.txt", "yaml.txt", "yml.txt", "config.json.txt"]
)
def test_invalid(path: str):
    with pytest.raises(typer.BadParameter):
        check_log_config_path(Path(path))
