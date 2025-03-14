import json
from pathlib import Path

import pytest

from faststream import FastStream


@pytest.fixture
def broker():
    # separate import from e2e tests
    from faststream.rabbit import RabbitBroker

    return RabbitBroker()


@pytest.fixture
def app_without_logger(broker):
    return FastStream(broker, None)


@pytest.fixture
def app_without_broker():
    return FastStream()


@pytest.fixture
def app(broker):
    return FastStream(broker)


@pytest.fixture
def log_config_file_path() -> Path:
    return Path(__file__).parent / "log_config.json"


@pytest.fixture
def log_config_dict(log_config_file_path: Path) -> dict:
    with log_config_file_path.open() as f:
        return json.load(f)
