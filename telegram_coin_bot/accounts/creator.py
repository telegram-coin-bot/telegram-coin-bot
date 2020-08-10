from telethon import TelegramClient
from telethon.sessions import StringSession


class AccountCreator(TelegramClient):
    def __init__(self, phone=None, password=None, api_id=None, api_hash=None):
        self.phone = phone
        self.password = password
        self.api_id = api_id
        self.api_hash = api_hash
        self.user = None

    async def init(self):
        super().__init__(StringSession(), self.api_id, self.api_hash)

        try:
            await self.connect()
        except IOError:
            print("Initial connection failed. Retrying...")
            await self.connect()

        if not await self.is_user_authorized():
            await self.sign_in(self.phone)

    async def enter_code(self, code):
        self.user = await self.sign_in(code=code, password=self.password)
        await self.disconnect()
        return StringSession.save(self.session)
