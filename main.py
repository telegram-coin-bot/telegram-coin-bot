import asyncio

import config
import utils
from bot import create_bot


async def main():
    accounts = utils.get_all_accounts()
    clients = [
        await create_bot(f"{config.TELETHON_SESSION_NAME}{x}", api_id, api_hash, loop)
        for x, _, _, api_id, api_hash in accounts
    ]
    await asyncio.create_task(*[client.run() for client in clients])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
