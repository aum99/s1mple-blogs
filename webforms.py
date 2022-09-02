from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField
from wtforms import TextAreaField
from flask_wtf.file import FileField


class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("NAME:", validators=[DataRequired()])
    username = StringField("USERNAME:", validators=[DataRequired()])
    email = StringField("EMAIL:", validators=[DataRequired()])
    fav_color = StringField("FAVOURITE COLOR:")
    about_author = TextAreaField("About author")
    password_hash = PasswordField("PASSWORD:", validators=[DataRequired(), EqualTo('password_hash2', message='Password must match')])
    password_hash2 = PasswordField("CONFIRM PASSWORD:", validators=[DataRequired()])
    profile_picture = FileField("PROFILE PIC:")
    submit = SubmitField('Submit')


class NamerForm(FlaskForm):
    name = StringField("WHATS YOUR NAME??", validators=[DataRequired()])
    submit = SubmitField('Submit')


class PasswordForm(FlaskForm):
    email = StringField("WHATS YOUR EMAIL?", validators=[DataRequired()])
    password_hash = PasswordField("WHATS YOUR PASSWORD?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")