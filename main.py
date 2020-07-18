import asyncio

import config
import utils
from bot import create_bot
import visit_sites


async def main():
    accounts = utils.get_all_accounts()
    clients = [
        await create_bot(f"{config.TELETHON_SESSION_NAME}{x}", api_id, api_hash)
        for x, _, _, api_id, api_hash in accounts
    ]
    tasks = [asyncio.create_task(client.run()) for client in clients]
    await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
