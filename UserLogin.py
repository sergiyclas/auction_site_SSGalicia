from flask import url_for
from flask_login import UserMixin


class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.getUSer(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else 'Без імені'

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"
