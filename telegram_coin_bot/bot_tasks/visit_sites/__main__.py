import asyncio
import asyncpg
from telegram_coin_bot.utils.config import Config
from telegram_coin_bot.bot import create_bot
from telegram_coin_bot.db.schema import Session, db
from telegram_coin_bot.utils.db import try_to_connect
from telegram_coin_bot.handlers import visit_sites


async def _main():
    await try_to_connect(db, Config.POSTGRES_URI.value)
    sessions = await db.all(Session.query)
    clients = [
        await create_bot(
            session.session_string,
            Config.API_ID.value,
            Config.API_HASH.value,
            session.phone,
        )
        for session in sessions
    ]
    await asyncio.gather(
        *[client.send_message(Config.BOT_ADDRESS.value, "/menu") for client in clients]
    )


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(_main())
    loop.run_forever()


if __name__ == "__main__":
    main()
