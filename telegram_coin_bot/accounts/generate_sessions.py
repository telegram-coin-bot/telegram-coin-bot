from telethon import TelegramClient
from telethon.sessions import StringSession

from telegram_coin_bot.utils.config import Config
from telegram_coin_bot.db.schema import Account, Session, db


async def generate_sessions():
    accounts = await db.all(Account.query)
    for account in accounts:
        print(f"Входим в аккаунт {account.phone}...")
        client = TelegramClient(
            StringSession(), Config.API_ID.value, Config.API_HASH.value
        )
        await client.start(phone=account.phone, password=account.password)
        session_string = client.session.save()
        session = await Session.query.where(Session.phone == account.phone).gino.first()
        if not session:
            await Session.create(phone=account.phone, session_string=session_string)
        else:
            await session.update(session_string=session_string).apply()
        await client.disconnect()
