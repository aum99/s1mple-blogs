from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:aum150402@localhost/our_users'
app.config['SECRET_KEY'] = 'this is a secret key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    fav_color = db.Column(db.String(150))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name

class UserForm(FlaskForm):
    name = StringField("NAME:", validators=[DataRequired()])
    email = StringField("EMAIL:", validators=[DataRequired()])
    fav_color = StringField("FAVOURITE COLOR:")
    password_hash = PasswordField("PASSWORD:", validators=[DataRequired(), EqualTo('password_hash2', message='Password must match')])
    password_hash2 = PasswordField("CONFIRM PASSWORD:", validators=[DataRequired()])
    submit = SubmitField('Submit')


class NamerForm(FlaskForm):
    name = StringField("WHATS YOUR NAME??", validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/update/<int:id>', methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error! There was something wrong.... Please try again")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")

            user = Users(name=form.name.data, email=form.email.data, fav_color=form.fav_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.password_hash.data = ''
        flash("USER ADDED SUCCESSFULLY")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route('/delete/<int:id>')
def delete(id):
    name = None
    form = UserForm()
    name_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(name_to_delete)
        db.session.commit()
        flash("User Deleted successfully")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("There was a problem deleting this record... Please try again later!")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user=name)


@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404


class PasswordForm(FlaskForm):
    email = StringField("WHATS YOUR EMAIL?", validators=[DataRequired()])
    password_hash = PasswordField("WHATS YOUR PASSWORD?", validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # flash("FORM SUBMITTED SUCCESSFULLY")
        pw_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template('test_pw.html', email=email, password=password, form=form, pw_to_check=pw_to_check, passed=passed)

@app.route('/name', methods=['GET', 'POST'])
def user_form():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data.title()
        form.name.data = ''
        flash("FORM SUBMITTED SUCCESSFULLY")
    return render_template('name.html', name=name, form=form)