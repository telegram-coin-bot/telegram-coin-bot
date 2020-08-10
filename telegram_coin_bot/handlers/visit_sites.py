import asyncio
import logging

from bs4 import BeautifulSoup
from telethon import events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

from telegram_coin_bot.utils.config import Config
from telegram_coin_bot.bot import Bot
from telegram_coin_bot.db.schema import Money, MoneyType


def is_menu_message(event):
    message = event.message
    if (
        not message.message.startswith("Welcome to")
        or "Visit sites to earn by clicking links" not in message.message
        or "You can also create your own ads with" not in message.message
        or "Use the /help command for more info." not in message.message
    ):
        return False

    return True


def is_visit_site_message(event):
    message = event.message
    if (
        'Press the "Visit website" button to earn' not in message.message
        or "You will be redirected to a third party site." not in message.message
    ):
        return False
    try:
        url_button = message.reply_markup.rows[0].buttons[0]
        report_button = message.reply_markup.rows[1].buttons[0]
        skip_button = message.reply_markup.rows[1].buttons[1]

        if (
            "Go to website" not in url_button.text
            or "Report" not in report_button.text
            or "Skip" not in skip_button.text
        ):
            return False

    except:
        return False
    return True


@Bot.register_handler(events.NewMessage(func=is_menu_message))
async def start_handler(event: events.NewMessage.Event):
    client = event.client
    logging.info(f"{client.phone}: Поехали!")
    await event.respond("/visit")


@Bot.register_handler(events.NewMessage(func=is_visit_site_message))
async def start_visiting_site(event: events.NewMessage.Event):
    client = event.client
    logging.info(f"{client.phone}: Приступаем к заданию")

    message = event.message
    url = message.reply_markup.rows[0].buttons[0].url

    try:
        response = await client.client.get(url)
    except:
        logging.error(
            f"{client.phone}: Не получилось выполнить запрос: {url}", exc_info=True
        )
        await skip_task(client, message)
        return
    soup = BeautifulSoup(response.content, "lxml")
    potential_captcha = soup.select_one(".card .card-body .text-center h6")
    potential_error = soup.select_one(".card .card-body .text-center p")
    if potential_captcha and potential_captcha.text.startswith("Please solve"):
        logging.info(f"{client.phone}: Найдена капча. Пропускаем задание")
        await skip_task(client, message)
        return
    if (
        potential_error
        and "Sorry, but the link you used is not valid." == potential_error.text
    ):
        logging.info(f"{client.phone}: Невалидная ссылка. Пропуск задания")
        await skip_task(client, message)
        return
    p = soup.select_one("#headbar.container-fluid")
    if p is not None:
        wait_time = int(p["data-timer"])
        logging.info(f"{client.phone}: Нестандартное задание")
        await asyncio.sleep(wait_time)
        await client.client.post(
            "https://dogeclick.com/reward",
            data={"code": p["data-code"], "token": p["data-token"]},
        )
    logging.info(f"{client.phone}: Задание выполнено успешно")


@Bot.register_handler(
    events.NewMessage(
        func=lambda ev: ev.message.message.startswith("Please stay on the site")
        or ev.message.message.startswith("You must stay on the site")
    )
)
async def getting_wait_time(event: events.NewMessage.Event):
    client = event.client
    logging.info(f"{client.phone}: {event.message.message}")


@Bot.register_handler(
    events.NewMessage(func=lambda ev: ev.message.message.startswith("You earned"))
)
async def getting_reward_info(event: events.NewMessage.Event):
    client = event.client
    msg = event.message.message.split("\n")[0]
    earned = float(msg.split(" ")[2])
    Money.create(amount=earned, type=MoneyType.ADD.value)
    logging.info(f"{client.phone}: {msg}")


@Bot.register_handler(
    events.NewMessage(func=lambda ev: ev.message.message.startswith("Skipping task..."))
)
async def skipping_task(event: events.NewMessage.Event):
    client = event.client
    logging.info(f"{client.phone}: Задание пропущено")


@Bot.register_handler(
    events.NewMessage(
        func=lambda ev: ev.message.message.startswith(
            "Sorry, there are no new ads available"
        )
    )
)
async def no_new_tasks(event: events.NewMessage.Event):
    client = event.client
    logging.info(f"{client.phone}: Заданий больше нет.")
    await asyncio.sleep(int(Config.DELAY_BETWEEN_GETTING_TASKS.value))
    await event.respond("/visit")


async def skip_task(bot, message):
    await bot(
        GetBotCallbackAnswerRequest(
            Config.BOT_ADDRESS.value,
            message.id,
            data=message.reply_markup.rows[1].buttons[1].data,
        )
    )
