import os
from pathlib import Path
from configparser import ConfigParser

PROJECT_PATH = Path(__file__).parent.parent.resolve()

config_file = os.path.join(PROJECT_PATH, "config.ini")


class ConfigUnit:
    def __init__(self, section, name, value=None, default_value=None, description=None):
        self._section = section
        self._name = name
        self._value = value
        self._default_value = default_value
        self._description = description

    @property
    def section(self):
        return self._section

    @property
    def name(self):
        return self._name

    @property
    def default_value(self):
        return self._default_value

    @property
    def description(self):
        return self._description

    @property
    def value(self):
        return Config.get_raw(self.section, self.name)

    def set_value(self, val):
        self._value = val


class Config:
    _config = ConfigParser()
    _config.read(config_file)

    @classmethod
    def set(cls, section, key, value):
        cls._config.set(section, key, value)
        for var in vars(cls).values():
            if (
                isinstance(var, ConfigUnit)
                and var.section == section
                and var.name == key
            ):
                var.set_value(value)

    @classmethod
    def get_raw(cls, section, key):
        return cls._config.get(section, key)

    @classmethod
    def get_units(cls):
        return [v for v in vars(cls).values() if isinstance(v, ConfigUnit)]

    @staticmethod
    def save():
        with open(config_file, "w") as f:
            Config._config.write(f)

    BOT_ADDRESS = ConfigUnit(
        "application",
        "bot_address",
        default_value="Litecoin_click_bot",
        description="Адрес бота. Доступны: Dogecoin_click_bot, Litecoin_click_bot, BCH_clickbot, Zcash_click_bot, "
        "BitcoinClick_bot",
    )
    DELAY_BETWEEN_GETTING_TASKS = ConfigUnit(
        "application",
        "delay_between_getting_tasks",
        default_value=300,
        description="Задержка между попыткой получить задание (в секундах)",
    )
    WALLET = ConfigUnit(
        "application",
        "wallet",
        description="Криптовалютный кошелёк, куда будут выводиться деньги",
    )
    API_ID = ConfigUnit(
        "telethon",
        "api_id",
        description="https://core.telegram.org/api/obtaining_api_id",
    )
    API_HASH = ConfigUnit(
        "telethon",
        "api_hash",
        description="https://core.telegram.org/api/obtaining_api_id",
    )

    POSTGRES_HOST = ConfigUnit(
        "postgres", "host", default_value="127.0.0.1", description="Хост"
    )
    POSTGRES_PORT = ConfigUnit(
        "postgres", "port", default_value="5432", description="Порт"
    )
    POSTGRES_USER = ConfigUnit(
        "postgres",
        "user",
        default_value="telegram_coin_user",
        description="Имя пользователя",
    )
    POSTGRES_PASSWORD = ConfigUnit(
        "postgres",
        "password",
        default_value="telegram_coin_password",
        description="Пароль",
    )
    POSTGRES_DB = ConfigUnit(
        "postgres", "db", default_value="telegram_coin_db", description="Имя БД"
    )
    POSTGRES_URI = ConfigUnit("postgres", "uri")
