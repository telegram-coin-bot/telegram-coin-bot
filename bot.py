import asyncio
import enum
import logging
from collections import namedtuple

from httpx import AsyncClient
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.network import ConnectionTcpAbridged
from telethon.sessions import StringSession

import config


class State(enum.Enum):
    START = 0
    START_VISITING_SITE = 1
    GETTING_WAIT_TIME = 2
    GETTING_REWARD_INFO = 3
    NO_NEW_TASKS = 4
    SKIPPING_TASK = 5
    STOP = 6


StateHandler = namedtuple("StateHandler", "state func callback")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")


class Bot(TelegramClient):
    state_handlers = []

    def __init__(self, session, api_id, api_hash, phone, proxy=None):
        super().__init__(
            session, api_id, api_hash, connection=ConnectionTcpAbridged, proxy=proxy
        )
        self.client = AsyncClient()
        self.current_state = State.START
        self._phone = phone[1:] if phone[0] == "+" else phone

    @property
    def phone(self):
        return self._phone[:3] + "*" * 4 + self._phone[-2:]

    async def _init(self):
        try:
            await self.connect()
        except IOError:
            print("Initial connection failed. Retrying...")
            await self.connect()

        if not await self.is_user_authorized():
            print("First run. Sending code request...")
            user_phone = input("Enter your phone: ")
            await self.sign_in(user_phone)

            self_user = None
            while self_user is None:
                code = input("Enter the code you just received: ")
                try:
                    self_user = await self.sign_in(code=code)

                # Two-step verification may be enabled, and .sign_in will
                # raise this error. If that's the case ask for the password.
                # Note that getpass() may not work on PyCharm due to a bug,
                # if that's the case simply change it for input().
                except SessionPasswordNeededError:
                    pw = input(
                        "Two step verification is enabled. "
                        "Please enter your password: "
                    )

                    self_user = await self.sign_in(password=pw)

    async def get_user_id(self):
        me = await self.get_me()
        return me.id

    async def run(self):
        messages = await self.get_messages(config.BOT_ADDRESS)
        if not messages.total:
            logging.info("Начинаем диалог с ботом")
            await self.send_message(config.BOT_ADDRESS, "/start")

        self.add_event_handler(
            self.message_handler,
            events.NewMessage(incoming=True, chats="Litecoin_click_bot"),
        )
        await self.send_message(config.BOT_ADDRESS, "/menu")
        while 1:
            if self.current_state == State.STOP:
                return
            await asyncio.sleep(5)

    @staticmethod
    def register_state_handler(state, func, callback):
        Bot.state_handlers.append(
            StateHandler(state=state, func=func, callback=callback)
        )

    @staticmethod
    def state_handler(state=None, func=None):
        def decorator(callback):
            Bot.register_state_handler(state=state, func=func, callback=callback)
            return callback

        return decorator

    async def message_handler(self, event: events.NewMessage.Event):
        for state_handler in self.state_handlers:
            if state_handler.state == self.current_state or (
                state_handler.func and state_handler.func(event)
            ):
                s = await state_handler.callback(self, event)
                if s is not None:
                    self.current_state = s
                break


async def create_bot(session, api_id, api_hash, phone, proxy=None):
    bot = Bot(session, api_id, api_hash, phone, proxy)
    await bot._init()

    return bot
