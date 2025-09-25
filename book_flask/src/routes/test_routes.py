from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from models.user import User
from services.book_service import test_data, update_book_user, get_books_by_user_id
from services.db import db

test_bp = Blueprint('test', __name__)

@test_bp.route("/drop", methods=["POST"])
def drop():
    data = request.get_json()
    item = data.get("item")
    target = data.get("target")
    # Do something server-side (log, DB update, etc.)
    print(f"Item dropped: {item} onto {target}")
    return jsonify({"status": "ok", "message": f"{item} dropped on {target}"})

@test_bp.route("/test-card")
def get_test_card():
    v_book = get_books_by_user_id(1)[0:10]
    return render_template('content/test_grid.html', books=v_book)

