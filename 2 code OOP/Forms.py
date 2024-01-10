from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Benutzername"}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "Passwort"}, validators=[DataRequired()])
    submit = SubmitField('Anmelden')

class RegisterForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Benutzername"}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "Passwort"}, validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Passwort bestätigen"}, validators=[DataRequired()])
    submit = SubmitField('Regestrieren')