import argparse
import asyncio

from telegram_coin_bot.accounts.generate_sessions import generate_sessions
from telegram_coin_bot.accounts.manage_accounts import manage_accounts
from telegram_coin_bot.utils.config import Config
from telegram_coin_bot.db.schema import db
from telegram_coin_bot.utils.db import try_to_connect


async def _main():
    await try_to_connect(db, Config.POSTGRES_URI.value)
    parser = argparse.ArgumentParser(description="Account management tool")
    parser.add_argument("--generate-sessions", action="store_true")
    ns = parser.parse_args()
    if ns.generate_sessions:
        await generate_sessions()
    else:
        await manage_accounts()
    await db.pop_bind().close()


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
