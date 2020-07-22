import asyncio
import enum
import logging
from collections import namedtuple

from httpx import AsyncClient
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.events.common import EventBuilder
from telethon.network import ConnectionTcpAbridged
from telethon.sessions import StringSession

from telegram_coin_bot import config, utils

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")


class Bot(TelegramClient):
    handlers = []

    def __init__(self, session, api_id, api_hash, phone, proxy=None):
        super().__init__(session, api_id, api_hash, proxy=proxy)
        for handler in self.handlers:
            self.add_event_handler(*handler)
        self.client = AsyncClient()
        self._phone = phone[1:] if phone[0] == "+" else phone

    @property
    def phone(self):
        return self._phone[:3] + "*" * 4 + self._phone[-2:]

    @staticmethod
    def register_handler(event_handler: EventBuilder):
        def decorator(callback):
            Bot.handlers.append((callback, event_handler))
            return callback

        return decorator


async def create_bot(session, api_id, api_hash, phone, proxy=None):
    bot = Bot(session, api_id, api_hash, phone, proxy)
    await bot.start()

    return bot
