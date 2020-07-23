import asyncio

from telegram_coin_bot import config, utils
from telegram_coin_bot.bot import create_bot
from telegram_coin_bot.handlers import visit_sites


async def main():
    accounts = utils.get_all_accounts()
    clients = [
        await create_bot(f"{config.TELETHON_SESSION_NAME}{x}", api_id, api_hash, phone)
        for x, phone, _, api_id, api_hash in accounts
    ]
    await asyncio.gather(
        *[client.send_message(config.BOT_ADDRESS, "/menu") for client in clients]
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
