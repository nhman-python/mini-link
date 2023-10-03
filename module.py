from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


def get_israel_datetime():
    tz = pytz.timezone('Asia/Jerusalem')
    return datetime.now(tz=tz).strftime('%Y-%m-%d %H:%M:%S')


db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    permission = db.Column(db.Integer, default=0)
    create_at = db.Column(db.String(20), default=get_israel_datetime)

    def __repr__(self):
        return f"<Users(username='{self.username}')>"


class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    internal_url = db.Column(db.String(20), unique=True, nullable=False)
    redirect_url = db.Column(db.String, nullable=False)
    published = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.String(20), default=get_israel_datetime)
    view = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<ShortLink(internal_url='{self.internal_url}')>"

