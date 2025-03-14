import logging
from collections import defaultdict
from enum import Enum
from logging.config import dictConfig
from pathlib import Path
from typing import TYPE_CHECKING, DefaultDict, Optional, Union

import typer
import yaml

from faststream._compat import json_loads


if TYPE_CHECKING:
    from faststream._internal.application import Application
    from faststream.types import AnyDict, LoggerProto


class LogLevels(str, Enum):
    """A class to represent log levels.

    Attributes:
        critical : critical log level
        error : error log level
        warning : warning log level
        info : info log level
        debug : debug log level
    """

    critical = "critical"
    fatal = "fatal"
    error = "error"
    warning = "warning"
    warn = "warn"
    info = "info"
    debug = "debug"
    notset = "notset"


LOG_LEVELS: DefaultDict[str, int] = defaultdict(
    lambda: logging.INFO,
    **{
        "critical": logging.CRITICAL,
        "fatal": logging.FATAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "warn": logging.WARN,
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "notset": logging.NOTSET,
    },
)


def get_log_level(level: Union[LogLevels, str, int]) -> int:
    """Get the log level.

    Args:
        level: The log level to get. Can be an integer, a LogLevels enum value, or a string.

    Returns:
        The log level as an integer.

    """
    if isinstance(level, int):
        return level

    if isinstance(level, LogLevels):
        return LOG_LEVELS[level.value]

    if isinstance(level, str):  # pragma: no branch
        return LOG_LEVELS[level.lower()]


def set_log_level(level: int, app: "Application") -> None:
    """Sets the log level for an application."""
    if app.logger and getattr(app.logger, "setLevel", None):
        app.logger.setLevel(level)  # type: ignore[attr-defined]

    broker_logger: Optional[LoggerProto] = getattr(app.broker, "logger", None)
    if broker_logger is not None and getattr(broker_logger, "setLevel", None):
        broker_logger.setLevel(level)  # type: ignore[attr-defined]


def check_log_config_path(path: Optional[Path]) -> Optional[Path]:
    if path and not path.suffix.endswith(("json", "yaml", "yml")):
        raise typer.BadParameter(
            "Only json and yaml files are supported for logging configuration files."
        )
    return path


def load_log_config(path: Path) -> "AnyDict":
    """Loads logging configuration dictionary from the given json or yaml file."""
    loader = json_loads if path.suffix == ".json" else yaml.safe_load

    with path.open() as f:
        cfg = loader(f.read())

    assert isinstance(
        cfg, dict
    ), f"Logging configuration file must contain dict-like object. Got: {type(cfg)}"

    return cfg


def set_log_config(config: "AnyDict") -> None:
    """Sets the log config from the given file."""
    dictConfig(config)
