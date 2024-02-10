import typing
import typing_extensions
import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

log = logging.getLogger(__name__)


def get_settings() -> "ServerSettings":
    """Get the settings"""
    load_dotenv(get_dotenv_path())
    return ServerSettings()


def get_dotenv_path() -> Path:
    """Get the location of the settings file"""
    return Environment().dot_env_path


class Environment(BaseSettings):
    dot_env_path: Path = "emulator.env"

    class Config:
        env_prefix = "OICP_SERVER_"


class ServerSettings(BaseSettings):
    maximum_runs: int = Field(
        default=20,
        gt=0,
        description="The maximum nmber of runs to allow HTTP clients to create before auto-deleting old ones.",
    )

    class Config:
        env_prefix = "OICP_SERVER_"
