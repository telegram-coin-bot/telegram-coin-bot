import asyncpg
from telegram_coin_bot.db.schema import Account, Session, db


async def add_account():
    phone = input("Введите номер телефона: ")
    password = input("Введите пароль: ")

    if input("Данные введены верно? [Y/n] ").lower() == "n":
        return
    account = await Account.query.where(Account.phone == phone).gino.first()

    if account:
        if input("Номер в таблице уже существует. Обновить? [Y/n] ").lower() == "n":
            return
        await account.update(password=password).apply()
    else:
        await Account.create(phone=phone, password=password)


async def remove_account():
    phone = input("Введите номер телефона: ")
    await Account.delete.where(Account.phone == phone).gino.status()


async def list_accounts():
    accounts = await db.all(Account.query)
    accounts = [i.to_dict() for i in accounts]
    if not accounts:
        return

    keys = sorted(accounts[0].keys())
    max_lengths = {i: 0 for i in keys}
    accounts.insert(0, {i: i for i in keys})
    for account in accounts:
        for e in account:
            max_lengths[e] = max(max_lengths[e], len(str(account[e])))

    print(f"|{'|'.join(['-' * i for i in max_lengths.values()])}|")
    for account in accounts:
        print(f"|{'|'.join([str(account[e]).center(max_lengths[e]) for e in keys])}|")
        print(f"|{'|'.join(['-' * i for i in max_lengths.values()])}|")


async def exit_program():
    await db.pop_bind().close()
    exit(0)


actions = {1: add_account, 2: remove_account, 3: list_accounts, 4: exit_program}


async def generate_sessions():
    pass


async def manage_accounts():
    while 1:
        action = input(
            f"1) Добавить аккаунт\n"
            f"2) Удалить аккаунт\n"
            f"3) Посмотреть аккаунты\n"
            f"4) Выход\n"
        )

        try:
            action = int(action)
            if action not in range(1, 4 + 1):
                raise ValueError("action not in range 1..4")
        except ValueError:
            print("Неверный ввод. Попробуйте ещё раз")
            continue

        await actions[action]()
