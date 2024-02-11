import sqlite3

from flask import render_template, redirect, request, url_for, flash, make_response
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Lot, User
from app import app, login_manager
from UserLogin import UserLogin


def upload_date():
    lots = Lot.query.filter_by(status='Active').all()
    now = datetime.now()

    for lot in lots:
        if now - lot.date >= timedelta(days=7):
            lot.status = 'Inactive'

    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + "?next=" + request.url)
    return response


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/posts', methods= ['POST', 'GET'])
def posts():
    upload_date()

    order_ = 'date'
    sort_ = 'desc'
    status_ = 'Active'
    if request.method == 'POST':
        order_ = request.form['order']
        sort_ = request.form['sort']
        status_ = request.form['status']

    if order_ == 'date' and sort_ == 'desc':
        lots = Lot.query.filter_by(status=status_).order_by(Lot.date.desc()).all()
    elif order_ == 'title' and sort_ == 'desc':
        lots = Lot.query.filter_by(status=status_).order_by(Lot.name.desc()).all()
    elif order_ == 'min_val' and sort_ == 'desc':
        lots = Lot.query.filter_by(status=status_).order_by(Lot.min_val.desc()).all()
    elif order_ == 'title' and sort_ == 'asc':
        lots = Lot.query.filter_by(status=status_).order_by(Lot.title.asc()).all()
    elif order_ == 'min_val' and sort_ == 'asc':
        lots = Lot.query.filter_by(status=status_).order_by(Lot.min_val.asc()).all()
    else:
        lots = Lot.query.filter_by(status=status_).order_by(Lot.date.asc()).all()
    return render_template('posts.html', lots=lots)


@app.route('/posts/<int:id>')
def post_detail(id):
    upload_date()
    lot = Lot.query.get(id)
    user = User.query.get(lot.current_owner_id)
    return render_template("post_detail.html", lot=lot, user=user)


@app.route('/posts/<int:id>/del')
@login_required
def post_delete(id):
    upload_date()
    lot = Lot.query.get_or_404(id)

    try:
        db.session.delete(lot)
        db.session.commit()
        return redirect('/posts')
    except:
        return "Щось пішло не так під час видалення"


@app.route('/profile/<int:id>/lots')
@login_required
def user_lots(id):
    upload_date()
    lots = Lot.query.filter_by(owner_id=current_user.id).order_by(Lot.date.desc()).all()
    return render_template('user_lots.html', lots=lots)


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
@login_required
def post_update(id):
    upload_date()
    lot = Lot.query.get(id)
    user = User.query.get(lot.current_owner_id)
    if request.method == "POST":
        Lot.title = request.form['title']
        Lot.descr = request.form['descr']
        Lot.min_val = request.form['min_val']

        try:
            db.session.commit()
            return redirect('/posts')
        except SQLAlchemyError as e:
            # db.session.rollback()  # Виконуємо відкат змін, якщо виникла помилка
            # error = str(e)
            # return f'Помилка: {error}'
            return 'Щось пішло не так при редагуванні лоту'
    else:
        return render_template('post_update.html', lot=lot, user=user)


@app.route('/create_lots', methods=['POST', 'GET'])
@login_required
def create_lots():
    upload_date()
    print(request.method)
    if request.method == "POST":
        if current_user.name is None:
            flash("Ви не заповнили поле ім'я")
            return redirect(url_for('profile'))

        title = request.form['title']
        print(title)
        descr = request.form['descr']
        print(descr)
        min_val = request.form['min_val']
        print(min_val)
        file = request.files['file']
        print(file)
        owner_id = current_user.id
        print(owner_id)
        ext = file.filename.rsplit('.', 1)[1]
        png_ = False

        if ext == 'png' or ext == 'PNG':
            png = True
        if file and ext:
            try:
                img = file.read()
                binary = sqlite3.Binary(img)
            except sqlite3 as e:
                flash("Помилка відкриття, можливо файл пошкоджено")
        else:
            return redirect(url_for('/create_lot'))

        lot = Lot(title=title, descr=descr, min_val=min_val, photo=binary, owner_id=owner_id)
        try:
            db.session.add(lot)
            db.session.commit()
            return redirect('/posts')
        except SQLAlchemyError as e:
            db.session.rollback()  # Виконуємо відкат змін, якщо виникла помилка
            error = str(e)
            return f'Помилка: {error}'
            return 'Щось пішло не так'
    else:
        return render_template('create_lots.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    email = request.form.get('email')
    password = request.form.get('password')
    print(email, password)

    if email and password:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            redirect(next_page)
        else:
            flash('Пошта або пароль не вірні')
    else:
        flash('Будь ласка, заповніть всі поля')
    url_parts = request.url.split('?next=/')
    # return url_parts[1]
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Паролі не сходяться')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(email=email, password=hash_pwd)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Ви успішно зареєструвалися')
                return redirect(url_for('login_page'))
            except Exception as e:
                flash('Щось пішло не так...')

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    upload_date()
    if request.method == 'POST':
        print("RUN POST")
        name = request.form.get('name')
        surname = request.form.get('surname')
        phone = request.form.get('phone')
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        name_res = True
        surname_res = True
        phone_res = True
        if current_user.name is None and name is None:
            flash('Ви не заповнили поле імені')
        if current_user.surname is None and surname is None:
            flash('Ви не заповнили поле прізвища')
        if current_user.phone is None and phone is None:
            flash('Ви не заповнили поле телефону')

        if name_res and surname_res and phone_res:
            try:
                current_user.name = name
                current_user.surname = surname
                current_user.phone = phone
                db.session.commit()
            except sqlite3 as e:
                flash('Щось пішло не так під час додавання інформації')

            if password is not None and new_password is not None:

                if not check_password_hash(current_user.password, password):
                    flash('Ви ввели невірний пароль')
                else:
                    hash_pwd = generate_password_hash(new_password)
                    try:
                        current_user.password = hash_pwd
                        db.session.commit()
                        flash('Ви успішно змінили пароль')
                        return redirect(url_for('profile'))

                    except Exception as e:
                        flash('Щось пішло не так під час зміни паролю...')

    return render_template('profile.html')


@app.route('/avatar')
@login_required
def avatar():
    print('Пішло')
    upload_date()
    img = None
    if not current_user.avatar:
        try:
            with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), 'rb') as f:

                img = f.read()
        except FileNotFoundError as e:
            print('Не найдено аватарки за замовчуванням: ' + str(e))

    else:
        img = current_user.avatar

    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    upload_date()
    if request.method == 'POST':
        file = request.files['file']
        ext = file.filename.rsplit('.', 1)[1]
        png_ = False

        if ext == 'png' or ext == 'PNG':
            png = True

        if file and ext:
            try:
                img = file.read()
                try:
                    binary = sqlite3.Binary(img)
                    current_user.avatar = binary
                    db.session.commit()

                except sqlite3.Error as e:
                    flash("Помилка оновлення аватарки в БД" + str(e))

                if not current_user.avatar:
                    flash('Помилка оновлення аватарки')

                flash("Аватар оновлений")
            except FileNotFoundError as e:
                flash('Помилка читання файлу')
        else:
            flash('Помилка оновлення аватару')

    return redirect(url_for('profile'))
