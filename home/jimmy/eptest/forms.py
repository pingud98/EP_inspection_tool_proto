"""
WTForms definitions for authentication and inspection CRUD.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from config import Config

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

class InspectionForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=128)])
    description = TextAreaField("Description")
    remark_a = BooleanField("Remark A")
    remark_b = BooleanField("Remark B")
    remark_c = BooleanField("Remark C")
    photos = FileField("Photos", validators=[FileAllowed(list(Config.ALLOWED_EXTENSIONS), "Images only!")], render_kw={"multiple": True})
    submit = SubmitField("Save")

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    confirm_new = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Change Password")
