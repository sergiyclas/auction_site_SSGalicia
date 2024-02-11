from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.secret_key = 'some secret motivation...it is unreal to work by one person'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basadate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login_page'  # Установлення маршруту для авторизації
login_manager.login_message = "Авторизуйтесь для входу на цю сторінку"
login_manager.init_app(app)

from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
