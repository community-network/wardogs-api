import logging
import os
from dataclasses import dataclass
import sys

from environs import Env
from pydantic import BaseModel


@dataclass
class Api:
    steam_openid: str
    social_host: str
    game_host: str
    game_shard_id: str
    auth_base_url: str
    shared_key: str
    steam_web_api_key: str

    @staticmethod
    def from_env(env: Env):
        steam_openid = env.str(
            "STEAM_OPENID", "https://steamcommunity.com/openid/login"
        )
        social_host = env.str(
            "SOCIAL_HOST", "https://social.live.wardogs.bulkhead.pragmaengine.com"
        )
        game_host = env.str(
            "GAME_HOST", "https://game.live.wardogs.bulkhead.pragmaengine.com"
        )
        game_shard_id = env.str("GAME_SHARD_ID", "00000000-0000-0000-0000-000000000001")
        auth_base_url = env.str("AUTH_BASE_URL")
        shared_key = env.str("SHARED_KEY")
        steam_web_api_key = env.str("STEAM_WEB_API_KEY")
        return Api(
            steam_openid=steam_openid,
            social_host=social_host,
            game_host=game_host,
            game_shard_id=game_shard_id,
            auth_base_url=auth_base_url,
            shared_key=shared_key,
            steam_web_api_key=steam_web_api_key,
        )


@dataclass
class Db:
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    db_port: int = 5432

    @staticmethod
    def from_env(env: Env):
        db_host = env.str("DB_HOST")
        postgres_password = env.str("POSTGRES_PASSWORD")
        postgres_user = env.str("POSTGRES_USER")
        postgres_db = env.str("POSTGRES_DB")
        db_port = env.int("DB_PORT", 5432)
        return Db(
            postgres_user=postgres_user,  # type: ignore
            postgres_password=postgres_password,  # type: ignore
            postgres_db=postgres_db,  # type: ignore
            db_host=db_host,  # type: ignore
            db_port=db_port,
        )


@dataclass
class Config:
    api: Api
    db: Db


def load_config() -> Config:
    env = Env()
    env.read_env()

    return Config(
        api=Api.from_env(env),
        db=Db.from_env(env),
    )


class PackagePathFilter(logging.Filter):
    def filter(self, record):
        pathname = record.pathname
        record.relativepath = None
        abs_sys_paths = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.relativepath = os.path.relpath(pathname, path)
                break
        return True


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "api"
    LOG_FORMAT: str = "%(levelprefix)s %(relativepath)s:%(lineno)d: %(message)s"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {
            "handlers": ["default"],
            "propagate": "yes",
            "level": LOG_LEVEL.upper(),
        },
    }
    root: dict = {
        "level": "INFO",
        "handlers": ["default"],
        "propagate": "no",
    }
