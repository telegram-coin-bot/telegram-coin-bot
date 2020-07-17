import asyncio
import enum
import logging
from collections import namedtuple

from bs4 import BeautifulSoup
from httpx import AsyncClient
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.network import ConnectionTcpAbridged
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

import config
import utils


class State(enum.Enum):
    START = 0
    START_VISITING_SITE = 1
    GETTING_WAIT_TIME = 2
    GETTING_REWARD_INFO = 3
    NO_NEW_TASKS = 4
    SKIPPING_TASK = 5


StateHandler = namedtuple("StateHandler", "state callback")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")


class Bot(TelegramClient):
    state_handlers = []

    def __init__(self, session, api_id, api_hash, loop, proxy=None):
        super().__init__(
            session, api_id, api_hash, connection=ConnectionTcpAbridged, proxy=proxy
        )
        self.client = AsyncClient()
        self.current_state = State.START

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
            await asyncio.sleep(60 * 5)

    @staticmethod
    def register_state_handler(state, callback):
        Bot.state_handlers.append(StateHandler(state=state, callback=callback))

    @staticmethod
    def state_handler(state):
        def decorator(callback):
            Bot.register_state_handler(state=state, callback=callback)
            return callback

        return decorator

    async def message_handler(self, event: events.NewMessage.Event):
        for state_handler in self.state_handlers:
            if state_handler.state == self.current_state:
                s = await state_handler.callback(self, event)
                if s is not None:
                    self.current_state = s
                break


async def create_bot(session, api_id, api_hash, loop, proxy=None):
    bot = Bot(session, api_id, api_hash, loop, proxy)
    await bot._init()

    return bot


@Bot.state_handler(State.START)
async def start_handler(bot: Bot, event: events.NewMessage.Event):
    logging.info("Поехали!")
    await event.respond("/visit")
    return State.START_VISITING_SITE


@Bot.state_handler(State.START_VISITING_SITE)
async def start_visiting_site(bot: Bot, event: events.NewMessage.Event):
    logging.info("Приступаем к заданию")
    message = event.message
    if "Sorry, there are no new ads available." in message.message:
        logging.info("Нет новых заданий.")
        await asyncio.sleep(config.DELAY_BETWEEN_GETTING_TASKS)
        await event.respond("/visit")
        return State.START_VISITING_SITE
    try:
        url = message.reply_markup.rows[0].buttons[0].url
    except:
        logging.error("Не могу найти url")
        await event.respond("/visit")
        return State.START_VISITING_SITE
    bot.current_state = State.GETTING_WAIT_TIME
    try:
        response = await bot.client.get(url)
    except:
        logging.error("Не получилось выполнить запрос")
        await asyncio.sleep(30)
        return State.START_VISITING_SITE
    soup = BeautifulSoup(response.content, "lxml")
    potential_captcha = soup.select_one(".card .card-body .text-center h6")
    if potential_captcha is not None and "captcha" in potential_captcha.text.lower():
        logging.info("Найдена капча. Пропускаем задание")
        bot.current_state = State.SKIPPING_TASK
        await bot(
            GetBotCallbackAnswerRequest(
                config.BOT_ADDRESS,
                message.id,
                data=message.reply_markup.rows[1].buttons[1].data,
            )
        )
        return None
    p = soup.select_one("#headbar.container-fluid")
    if p is not None:
        wait_time = int(p["data-timer"])
        logging.info("Нестандартное задание")
        logging.info(f"Ожидаем {wait_time} с.")
        await asyncio.sleep(wait_time)
        await bot.client.post(
            "https://dogeclick.com/reward",
            data={"code": p["data-code"], "token": p["data-token"]},
        )


@Bot.state_handler(State.GETTING_WAIT_TIME)
async def getting_wait_time(bot: Bot, event: events.NewMessage.Event):
    return State.GETTING_REWARD_INFO


@Bot.state_handler(State.GETTING_REWARD_INFO)
async def getting_reward_info(bot: Bot, event: events.NewMessage.Event):
    return State.START_VISITING_SITE


@Bot.state_handler(State.SKIPPING_TASK)
async def skipping_task(bot: Bot, event: events.NewMessage.Event):
    logging.info("Задание пропущено")
    return State.START_VISITING_SITE


@Bot.state_handler(State.NO_NEW_TASKS)
async def no_new_tasks(bot: Bot, event: events.NewMessage.Event):
    pass
