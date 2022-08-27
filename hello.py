from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user=name)

@app.errorhandler(404)
def error(e):
    return render_template('404.html'), 404