from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, URLField, IntegerField
from wtforms.validators import InputRequired, Length, EqualTo, URL, NumberRange, email, Email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message='Username is required.'),
        Length(min=6, max=20, message='Username must be between 6 and 20s characters.')
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message='Password is required.'),
        Length(min=8, max=100, message='Password must be between 8 and 100 characters.')
    ])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message='Username is required.'),
        Length(min=6, max=20, message='Username must be between 6 and 20 characters.')
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message='Password is required.'),
        Length(min=8, max=100, message='Password must be between 8 and 100 characters.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    email = StringField('Email', validators=[
        InputRequired(message='Email is required.'),
        Email(message='Invalid email address.')
    ])
    submit = SubmitField('Register')


class CustomLinkForm(FlaskForm):
    custom_link = StringField('Custom Link', validators=[
        InputRequired(message='Custom link is required.'),
        Length(min=3, max=20, message='Custom link must be between 3 and 20 characters.')
    ])
    redirect_url = URLField('Redirect URL', validators=[
        InputRequired(message='Redirect URL is required.'),
        Length(min=8, max=200, message='Redirect URL must be between 8 and 200 characters.'),
        URL(message='Invalid URL format. Please enter a valid URL.')
    ])
    submit = SubmitField('Create Link')


class Index(FlaskForm):
    pass


class RandomLink(FlaskForm):
    redirect_url = URLField('Redirect URL', validators=[
        InputRequired(message='Redirect URL is required.'),
        Length(min=8, max=200, message='Redirect URL must be between 8 and 200 characters.'),
        URL(message='Invalid URL format. Please enter a valid URL.')
    ])
    length = IntegerField('Link Length', validators=[
        NumberRange(min=4, max=20, message='Link length must be between 4 and 20 characters.'),
        InputRequired(message='Link length is required.')
    ])
    password_protect = PasswordField('set-password', validators=[
        Length(min=0, max=30, message='please select password between 4 to 32 characters')])
    submit = SubmitField('Generate Link')


class ChangePassword(FlaskForm):
    current_password = PasswordField('Current Password', validators=[InputRequired(), Length(min=6, max=70)])
    new_password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=70)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Change password')
