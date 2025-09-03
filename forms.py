from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    SelectField,
)

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp, Optional, DataRequired
import email_validator
from flask_login import current_user
from wtforms import ValidationError, validators
from models import User


class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    # Placeholder labels to enable form rendering
    username = StringField(
        validators=[Optional()]
    )


class register_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("pwd", message="Passwords must match !"),
        ]
    )
    first_name = StringField(validators=[Optional(), Length(1, 50)])
    last_name = StringField(validators=[Optional(), Length(1, 50)])
    phone = StringField(validators=[Optional(), Length(10, 20)])

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered!")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already taken!")


class profile_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    first_name = StringField(validators=[Optional(), Length(1, 50)])
    last_name = StringField(validators=[Optional(), Length(1, 50)])
    phone = StringField(validators=[Optional(), Length(10, 20)])

    def validate_email(self, email):
        if current_user.email != email.data:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError("Email already registered!")

    def validate_username(self, username):
        if current_user.username != username.data:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError("Username already taken!")


class change_password_form(FlaskForm):
    current_pwd = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    new_pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    confirm_pwd = PasswordField(
        validators=[
            InputRequired(),
            Length(8, 72),
            EqualTo("new_pwd", message="Passwords must match !"),
        ]
    )


class admin_user_form(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(3, 20, message="Please provide a valid name"),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores",
            ),
        ]
    )
    email = StringField(validators=[InputRequired(), Email(), Length(1, 64)])
    first_name = StringField(validators=[Optional(), Length(1, 50)])
    last_name = StringField(validators=[Optional(), Length(1, 50)])
    phone = StringField(validators=[Optional(), Length(10, 20)])
    is_admin = BooleanField('Administrator')
    is_active = BooleanField('Active', default=True)


class search_form(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    role = SelectField('Role', choices=[('all', 'All Users'), ('admin', 'Administrators'), ('user', 'Regular Users')], default='all')
    status = SelectField('Status', choices=[('all', 'All'), ('active', 'Active'), ('inactive', 'Inactive')], default='all')