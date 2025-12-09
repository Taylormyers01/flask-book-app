import os
from pathlib import Path

from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_cors import CORS
from flask_login import LoginManager, current_user
from platformdirs import user_data_dir
from dotenv import load_dotenv

from logger import logger
from models.constants import BookStatus
from routes.ol_book_routes import ol_book_bp
from routes.test_routes import test_bp
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp
from services.db import db
from services.ol_book_service import gen_home_stats
from models.user import User
from utils.seed import Seeder

APP_NAME = "Book-Flask"
APP_AUTHOR = "TM"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, "resources", "dev.env")

# Load .env
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    logger.info(f"Environment variables loaded from: {ENV_PATH}")
else:
    load_dotenv()
    logger.info("Environment variables loaded from default .env (if present).")

# Initialize flask
app = Flask(__name__)
bootstrap = Bootstrap5(app)
CORS(app)
logger.info("Flask app starting...")

# DB Setup
data_dir = Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR))
data_dir.mkdir(parents=True, exist_ok=True)
sqlite_path = data_dir / "database.db"

# Load DB connection string (SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{sqlite_path}")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-default-key")

logger.info(f"Using database: {DATABASE_URL}")

app.config.update(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=DATABASE_URL,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(app)

# Flask Login setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(test_bp)
app.register_blueprint(user_bp)
app.register_blueprint(ol_book_bp)


@app.route("/")
def default():
    return redirect(url_for("home"))

@app.context_processor
def inject_enums():
    return dict(BookStatus=BookStatus)

@app.route("/home/")
def home():
    if current_user.is_authenticated:
        all_books, authors, read_books = gen_home_stats(current_user)
        return render_template(
            "parent/home.html",
            total_books=len(all_books),
            authors=len(authors),
            read_books=len(read_books),
            recent_books=all_books[:4] if all_books else []
        )

    return render_template(
        "parent/home.html",
        total_books=0,
        authors=0,
        read_books=0,
        recent_books=[]
    )

def run_flask():
    logger.info("App served on port 5000")
    # serve(app, host="0.0.0.0", port=5000)
    app.debug = True
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    with app.app_context():
        logger.info("Creating database and seeding if needed...")
        db.create_all()
        seed = Seeder(db)
        seed.seed()
        logger.info("Database initialized.")

    run_flask()
