from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, ValidationError, Email
from passlib.hash import pbkdf2_sha256
from models import User

def invalid_credentials(form, field):
    username_entered = form.username.data
    password_entered = field.data

    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("Username or password is incorrect")

class RegistrationForm(FlaskForm):
    username = StringField('username_label', 
        validators=[InputRequired(message="Username required"), 
        Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    email = StringField('email_label', validators=[DataRequired(), Email()])
    password = PasswordField('password_label',
        validators=[InputRequired(message="Password required"), 
        Length(min=8, message="Password must be at least 8 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label',
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
            raise ValidationError("Account with this email already exists.")

class LoginForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired(message="Username required")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), invalid_credentials])
    remember_me = BooleanField('Remember me')
    submit_button = SubmitField('Login')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField("email_label", validators=[DataRequired(), Email()])
    submit_button = SubmitField("Request Password Reset")

class ResetPasswordForm(FlaskForm):
    password = PasswordField('password_label',
        validators=[InputRequired(message="Password required"), 
        Length(min=8, message="Password must be at least 8 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label',
        validators=[InputRequired(message="Password required"), 
        EqualTo("password", message="Passwords must match")])
    submit_button = SubmitField("Submit new password")

class CreateRoomForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired(message="Username required")])
    room_name = StringField('room_label', validators=[InputRequired(message="Room name required")])
    password = PasswordField('password_label')
    submit_button = SubmitField('Create room')