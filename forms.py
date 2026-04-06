from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError, Email, Optional, Regexp
from flask_login import current_user
from models import User

class RegisterForm(FlaskForm):
    account_type = SelectField('Account Type', choices=[ # Account Type Selection
        ('actor', 'Actor'),
        ('company', 'Theater Company')
    ], validators=[InputRequired()])

    first_name = StringField(validators=[Length(max=50)
        ], render_kw={"placeholder": "First Name"})

    last_name = StringField(validators=[Length(max=50)
        ], render_kw={"placeholder": "Last Name"})
    
    company_name = StringField(validators=[Length( # Company Name Field (When account type is company)
        max=100)], render_kw={"placeholder": "Company Name"})

    email = StringField(validators=[InputRequired(), Email()], # Email Field
        render_kw={"placeholder": "Email"})

    username = StringField(validators=[InputRequired(), Length( # Username Field
        min=4, max=20), Regexp(r'^\S*$', message="No Spaces Allowed.")], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length( # Password Field
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register") # Submit Button

    def validate_first_name(self, first_name):
        if self.account_type.data == 'actor' and not first_name.data:
            raise ValidationError('First name is required for actors.')

    def validate_last_name(self, last_name):
        if self.account_type.data == 'actor' and not last_name.data:
            raise ValidationError('Last name is required for actors.')

    # Unique Email Validation
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "That email is already registered. Please use a different email.")

    # Unique Username Validation
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different username.")

# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length( # Username Field
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length( # Password Field
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login") # Submit Button

class EditActorProfileForm(FlaskForm):
    first_name = StringField(validators=[Length(max=50)
        ], render_kw={"placeholder": "First Name"})

    last_name = StringField(validators=[Length(max=50)
        ], render_kw={"placeholder": "Last Name"})
    
    bio = TextAreaField(validators=[
        ], render_kw={"placeholder": "Bio"})

    city = StringField(validators=[Optional(), Length(max=100)
        ], render_kw={"placeholder": "City"})

    state = StringField(validators=[Optional(), Length(max=2)
        ], render_kw={"placeholder": "State (e.g., MD)"})
    
    profile_photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    
    submit = SubmitField("Update Profile")
            
class EditCompanyProfileForm(FlaskForm):
    company_name = StringField(validators=[Length(max=100)
        ], render_kw={"placeholder": "Company Name"})

    bio = TextAreaField(validators=[Length(max=500)
        ], render_kw={"placeholder": "Bio"})

    city = StringField(validators=[Length(max=100)
        ], render_kw={"placeholder": "City"})

    state = StringField(validators=[Length(max=100)
        ], render_kw={"placeholder": "State"})

    website = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Website"})
    
    profile_photo = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

    submit = SubmitField("Update Profile")

class AccountSettingsForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()],
        render_kw={"placeholder": "Email"})

    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20), Regexp(r'^\S*$', message="No Spaces Allowed.")], render_kw={"placeholder": "Username"})

    submit = SubmitField("Update Account")

    # Unique Email Validation
    def validate_email(self, email):
        if email.data != current_user.email:
            existing_user_email = User.query.filter_by(
                email=email.data).first()
            if existing_user_email:
                raise ValidationError(
                    "That email is already registered. Please use a different email.")

    # Unique Username Validation
    def validate_username(self, username):
        if username.data != current_user.username:
            existing_user_username = User.query.filter_by(
                username=username.data).first()
            if existing_user_username:
                raise ValidationError(
                    "That username already exists. Please choose a different username.")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Current Password"})
    new_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "New Password"})
    confirm_password = PasswordField(validators=[InputRequired()],
        render_kw={"placeholder": "Confirm New Password"})
    submit = SubmitField("Reset Password")

    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('Passwords do not match.')

class ActorCreditForm(FlaskForm):
    show_name = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Show Name"})

    theater_name = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Theater Name"})

    role = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Role"})

    year = StringField(validators=[Length(max=4)
        ], render_kw={"placeholder": "Year (e.g., 2023)"})

    submit = SubmitField("Add Credit")

class DeleteCreditForm(FlaskForm):
    submit = SubmitField("Delete Credit")

class PastCompanyShowForm(FlaskForm):
    show_name = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Show Name"})

    year = StringField(validators=[Length(max=4)
        ], render_kw={"placeholder": "Year (e.g., 2023)"})

    description = TextAreaField(validators=[
        ], render_kw={"placeholder": "Description"})

    submit = SubmitField("Add Past Show")

class SearchForm(FlaskForm):
    search_query = StringField(validators=[Length(max=255)
        ], render_kw={"placeholder": "Search for actors or companies..."})

    submit = SubmitField("Search")