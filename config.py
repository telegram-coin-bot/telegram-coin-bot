import os

# Адрес бота, с которым будут общаться аккаунты
BOT_ADDRESS = "Litecoin_click_bot"
# BOT_ADDRESS = "Dogecoin_click_bot"
# BOT_ADDRESS = "BCH_clickbot"
# BOT_ADDRESS = "Zcash_click_bot"
# BOT_ADDRESS = "BitcoinClick_bot"

# Задержка между попытками получить новые задания, если они закончились
DELAY_BETWEEN_GETTING_TASKS = 5 * 60

# Адрес кошелька для вывода средств
WALLET = ""

# API_ID и API_HASH
# Изначально взято отсюда https://bit.ly/3htWcDt
TELEGRAM_API_ID = 50322
TELEGRAM_API_HASH = "9ff1a639196c0779c86dd661af8522ba"

# Postgres config
POSTGRES_HOST = os.getenv("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", default=5432)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", default="")
POSTGRES_USER = os.getenv("POSTGRES_USER", default="telegram-coin-bot")
POSTGRES_DB = os.getenv("POSTGRES_DB", default="telegram-coin-bot")
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
