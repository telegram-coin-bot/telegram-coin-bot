import asyncio

from telegram_coin_bot.bot import create_bot
from telegram_coin_bot.db.schema import Account, Session, db
from telegram_coin_bot.utils.config import Config
from telegram_coin_bot.utils.db import try_to_connect


async def _main():
    await try_to_connect(db, Config.POSTGRES_URI.value)
    sessions = await db.all(Session.query)
    total_balance = 0
    clients = [
        await create_bot(
            session.session_string,
            Config.API_ID.value,
            Config.API_HASH.value,
            session.phone,
        )
        for session in sessions
    ]
    for client in clients:
        print(f"Enter in account: {client.phone}")
        print(f"BOT ADDRESS: {Config.BOT_ADDRESS.value}")
        if (await client.get_messages(Config.BOT_ADDRESS.value)).total == 0:
            await client.send_message(Config.BOT_ADDRESS.value, "/start")
            await asyncio.sleep(3)
        await client.send_message(Config.BOT_ADDRESS.value, "/balance")
        await asyncio.sleep(5)
        text = (await client.get_messages(Config.BOT_ADDRESS.value, limit=1))[0].message
        balance = float(text.replace("Available balance: ", "").replace(" LTC", ""))
        print(f"Balance in account: {client.phone} {balance:.9f} LTC")
        total_balance += balance
    print(f"Общий баланс со всех аккаунтов: {total_balance:.9f} LTC")


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(_main())
    loop.run_forever()


if __name__ == "__main__":
    main()
