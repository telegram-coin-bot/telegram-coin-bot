import asyncio

from telegram_coin_bot import config
from telegram_coin_bot.bot import create_bot
from telegram_coin_bot.db.schema import Session, db
from telegram_coin_bot.handlers import visit_sites


async def main():
    await db.set_bind(config.POSTGRES_URI)
    sessions = await db.all(Session.query)
    clients = [
        await create_bot(
            session.session_string,
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_ID,
            session.phone,
        )
        for session in sessions
    ]
    await asyncio.gather(
        *[client.send_message(config.BOT_ADDRESS, "/menu") for client in clients]
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
