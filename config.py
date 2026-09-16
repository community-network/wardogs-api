import json
from dataclasses import dataclass

from environs import Env


@dataclass
class Api:
    steam_openid: str
    social_host: str
    game_host: str
    game_shard_id: str
    auth_base_url: str
    shared_key: str

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
        return Api(
            steam_openid=steam_openid,
            social_host=social_host,
            game_host=game_host,
            game_shard_id=game_shard_id,
            auth_base_url=auth_base_url,
            shared_key=shared_key,
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
