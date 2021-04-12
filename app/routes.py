from flask import render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from wtform_fields import *
from models import *
from app import app

login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/register", methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_pswd = pbkdf2_sha256.hash(password)

        user = User(username=username, password=hashed_pswd)
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
    logout_user()
    flash("You have logged out successfully", "success")
    return redirect(url_for("login"))

@app.route('/game', methods=['GET', 'POST'])
def game():
    if not current_user.is_authenticated:
        flash("Please login.", "danger")
        return redirect(url_for('login'))
    return render_template('game.html')