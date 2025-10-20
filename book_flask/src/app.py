import os

from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_cors import CORS
from flask_login import LoginManager, current_user
from logger import logger
from dotenv import load_dotenv
from waitress import serve

from models.constants import BookStatus
from routes.test_routes import test_bp
from routes.user_routes import user_bp
from services.book_service import test_data, gen_home_stats
from services.db import db
from models.user import User
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from utils.seed import Seeder

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
bootstrap = Bootstrap5(app)
CORS(app)
logger.info("Flask app starting...")
logger.info(f"App root directory: {basedir}")

# Config
app.secret_key = "super-secret"  # Load from env in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(test_bp)
app.register_blueprint(user_bp)

@app.route("/")
def default():
    return redirect(url_for('home'))

@app.context_processor
def inject_enums():
    return dict(BookStatus=BookStatus)


@app.route('/home/')
def home():
    if current_user.is_authenticated:
        all_books, authors, read_books = gen_home_stats(current_user)
        return render_template('parent/home.html',
                               total_books=len(all_books), authors=len(authors), read_books=len(read_books), recent_books=test_data()[:4])
    return render_template('parent/home.html',
                           total_books=0, authors=0, read_books=0, recent_books=[])


def run_flask():
    logger.info('App served on port: %s', 5000)
    app.debug = True
    serve(app, host="0.0.0.0", port=5000)


if __name__ == '__main__':
    dotenv_path = os.path.join(basedir, 'dev.env')
    logger.info(f"Loading environment variables from {dotenv_path}")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logger.info("ENV Variables Loaded")
    with app.app_context():
        logger.info('Creating DB')
        db.create_all()
        seed = Seeder(db)
        seed.seed()
    logger.info('DB created successfully')
    run_flask()
    
