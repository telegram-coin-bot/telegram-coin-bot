import asyncio
import utils
import config
from bot import Bot


def main():
    loop = asyncio.get_event_loop()
    accounts = utils.get_all_accounts()
    clients = [Bot(f"{config.TELETHON_SESSION_NAME}{x}", api_id, api_hash, loop) for x, _, _, api_id, api_hash in
               accounts]
    loop.run_until_complete(asyncio.gather(*[client.run() for client in clients]))


if __name__ == '__main__':
    main()
