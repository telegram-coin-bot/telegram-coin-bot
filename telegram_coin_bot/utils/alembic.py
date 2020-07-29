import os
from pathlib import Path
from types import SimpleNamespace
from typing import Union

from alembic.config import Config
from configargparse import Namespace

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(
    cmd_opts: Union[Namespace, SimpleNamespace], base_path: str = PROJECT_PATH
) -> Config:
    """
    Создает объект конфигурации alembic на основе аргументов командной строки,
    подменяет относительные пути на абсолютные.
    """
    # Подменяем путь до файла alembic.ini на абсолютный
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Подменяем путь до папки с alembic на абсолютный
    alembic_location = config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            "script_location", os.path.join(base_path, alembic_location)
        )
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config
