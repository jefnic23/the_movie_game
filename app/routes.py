from flask import render_template, redirect, url_for, flash, session
from flask_session import Session
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from sqlalchemy.orm.session import SessionTransaction
from wtform_fields import *
from models import *
from app.email import send_password_reset_email
from app import app

Session(app)
bootstrap = Bootstrap(app)
socketio = SocketIO(app)
login = LoginManager(app)
login.init_app(app)

# instantiate game class
game = Game()

#####

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
        flash('Registered successfully, please login', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=reg_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        db.session.commit()
        if not user_object or not user_object.check_password(login_form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user_object, remember=login_form.remember_me.data)
        flash('Login successful', 'success')
        return redirect(url_for('profile', username=current_user.username))
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
        db.session.commit()
        if user:
            send_password_reset_email(user)
        flash("Check your email for instructions on how to reset your password", 'info')
        return redirect(url_for('login'))
    return render_template("reset_password_request.html", form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        user.set_password(hashed_pswd)
        db.session.commit()
        flash('Your password has been reset', "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    q = 'SELECT t1.roomname, t1.password, t1.status, t2.count FROM games t1 JOIN (SELECT a.roomname, COUNT(a.roomname) FROM rooms a GROUP BY a.roomname) t2 ON t1.roomname = t2.roomname'
    query = db.session.execute(q).fetchall()
    response = {'rows': [dict(row) for row in query]}
    db.session.commit()
    return render_template('lobby.html', rows=response['rows'])

@app.route('/profile/<username>')
def profile(username):
    if current_user.is_anonymous:
        flash("Please login to access your profile", "danger")
        return redirect(url_for('login'))
    rooms = Room.query.filter_by(player=current_user.id).all()
    db.session.commit()
    return render_template('profile.html', rooms=rooms)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.is_anonymous:
        flash("Please login to create a game", "danger")
        return redirect(url_for('login'))
    create_form = CreateRoomForm()
    if create_form.validate_on_submit():
        roomname = create_form.roomname.data
        password = create_form.password.data  
        game.add_player(current_user.username)
        gameroom = GameRoom(roomname=roomname, password=password, host=current_user.id)
        room = Room(roomname=roomname, player=current_user.id, room_id=gameroom.id)
        db.session.add_all([gameroom, room])
        db.session.commit()
        return redirect(url_for('room', room_id=gameroom.id))
    return render_template('create.html', form=create_form)

@app.route('/join', methods=['GET', 'POST'])
def join():
    if current_user.is_anonymous:
        flash("Please login to join a game", "danger")
        return redirect(url_for('login'))
    join_form = JoinRoomForm()
    if join_form.validate_on_submit():
        roomname = join_form.roomname.data
        gameroom = GameRoom.query.filter_by(roomname=roomname).first()
        room = Room(roomname=roomname, player=current_user.id, room_id=gameroom.id)
        game.add_player(current_user.username)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('room', room_id=gameroom.id))
    return render_template('join.html', form=join_form)

@app.route('/invite/<invitation>', methods=['GET', 'POST'])
def invite(invitation):
    if current_user.is_anonymous:
        flash("Please login to join a game", "danger")
        return redirect(url_for('login'))
    join_form = JoinRoomForm() 
    join_form.roomname.data = invitation
    if join_form.validate_on_submit():
        roomname = join_form.roomname.data
        gameroom = GameRoom.query.filter_by(roomname=roomname).first()
        room = Room(roomname=roomname, player=current_user.id, room_id=gameroom.id)
        game.add_player(current_user.username)
        db.session.add_all(room)
        db.session.commit()
        return redirect(url_for('room', room_id=gameroom.id))
    return render_template('join.html', form=join_form)

@app.route('/room/<room_id>', methods=['GET', 'POST'])
def room(room_id):
    if not current_user.is_authenticated:
        flash("Please login", "danger")
        return redirect(url_for('login'))
    else:
        room = GameRoom.query.filter_by(id=room_id).first()
        if room:
            present = Room.query.filter_by(roomname=room.roomname, player=current_user.id).first()
            db.session.commit()
            if present:
                return render_template('game.html', username=current_user.username, room=room.id)
            else:
                return redirect(url_for('invite', invitation=room.roomname))
        else:
            db.session.commit()
            flash("Please join or create a room", "danger")
            return redirect(url_for('lobby'))

# sockets

@socketio.on('join')
def on_join(data):
    username = data['username']
    join_room(data['room'])
    emit('joined', {'username': username, "players": [player.serialize() for player in game.players], "current_player": game.current_player.username, 'room': data['room']}, room=data['room'])

# write socket event "begin" that changes gameroom status to false

@socketio.on('search')
def on_search(data): 
    player = game.find_player(data['username'])
    guess = data['guess']
    if game.round_index == 0:
        game.add_to_round(guess)
    else:
        game.check_answer(guess, player)
    emit("answer", {"answer": guess, "player": player.username, "score": player.rollcall, "current_player": game.current_player.username, "round_index": game.round_index, 'round_over': game.round_over}, room=data['room'])

@socketio.on("veto")
def on_veto(data):
    game.veto_challenge(veto=True)
    emit("vetoed", {"current_player": game.current_player.username}, room=data['room'])

@socketio.on("challenge")
def on_veto(data):
    game.veto_challenge()
    emit("challenged", {"current_player": game.current_player.username, "round_index": game.round_index}, room=data['room'])

@socketio.on('noTime')
def no_time(data):
    player = game.find_player(data['current_player'])
    game.times_up(game.current_player)
    emit('times_up', {'player': player.username, "score": player.rollcall, "current_player": game.current_player.username}, room=data['room'])

@socketio.on('restart')
def on_restart():
    game.new_round()

if __name__ == '__main__':
    socketio.run(app, debug=True)