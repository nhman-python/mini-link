import random
import string
from functools import wraps

from flask import session, flash, redirect, url_for
from dataclasses import dataclass
from module import db, ShortLink, Users
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class ShortInfo:
    pass


class UserExist(Exception):
    pass


class UserManager:
    @staticmethod
    def _commit_user():
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def random_password():
        cher = string.ascii_letters + string.digits
        password = ''.join(random.choice(cher) for _ in range(12))
        return password

    @staticmethod
    def get_user_info(username: str):
        u_info = Users.query.filter_by(username=username).first()
        return u_info

    @staticmethod
    def create_user(username: str, password: str, email: str) -> bool:
        if UserManager.exist_username_email(username, email):
            raise UserExist('user exist try different username or email')
        user = Users(username=username, password=generate_password_hash(password), email=email)
        db.session.add(user)
        return UserManager._commit_user()

    @staticmethod
    def user_auth(username: str, password: str):
        user = Users.query.filter_by(username=username).first()
        if user:
            password_hash = user.password
            return check_password_hash(password_hash, password)
        return False

    @staticmethod
    def update_password(username: str, password: str, new_password):
        user = Users.query.filter_by(username=username).first()
        if user:
            password_hash = user.password
            if check_password_hash(password_hash, password):
                user.password = generate_password_hash(new_password)
                return UserManager._commit_user()
        return False

    @staticmethod
    def exist_username_email(username: str, email: str):
        user = Users.query.filter((Users.username == username) | (Users.email == email)).first()
        return user is not None

    @staticmethod
    def login_required(view_func):
        @wraps(view_func)
        def validation(*args, **kwargs):
            check = False
            if not session.get('user'):
                check = True
            if not session.get('id'):
                check = True

            if check:
                flash('you need to login to see this page', 'danger')
                return redirect(url_for('login'))
            return view_func(*args, **kwargs)

        return validation


class ShortManager:
    @staticmethod
    def _commit_short():
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def create_short(endpoints, user_id: str, redirect_url: str, length=4):
        random_cher = ShortManager.random_letters(length, endpoints)
        new_link = ShortLink(internal_url=random_cher,
                             redirect_url=redirect_url,
                             published=user_id, view=0)
        db.session.add(new_link)
        ShortManager._commit_short()
        return f'/{random_cher}'

    @staticmethod
    def custom_short(user_id, custom_short, redirect_url):
        if ShortManager.redirect_exist(custom_short):
            return False
        new_link = ShortLink(internal_url=custom_short,
                             redirect_url=redirect_url,
                             published=user_id, view=0)
        db.session.add(new_link)
        ShortManager._commit_short()
        return f'/{custom_short}'

    @staticmethod
    def redirect_exist(internal_url):
        check = ShortLink.query.filter_by(internal_url=internal_url).first()
        return bool(check)

    @staticmethod
    def random_letters(length, endpoints):
        letters = string.ascii_letters
        max_attempts = 10
        for _ in range(max_attempts):
            gen = ''.join(random.choice(letters) for _ in range(length))
            if not ShortManager.redirect_exist(gen) and gen not in endpoints:
                return gen
        raise Exception("Failed to generate a unique random string")

    @staticmethod
    def get_url_redirect(internal_url):
        external_link = ShortLink.query.filter_by(internal_url=internal_url).first()
        return external_link.redirect_url if external_link else None

    @staticmethod
    def patch_all_links(user_id):
        short_obj = ShortLink.query.filter_by(published=user_id).all()
        return short_obj

    @staticmethod
    def increment_view(internal_url):
        short = ShortLink.query.filter_by(internal_url=internal_url).first()

        if short:
            short.view += 1
            return ShortManager._commit_short()
        return False

    @staticmethod
    def update_external_link(new_link, internal_url, published_id):
        update = ShortLink.query.filter_by(internal_url=internal_url, published=published_id).first()
        update.redirect_url = new_link
        return ShortManager._commit_short()

    @staticmethod
    def delete_link(internal_url, published_id):
        delete = ShortLink.query.filter_by(internal_url=internal_url, published=published_id).first()
        if delete:
            db.session.delete(delete)
            return ShortManager._commit_short()
        return False
