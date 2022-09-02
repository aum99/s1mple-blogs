from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, UserMixin, logout_user, current_user
from webforms import UserForm, LoginForm, NamerForm, PasswordForm, PostForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app = Flask(__name__)
ckeditor = CKEditor(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:aum150402@localhost/our_users'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ecvccjywwdquih:3e90377a721b78190de9196d66a61527e3fd8e59c3f87857' \
                                        '870e86fe71f22ead@ec2-54-152-28-9.compute-1.amazonaws.com:5432/d3083sbh16l0in'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yifjqswrviguky:0b3749151d82e1a0209d7ae06fbad73fdb9097b0903d1d932' \
                                        '59d5aefc89f9ab7@ec2-44-207-126-176.compute-1.amazonaws.com:5432/dbvm4qsrm6vhh9'
app.config['SECRET_KEY'] = 'this is a secret key'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = '/Users/aumravibattul/flasker/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(155))
    author = db.Column(db.String(155))
    slug = db.Column(db.String(155))
    content = db.Column(db.Text)
    post_added = db.Column(db.DateTime, default=datetime.utcnow())
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    fav_color = db.Column(db.String(150))
    about_author = db.Column(db.Text())
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(), nullable=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='poster')

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


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash("You have to be an Admin to access this page.....")
        return redirect(url_for('dashboard'))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!!Visit Again;)")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        this_user = Users.query.filter_by(username=form.username.data).first()
        if this_user:
            if check_password_hash(this_user.password_hash, form.password.data):
                login_user(this_user)
                flash('Loing Successfull')
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password... Try Again!!")
        else:
            flash("That user doesnt exits....:(")
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        if request.files['profile_picture']:
            name_to_update.profile_picture = request.files['profile_picture']
            pic_filename = secure_filename(name_to_update.profile_picture.filename)
            pic_name = str(uuid.uuid1()) + '_' + pic_filename
            saver = request.files['profile_picture']
            name_to_update.profile_picture = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User Updated Successfully!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
            except:
                flash("Error! There was something wrong.... Please try again")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)

    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)


@app.route('/update/<int:id>', methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']
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

            user = Users(username=form.username.data, name=form.name.data, email=form.email.data, fav_color=form.fav_color.data,
                         password_hash=hashed_pw, about_author=form.about_author.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.username.data = ''
        form.fav_color.data = ''
        form.password_hash.data = ''
        form.about_author.data = ''
        flash("USER ADDED SUCCESSFULLY")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        name_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(name_to_delete)
            db.session.commit()
            flash("User Deleted successfully")
            our_users = Users.query.order_by(Users.date_added)
            return render_template("add_user.html", form=form, name=name, our_users=our_users)
        except:
            flash("There was a problem deleting this record... Please try again later!")
    else:
        flash("Sorry, you cant delete that user....")
        return redirect(url_for('dashboard'))

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404


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


# ADD POST PAGE
@app.route('/add-post', methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, slug=form.slug.data, poster_id=poster, content=form.content.data)
        # CLEAR THE FORM
        form.title.data = ''
        form.slug.data = ''
        form.content.data = ''

        # ADD DATA TO DATABASE
        db.session.add(post)
        db.session.commit()

        # CREATE A FLASH
        flash("Blog Post Added Successfully")

    # REDIRECT TO THE PAGE
    return render_template("add_post.html", form=form)


@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.post_added)
    return render_template('posts.html', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=["GET", "POST"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    id = current_user.id
    if id == post.poster.id or id == 1:
        if form.validate_on_submit():
            post.title = form.title.data
            post.slug = form.slug.data
            post.content = form.content.data
            # COMMIT TO DB
            db.session.add(post)
            db.session.commit()
            # FLASH UPDATION
            flash("POST HAS BEEN UPDATED SUCCESSFULLY")
            return redirect(url_for('post', id=post.id))
    else:
        flash("This isn't your post so you cannot edit it")
        posts = Posts.query.order_by(Posts.post_added)
        return render_template("posts.html", posts=posts)

    form.title.data = post.title
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Post Deleted Successfully")

            posts = Posts.query.order_by(Posts.post_added)
            return render_template("posts.html", posts=posts)

        except:
            flash("Whoops there was something wrong. Please try again....")
            posts = Posts.query.order_by(Posts.post_added)
            return render_template("posts.html", posts=posts)
    else:
        flash("You arent authorized to delete that post...")
        posts = Posts.query.order_by(Posts.post_added)
        return render_template("posts.html", posts=posts)


@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template('search.html', form=form, posts=posts, searched=post.searched)
