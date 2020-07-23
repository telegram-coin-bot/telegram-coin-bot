from gino import Gino

db = Gino()


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer(), primary_key=True)
    phone = db.Column(db.String(), unique=True)
    password = db.Column(db.String())


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer(), primary_key=True)
    phone = db.Column(db.String(), unique=True)
    session_string = db.Column(db.String())
