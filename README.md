# Telegram Coin Bot
![Preview](https://i.imgur.com/dGC2Ay8.png)

Бот, который выполняет задания ботов [dogeclick](https://dogeclick.com/), для добычи криптовалюты.

Проект находится в очень сыром виде. [Помощь](.github/CONTRIBUTING.md) приветствуется.

## Установка
1. `pip install -e git+https://github.com/telegram-coin-bot/telegram-coin-bot#egg=telegram_coin_bot`
2. Зарегистрировать Telegram-аккаунты (см. правила регистрации аккаунтов)
3. Установить [PostgreSQL](https://www.postgresql.org/download/)
4. Создать базу данных и пользователя. (см. Создание БД)
5. Создать Telegram Application.
6. Запустить `telegram_coin_bot_config`, указать всё, что требуется
7. `telegram_coin_bot_db upgrade head`
8. Запустить `telegram_coin_bot_accounts`, добавить аккаунты
9. Сгенерировать сессии `telegram_coin_bot_accounts --generate-sessions`

## Создание БД
Например, так
```sql
CREATE USER telegram_coin_user WITH ENCRYPTED PASSWORD 'telegram_coin_password'; 
CREATE DATABASE telegram_coin_db;
GRANT ALL PRIVILEGES ON DATABASE telegram_coin_db to telegram_coin_user;
```
## Использование
1. Запустите `telegram_coin_bot_visit_sites`, чтобы начать добывать криптоволюту
2. Проверить баланс &mdash; `telegram_coin_bot_balance`
## Правила регистрации аккаунтов

## Связь
1. [Telegram-канал](https://t.me/joinchat/Uue9YBXPFKDlkFpTvH_qSA)