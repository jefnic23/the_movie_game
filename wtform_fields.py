from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, ValidationError, Email
from models import *


class RegistrationForm(FlaskForm):
    username = StringField('Username', 
        validators=[InputRequired(message="Username required"), 
        Length(min=4, max=25, message="Username must be between 4 and 25 characters")],
        render_kw={'autofocus': True})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[InputRequired(message="Password required"), 
        Length(min=8, message="Password must be at least 8 characters")])
    confirm_pswd = PasswordField('Confirm password',
        validators=[InputRequired(message="Password required"), 
        EqualTo("password", message="Passwords must match")])
    submit_button = SubmitField("Register")

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists.")

    def validate_email(self, email):
        user_object = User.query.filter_by(email=email.data).first()
        if user_object:
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(message="Username required")], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[InputRequired(message="Password required")])
    remember_me = BooleanField('Remember me')
    submit_button = SubmitField('Login')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Enter your email", validators=[DataRequired(), Email()], render_kw={'autofocus': True})
    submit_button = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password',
        validators=[InputRequired(message="Password required"), 
        Length(min=8, message="Password must be at least 8 characters")], 
        render_kw={'autofocus': True})
    confirm_pswd = PasswordField('Confirm new password',
        validators=[InputRequired(message="Password required"), 
        EqualTo("password", message="Passwords must match")])
    submit_button = SubmitField("Submit new password")


class CreateRoomForm(FlaskForm):
    roomname = StringField('Create a name for your room', validators=[InputRequired(message="Room name required")], render_kw={'autofocus': True})
    password = PasswordField("Enter a password if you'd like your room to be private")
    submit_button = SubmitField('Create room')

    def validate_roomname(self, roomname):
        room_object = GameRoom.query.filter_by(roomname=roomname.data).first()
        if room_object:
            raise ValidationError("Room name already exists.")


class JoinRoomForm(FlaskForm):
    roomname = StringField('Enter the name of the room you want to join', validators=[InputRequired(message="Room name required")], render_kw={'autofocus': True})
    password = PasswordField("Enter the room's password, if applicable")
    submit_button = SubmitField('Join room')

    def validate_roomname(self, roomname):
        from flask_login import current_user
        room_object = GameRoom.query.filter_by(roomname=roomname.data).first()
        if not room_object:
            raise ValidationError("Room name does not exist.")  
        else:
            room = Room.query.filter_by(roomname=roomname.data, player=current_user.id).first()
            if room:
                raise ValidationError("You are already in this game.")

    def incorrect_password(self, password):
        roomname = self.roomname.data
        room_object = GameRoom.query.filter_by(roomname=roomname).first()
        if room_object:
            if room_object.password and password != room_object.password:
                raise ValidationError("Incorrect password.")