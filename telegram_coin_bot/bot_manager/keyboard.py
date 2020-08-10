from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram_coin_bot.bot_manager import consts


MAIN_MENU = (
    ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    .add(
        KeyboardButton(consts.SETTINGS_BUTTON_TEXT),
        KeyboardButton(consts.BALANCE_BUTTON_TEXT),
    )
    .add(KeyboardButton(consts.ACCOUNTS_BUTTON_TEXT))
    .add(KeyboardButton(consts.START_BOT_TEXT), KeyboardButton(consts.STOP_BOT_TEXT))
)

ACCOUNTS_MENU = (
    InlineKeyboardMarkup()
    .add(
        InlineKeyboardButton(
            consts.ADD_ACCOUNT_BUTTON_TEXT, callback_data=consts.ADD_ACCOUNT_BUTTON_DATA
        ),
        InlineKeyboardButton(
            consts.REMOVE_ACCOUNT_BUTTON_TEXT,
            callback_data=consts.REMOVE_ACCOUNT_BUTTON_DATA,
        ),
    )
    .add(
        InlineKeyboardButton(
            consts.LIST_ACCOUNTS_BUTTON_TEXT,
            callback_data=consts.LIST_ACCOUNTS_BUTTON_DATA,
        ),
        InlineKeyboardButton(
            consts.BACK_BUTTON_TEXT, callback_data=consts.BACK_BUTTON_DATA
        ),
    )
)

ADD_ACCOUNT_CONFIRMATION_KEYBOARD = InlineKeyboardMarkup().add(
    InlineKeyboardButton(
        consts.ADD_ACCOUNT_CONFIRMATION_YES_TEXT,
        callback_data=consts.ADD_ACCOUNT_CONFIRMATION_YES_DATA,
    ),
    InlineKeyboardButton(
        consts.ADD_ACCOUNT_CONFIRMATION_NO_TEXT,
        callback_data=consts.ADD_ACCOUNT_CONFIRMATION_NO_DATA,
    ),
)
