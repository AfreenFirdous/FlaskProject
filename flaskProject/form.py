from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, InputRequired


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])


class UserForm(FlaskForm):
    username = StringField('UserName', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
