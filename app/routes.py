from flask import render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from wtform_fields import *
from models import *
from email import send_password_reset_email
from app import app

login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        email = reg_form.email.data

        hashed_pswd = pbkdf2_sha256.hash(password)

        user = User(username=username, password=hashed_pswd, email=email)
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=reg_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object, remember=login_form.remember_me.data)
        if current_user.is_authenticated:
            return redirect(url_for('game'))

    return render_template("login.html", form=login_form)

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    logout_user()
    flash("You have logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for instructions on how to reset your password")
        return redirect(url_for('login'))
    return render_template("reset_password_request.html", form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        password = form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        User(password=hashed_pswd)
        db.session.commit()
        flash('Your password has been reset')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/game', methods=['GET', 'POST'])
def game():
    if not current_user.is_authenticated:
        flash("Please login.", "danger")
        return redirect(url_for('login'))
    return render_template('game.html')