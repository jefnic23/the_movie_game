from flask import render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from wtform_fields import *
from models import *
from app.email import send_password_reset_email
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import json
from app import app

game = Game()
socketio = SocketIO(app)
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
        return redirect(url_for('lobby'))
    return render_template("login.html", form=login_form)

@app.route('/logout', methods=['GET'])
def logout():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    logout_user()
    flash("You have logged out successfully.", "success")
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
        flash("Check your email for instructions on how to reset your password.")
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
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/lobby', methods=['GET', 'POST'])
def lobby():
    q = 'SELECT t1.roomname, t1.password, t1.status, t2.count FROM games t1 JOIN (SELECT a.roomname, COUNT(a.roomname) FROM rooms a GROUP BY a.roomname) t2 ON t1.roomname = t2.roomname'
    rows = db.session.execute(q).fetchall()
    data = {'rows': [dict(row) for row in rows]}
    return render_template('lobby.html', data=data)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    create_form = CreateRoomForm()
    if create_form.validate_on_submit():
        roomname = create_form.roomname.data
        password = create_form.password.data
        # game = Game()
        game.add_player(current_user.username)
        gameroom = GameRoom(roomname=roomname, password=password, host=current_user.id, game=game.serialize())
        room = Room(roomname=roomname, player=current_user.id)
        db.session.add_all([gameroom, room])
        db.session.commit()
        # room_id = GameRoom.query.filter_by(roomname=roomname).first()
        return redirect(url_for('room', username=current_user.username, room=gameroom.id))
    return render_template('create.html', form=create_form)

@app.route('/join', methods=['GET', 'POST'])
def join():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    join_form = JoinRoomForm()
    if join_form.validate_on_submit():
        roomname = join_form.roomname.data
        room = Room(roomname=roomname, player=current_user.id)
        game.add_player(current_user.username)
        gameroom = GameRoom.query.filter_by(roomname=roomname).first()
        gameroom.update_game(game.serialize())
        db.session.add_all([gameroom, room])
        db.session.commit()
        # room_id = GameRoom.query.filter_by(roomname=roomname).first()
        return redirect(url_for('room', username=current_user.username, room=gameroom.id))
    return render_template('join.html', form=join_form)

@app.route('/room/<room>', methods=['GET', 'POST'])
def room(room):
    if not current_user.is_authenticated:
        flash("Please login.", "danger")
        return redirect(url_for('login'))
    else:
        room_id = GameRoom.query.filter_by(id=room).first()
        if room_id:
            present = Room.query.filter_by(roomname=room_id.roomname, player=current_user.id).first()
            if present:
                return render_template('game.html', username=current_user.username, room=room)
        else:
            flash("Please join or create a room.", "danger")
            return redirect(url_for('lobby'))

# sockets

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('joined', {'username': username, "players": game.players, "current_player": game.current_player, 'room': room}, room=room)

@socketio.on('search')
def on_search(data):
    player = data['username']
    guess = data['guess']
    room = data['room']
    if game.round_index == 0:
        game.add_to_round(guess)
    else:
        game.check_answer(guess, player)
    emit("answer", {"answer": guess, "round_over": game.round_over, "round_index": game.round_index, "current_player": game.current_player, "player": player, "score": game.scores[player].rollcall}, room=room)

@socketio.on("veto")
def on_veto(data):
    game.veto_challenge(veto=True)
    emit("vetoed", {"current_player": game.current_player}, room=data['room'])

@socketio.on("challenge")
def on_veto(data):
    game.veto_challenge()
    emit("challenged", {"current_player": game.current_player, "round_index": game.round_index}, room=data['room'])

@socketio.on('noTime')
def no_time(data):
    player = data['current_player']
    room = data['room']
    game.times_up(player)
    emit('times_up', {'player': player, "score": game.scores[player].rollcall, "current_player": game.current_player}, room=room)

@socketio.on('restart')
def on_restart():
    game.new_round()

if __name__ == '__main__':
    socketio.run(app, debug=True)