from telegram_coin_bot.utils.config import Config


def main():
    print("Оставьте поле пустым, если не хотите менять значение")
    print("Имя параметра - описание (текущее значение)")
    for c in Config.get_units():
        if not c.description:
            continue
        new_val = input(f"{c.section}/{c.name} - {c.description} ({c.value}): ")
        if not new_val:
            continue
        Config.set(c.section, c.name, new_val)
    Config.save()
