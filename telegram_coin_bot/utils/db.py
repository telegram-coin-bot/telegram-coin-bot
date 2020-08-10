from telegram_coin_bot.db.schema import db, Session, Money


def create_tables():
    with db:
        db.create_tables([Session, Money])
