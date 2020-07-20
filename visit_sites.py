import asyncio
import logging

from bs4 import BeautifulSoup
from telethon import events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

import config
from bot import Bot, State


@Bot.state_handler(State.START)
async def start_handler(bot: Bot, event: events.NewMessage.Event):
    logging.info(f"{bot.phone}: Поехали!")
    await event.respond("/visit")
    return State.START_VISITING_SITE


@Bot.state_handler(State.START_VISITING_SITE)
async def start_visiting_site(bot: Bot, event: events.NewMessage.Event):
    logging.info(f"{bot.phone}: Приступаем к заданию")
    message = event.message
    if "Sorry, there are no new ads available." in message.message:
        logging.info(f"{bot.phone}: Нет новых заданий.")
        await asyncio.sleep(config.DELAY_BETWEEN_GETTING_TASKS)
        await event.respond("/visit")
        return State.START_VISITING_SITE
    try:
        url = message.reply_markup.rows[0].buttons[0].url
    except:
        logging.error(f"{bot.phone}: Не могу найти url в сообщении")
        await event.respond("/visit")
        return State.START_VISITING_SITE
    bot.current_state = State.GETTING_WAIT_TIME
    try:
        response = await bot.client.get(url)
    except:
        logging.error(
            f"{bot.phone}: Не получилось выполнить запрос: {url}", exc_info=True
        )
        await skip_task(bot, message)
        return
    soup = BeautifulSoup(response.content, "lxml")
    potential_captcha = soup.select_one(".card .card-body .text-center h6")
    potential_error = soup.select_one(".card .card-body .text-center p")
    if potential_captcha and potential_captcha.text.startswith("Please solve"):
        logging.info(f"{bot.phone}: Найдена капча. Пропускаем задание")
        await skip_task(bot, message)
        return
    if (
        potential_error
        and "Sorry, but the link you used is not valid." == potential_error.text
    ):
        logging.info(f"{bot.phone}: Невалидная ссылка. Пропуск задания")
        await skip_task(bot, message)
        return
    p = soup.select_one("#headbar.container-fluid")
    if p is not None:
        wait_time = int(p["data-timer"])
        logging.info(f"{bot.phone}: Нестандартное задание")
        await asyncio.sleep(wait_time)
        await bot.client.post(
            "https://dogeclick.com/reward",
            data={"code": p["data-code"], "token": p["data-token"]},
        )
    logging.info(f"{bot.phone}: Задание выполнено успешно")


@Bot.state_handler(
    func=lambda ev: ev.message.message.startswith("Please stay on the site")
    or ev.message.message.startswith("You must stay on the site")
)
async def getting_wait_time(bot: Bot, event: events.NewMessage.Event):
    logging.info(f"{bot.phone}: {event.message.message}")
    return State.GETTING_REWARD_INFO


@Bot.state_handler(func=lambda ev: ev.message.message.startswith("You earned"))
async def getting_reward_info(bot: Bot, event: events.NewMessage.Event):
    logging.info(f"{bot.phone}: {event.message.message}")
    return State.START_VISITING_SITE


@Bot.state_handler(func=lambda ev: ev.message.message.startswith("Skipping task..."))
async def skipping_task(bot: Bot, event: events.NewMessage.Event):
    logging.info(f"{bot.phone}: Задание пропущено")
    return State.START_VISITING_SITE


@Bot.state_handler(State.NO_NEW_TASKS)
async def no_new_tasks(bot: Bot, event: events.NewMessage.Event):
    pass


async def skip_task(bot, message):
    await bot(
        GetBotCallbackAnswerRequest(
            config.BOT_ADDRESS,
            message.id,
            data=message.reply_markup.rows[1].buttons[1].data,
        )
    )
