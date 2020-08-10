import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
import telethon
from telegram_coin_bot.accounts.creator import AccountCreator
from telegram_coin_bot.bot_manager import consts, keyboard
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegram_coin_bot.accounts.manager import AccountsManager
from telegram_coin_bot.utils.config import Config, PROJECT_PATH
from telegram_coin_bot.db.schema import Session, Money
import os
import peewee

# Configure logging
from telegram_coin_bot.utils.db import create_tables

"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_id: int):
        self.access_id = access_id
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != int(self.access_id):
            await message.answer("Access Denied")
            raise CancelHandler()


logging.basicConfig(level=logging.INFO)

accounts_manager = AccountsManager()

storage = MemoryStorage()
bot = Bot(token=Config.BOT_TOKEN.value)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(Config.TG_USER_ID.value))


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await bot.send_message(
        message.from_user.id, "Welcome", reply_markup=keyboard.MAIN_MENU
    )


@dp.callback_query_handler(text=consts.BACK_BUTTON_DATA)
async def back(query: types.CallbackQuery):
    await query.answer("")
    await bot.send_message(
        query.from_user.id, "Welcome", reply_markup=keyboard.MAIN_MENU
    )


@dp.message_handler(Text(equals=consts.SETTINGS_BUTTON_TEXT))
async def settings(message: types.Message):
    await message.reply("Coming soon...")


@dp.message_handler(Text(equals=consts.ACCOUNTS_BUTTON_TEXT))
async def accounts(message: types.Message):
    await bot.send_message(
        message.from_user.id, "Accounts", reply_markup=keyboard.ACCOUNTS_MENU
    )


@dp.message_handler(Text(equals=consts.BALANCE_BUTTON_TEXT))
async def balance(message: types.Message):
    total_balance = 0
    for m in Money.select():
        total_balance += m.amount
    await bot.send_message(message.from_user.id, f"Total balance: {total_balance: .9f}")


@dp.message_handler(Text(equals=consts.START_BOT_TEXT))
async def start_bot_earning(message: types.Message):
    await bot.send_message(message.from_user.id, "Bot started")
    bot.loop.create_task(accounts_manager.start(bot.loop))


@dp.message_handler(Text(equals=consts.STOP_BOT_TEXT))
async def stop_bot_earning(message: types.Message):
    await bot.send_message(message.from_user.id, "Bot stopped")
    bot.loop.create_task(accounts_manager.stop())


@dp.callback_query_handler(text=consts.LIST_ACCOUNTS_BUTTON_DATA)
async def list_accounts(query: types.CallbackQuery):
    await query.answer()
    sessions = Session.select()
    phones = "\n".join(
        [
            f"{i + 1}) {s.phone[:4] + '.' * 3 + s.phone[-2:]}"
            for i, s in enumerate(sessions[:5])
        ]
    )
    await bot.send_message(query.from_user.id, f"Accounts ({len(sessions)})\n{phones}")


class Account(StatesGroup):
    phone = State()
    password = State()
    api_id = State()
    api_hash = State()
    confirmation = State()
    code = State()
    remove = State()


account_creator = AccountCreator()


@dp.callback_query_handler(text=consts.ADD_ACCOUNT_BUTTON_DATA)
async def add_account_start(query: types.CallbackQuery):
    await query.answer("")
    await bot.send_message(query.from_user.id, "Enter the phone (starts with +7)")
    await Account.phone.set()


@dp.message_handler(state=Account.phone)
async def add_account_phone(message: types.Message, state: FSMContext):
    account_creator.phone = message.text
    await bot.send_message(
        message.from_user.id,
        "Enter password (type `!empty` if password doesn't exist)",
    )
    await Account.password.set()


@dp.message_handler(state=Account.password)
async def add_account_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    account_creator.password = password if password != "!empty" else None
    await bot.send_message(message.from_user.id, "Enter api_id")
    await Account.api_id.set()


@dp.message_handler(state=Account.api_id)
async def add_account_api_id(message: types.Message, state: FSMContext):
    account_creator.api_id = message.text
    await bot.send_message(message.from_user.id, "Enter api_hash")
    await Account.api_hash.set()


@dp.message_handler(state=Account.api_hash)
async def add_account_api_hash(message: types.Message, state: FSMContext):
    account_creator.api_hash = message.text
    await bot.send_message(
        message.from_user.id,
        "Confirmation",
        reply_markup=keyboard.ADD_ACCOUNT_CONFIRMATION_KEYBOARD,
    )
    await Account.confirmation.set()


@dp.callback_query_handler(
    state=Account.confirmation, text=consts.ADD_ACCOUNT_CONFIRMATION_YES_DATA
)
async def add_account_confirmation_yes(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    try:
        await account_creator.init()
    except telethon.errors.rpcerrorlist.ApiIdInvalidError as e:
        await bot.send_message(query.from_user.id, repr(e))
        await state.finish()
    else:
        await bot.send_message(
            query.from_user.id,
            "OK. Now I'm trying to login to this account. Enter the code",
        )
        await Account.code.set()


@dp.callback_query_handler(
    state=Account.confirmation, text=consts.ADD_ACCOUNT_CONFIRMATION_NO_DATA
)
async def add_account_confirmation_no(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    await bot.send_message(
        query.from_user.id, "Accounts", reply_markup=keyboard.ACCOUNTS_MENU
    )


@dp.message_handler(state=Account.code)
async def add_account_code(message: types.Message, state: FSMContext):
    code = message.text
    session = await account_creator.enter_code(code)
    try:
        Session.create(
            phone=account_creator.phone,
            api_id=account_creator.api_id,
            api_hash=account_creator.api_hash,
            session_string=session,
        )
    except peewee.IntegrityError:
        await bot.send_message(message.from_user.id, "Account already in database")
    else:
        await bot.send_message(message.from_user.id, "Account added")
    await state.finish()


@dp.callback_query_handler(text=consts.REMOVE_ACCOUNT_BUTTON_DATA)
async def remove_account_init(query: types.CallbackQuery):
    await query.answer()
    await bot.send_message(query.from_user.id, "Enter the phone (starts with +7)")
    await Account.remove.set()


@dp.message_handler(state=Account.remove)
async def remove_account(message: types.Message, state: FSMContext):
    Session.delete().where(Session.phone == message.text).execute()
    await bot.send_message(message.from_user.id, "Account deleted")
    await state.finish()


def main():
    if not os.path.exists(os.path.join(PROJECT_PATH, "project.db")):
        create_tables()
    executor.start_polling(dp, skip_updates=True)
