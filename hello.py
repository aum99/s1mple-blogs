from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is a secret key'

class UserForm(FlaskForm):
    name = StringField("WHATS YOUR NAME??", validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user=name)


@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404


@app.route('/name', methods=['GET', 'POST'])
def user_form():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data.title()
        form.name.data = ''
    return render_template('name.html', name=name, form=form)