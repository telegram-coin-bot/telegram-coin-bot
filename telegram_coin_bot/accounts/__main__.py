import argparse
import asyncio

from telethon.sessions import StringSession

from telegram_coin_bot.accounts.generate_sessions import generate_sessions
from telegram_coin_bot.accounts.manage_accounts import manage_accounts
from telegram_coin_bot.config import POSTGRES_URI
from telegram_coin_bot.db.schema import db


async def _main():
    await db.set_bind(POSTGRES_URI)
    parser = argparse.ArgumentParser(description="Account management tool")
    parser.add_argument("--generate-sessions", action="store_true")
    ns = parser.parse_args()
    if ns.generate_sessions:
        await generate_sessions()
    else:
        await manage_accounts()
    await db.pop_bind().close()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
