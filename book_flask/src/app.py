import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from logger import logger
from dotenv import load_dotenv

from models.constants import BookStatus
from routes.test_routes import test_bp
from services.book_service import test_data
from services.db import db
from services import user_service
from models.user import User
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from utils import seed
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

@app.route("/")
def default():
    return redirect(url_for('home'))

@app.context_processor
def inject_enums():
    return dict(BookStatus=BookStatus)

@app.route('/home/')
def home(name=None):
    if current_user.is_authenticated:
        return render_template('parent/home.html',
                               total_books=10, authors=[' ',' '], read_books=[' ',' '], recent_books=test_data()[:4])
    return render_template('parent/home.html',
                           total_books=0, authors=[], read_books=[], recent_books=[])

@app.route('/book')
def book():
    return render_template('parent/catalog-search.html', books=[{"name": "book1"}, {"name": "book2"}, {"name": "book3"}])

# @app.route('/add_user', methods=['POST'])
# def add_user():
#     name = request.json.get('name')
#     logger.info(f'Received request to add user: {name}')
#     output = user_service.add_user(name=name)
#     return output

@app.route('/users', methods=['GET'])
@app.route('/users/<name>', methods=['GET'])
def list_users(name=None):
    return user_service.get_user_by_name(name=name)

def run_flask():
    app.run(port=5000, debug=True, use_reloader=True)

if __name__ == '__main__':
    dotenv_path = os.path.join(basedir, 'dev.env')
    print(f"Loading environment variables from {dotenv_path}")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    with app.app_context():
        logger.info('Creating DB')
        db.create_all()
        seed = Seeder(db)
        seed.seed()
    logger.info('DB created successfully')
    run_flask()
    
