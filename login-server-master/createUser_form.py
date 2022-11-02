from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class CreateUserForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    repeatPassword = PasswordField('Repeat-Password')
    submit = SubmitField('Submit')