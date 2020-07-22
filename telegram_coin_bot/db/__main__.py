import argparse
import logging
import os

from alembic.config import CommandLine
from telegram_coin_bot.config import POSTGRES_URI
from telegram_coin_bot.utils import make_alembic_config


def main():
    logging.basicConfig(level=logging.DEBUG)

    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    alembic.parser.add_argument(
        "--pg-url",
        default=os.getenv("POSTGRES_URI", POSTGRES_URI),
        help="Database URL [env var: POSTGRES_URI]",
    )

    options = alembic.parser.parse_args()
    if "cmd" not in options:
        alembic.parser.error("too few arguments")
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


if __name__ == "__main__":
    main()
