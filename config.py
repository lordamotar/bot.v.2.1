from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    token: str
    manager_id: int


@dataclass
class DatabaseConfig:
    database: str = "support_bot.db"


@dataclass
class TgBot:
    config: Config
    db: DatabaseConfig


def load_config() -> TgBot:
    env = Env()
    env.read_env()

    return TgBot(
        config=Config(
            token=env.str("BOT_TOKEN"),
            manager_id=env.int("MANAGER_ID")
        ),
        db=DatabaseConfig()
    )