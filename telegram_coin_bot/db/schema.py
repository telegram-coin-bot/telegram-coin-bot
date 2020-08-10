from telegram_coin_bot.utils.config import PROJECT_PATH
import os
from peewee import Model, CharField, IntegerField, FloatField, SqliteDatabase
import enum

db = SqliteDatabase(os.path.join(PROJECT_PATH, "project.db"))


class BaseModel(Model):
    class Meta:
        database = db


class Session(BaseModel):
    id = IntegerField(primary_key=True)
    phone = CharField(unique=True)
    api_id = CharField()
    api_hash = CharField()
    session_string = CharField()


class Money(BaseModel):
    id = IntegerField(primary_key=True)
    type = IntegerField()
    amount = FloatField()


class MoneyType(enum.Enum):
    ADD = 0
    WITHDRAW = 1
