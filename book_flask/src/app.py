import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_cors import CORS
from flask_login import LoginManager
from logger import logger
from services.db import db
from services import user_service
from models.user import user


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
bootstrap = Bootstrap5(app)
CORS(app)
logger.info("Flask app starting...")
logger.info(f"App root directory: {basedir}")

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@app.route("/")
def home():
    return redirect(url_for('hello'))

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', person=name)

@app.route('/book')
def book():
    return render_template('book.html', books=[{"name": "book1"},{"name": "book2"},{"name": "book3"}])

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.json.get('name')
    logger.info(f'Received request to add user: {name}')
    output = user_service.add_user(name=name)
    return output

@app.route('/users', methods=['GET'])
@app.route('/users/<name>', methods=['GET'])
def list_users(name=None):
    return user_service.get_user_by_name(name=name)


def run_flask():
    app.run(port=5000, debug=True, use_reloader=True)

if __name__ == '__main__':
    with app.app_context():
        logger.info('Creating DB')
        db.create_all()
    logger.info('DB created successfully')
    run_flask()
    # threading.Thread(target=run_flask).start()