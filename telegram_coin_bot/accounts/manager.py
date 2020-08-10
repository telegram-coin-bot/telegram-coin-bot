import asyncio

from telegram_coin_bot.bot import create_bot
from telegram_coin_bot.db.schema import Session
from telegram_coin_bot.handlers import visit_sites
from telegram_coin_bot.utils.config import Config


class AccountsManager:
    def __init__(self):
        self.accounts = []
        self.tasks = []
        self.started = False

    async def start(self, loop):
        if self.started:
            return
        self.started = True
        self.accounts = [
            await create_bot(
                session.session_string, session.api_id, session.api_hash, session.phone,
            )
            for session in Session.select()
        ]
        await asyncio.gather(
            *[
                account.send_message(Config.BOT_ADDRESS.value, "/menu")
                for account in self.accounts
            ]
        )

    async def stop(self):
        await asyncio.gather(*[account.disconnect() for account in self.accounts])
        self.started = False
