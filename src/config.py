import os
from configparser import ConfigParser
from functools import lru_cache
from typing import Any

import typer
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from src.logger import configure_log_listener, get_logger


class AppConfig(BaseSettings):
    app_name: str = ""
    environment: str = "dev"

    image_host: str = ""
    image_repo: str = ""
    image_tag: str = ""

    # logging
    log_console: bool = True
    log_file: str = "main.log"
    max_file_size_mb: int = 1
    retention_days: int = 30

    message: str = "default message"

    class Config:
        type_ = ConfigDict
        env_file = ".env"


@lru_cache
def get_config(
    ini_path: str = "configs/main.ini",
    environment: str = os.environ.get("ENVIRONMENT", "dev"),
    **kwargs: Any,  # noqa: ANN401
) -> AppConfig:
    # read configs
    parser = ConfigParser()
    parser.read(ini_path)
    # environment config
    config = dict(parser[environment].items())
    config.update(kwargs)
    return AppConfig(**config)  # type: ignore[arg-type]


config = get_config()

# config logger
configure_log_listener(console=config.log_console, log_path=config.log_file, max_file_size_mb=config.max_file_size_mb
                       , retention_days=config.retention_days)
logger = get_logger(config.app_name)
logger.debug("config", extra={"config": config.model_dump()})


def main(key: str) -> None:
    """Print config value of specified key."""
    typer.echo(config.model_dump().get(key))


if __name__ == "__main__":
    typer.run(main)
