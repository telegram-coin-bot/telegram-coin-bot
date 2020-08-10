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

    BOT_TOKEN = ConfigUnit("telethon", "bot_token", description="Токен бота")

    TG_USER_ID = ConfigUnit(
        "telethon", "tg_user_id", description="Admin's user id (https://bit.ly/30KuyfC)"
    )
