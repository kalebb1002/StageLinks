from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from models import User

class RegisterForm(FlaskForm):
    first_name = StringField(validators=[InputRequired(), Length(
        min=2, max=50)], render_kw={"placeholder": "First Name"})

    last_name = StringField(validators=[InputRequired(), Length(
        min=2, max=50)], render_kw={"placeholder": "Last Name"})

    email = StringField(validators=[InputRequired(), Email()], # Email Form
        render_kw={"placeholder": "Email"})

    username = StringField(validators=[InputRequired(), Length( # Username Form
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length( # Password Form
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    account_type = SelectField('Account Type', choices=[
        ('actor', 'Actor'),
        ('company', 'Theater Company')
    ], validators=[InputRequired()])

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "That email is already registered. Please use a different email.")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different username.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")