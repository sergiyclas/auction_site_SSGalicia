import math
import sqlite3
import time
from datetime import datetime
import re
from flask import url_for
from flask_login import UserMixin
from app import db
from UserLogin import UserLogin


class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    descr = db.Column(db.String(3000), nullable=False)
    min_val = db.Column(db.Integer, nullable=False)
    current_val = db.Column(db.Integer)
    photo = db.Column(db.BLOB)
    date = db.Column(db.DateTime, default=datetime.now())
    owner_id = db.Column(db.Integer)
    current_owner_id = db.Column(db.Integer)
    status = db.Column(db.String(10), default='Active')

    def __repr__(self):
        return '<Lot %r>' % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default=None)
    surname = db.Column(db.String(128), default=None)
    phone = db.Column(db.Integer, default=None)
    avatar = db.Column(db.BLOB)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
