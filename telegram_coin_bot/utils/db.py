from telegram_coin_bot.db.schema import Money, Session, db


def create_tables():
    with db:
        db.create_tables([Session, Money])
