from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user

from logger import logger
from models.constants import BookStatus
from services.auth_service import refresh_user
from services.ol_book_service import search_books, update_user_ol_book, get_shelf_books


from services.db import db

ol_book_bp = Blueprint("ol_book", __name__)


@ol_book_bp.route("/ol-search")
def ol_search():
    title = request.args.get("title", None)
    author = request.args.get("author", None)
    q = request.args.get("q", None)
    books = search_books(title, author, q, 2)
    return render_template("layout/book-grid.html", books=books)


@login_required
@ol_book_bp.route("/update-ol-book", methods=["POST"])
def update_book():
    if request.method == "POST" and current_user.is_authenticated:
        data = request.get_json()
        # logger.info(f'OlBook Data: {data}')
        outcome = update_user_ol_book(current_user, data)
        return jsonify(success=True), 200


@ol_book_bp.route("/my-archives")
@login_required
def my_archives():
    refresh_user(current_user)
    all_books = [ub for ub in current_user.user_ol_books]
    return render_template(
        "parent/my-archives.html",
        all_books=[ub.ol_book for ub in all_books],
        owned_books=[ub.ol_book for ub in all_books if ub.owned == True],
        want_to_read=[
            wtr.ol_book for wtr in all_books if wtr.status == BookStatus.WANT_TO_READ
        ],
        read_books=[read.ol_book for read in all_books if read.status == BookStatus.READ],
        next=url_for("ol_book.my_archives"),
    )


@login_required
@ol_book_bp.route("/my-shelf")
def my_shelf():
    shelf_books = get_shelf_books(current_user)
    return render_template("parent/my-shelf.html", books=shelf_books)


@login_required
@ol_book_bp.route("/update-bookshelf-order", methods=["POST"])
def update_bookshelf_order():
    data = request.get_json()
    ol_id = data.get("ol_id")
    position = data.get("position")
    optional_book = current_user.get_user_ol_book(ol_id)
    assigned_book = current_user.get_ol_book_by_position(position)
    if assigned_book is not None:
        logger.info(f"Position already assigned, ", assigned_book.to_dict())
        return jsonify(success=False, body=f"Position already assigned"), 400
    if optional_book:
        optional_book.shelf_pos = position
    else:
        logger.info(f"No book found for {ol_id}")
        return jsonify(body=f"No book found for {ol_id}"), 400
    db.session.commit()
    logger.info("Saved Successfully")
    return jsonify(success=True, ol_id=ol_id, position=position), 200

@ol_book_bp.route("/search-catalog")
def search_catalog():
    """
    Search catalog HTML -> javascript handles updating search results
    """
    return render_template(
        "parent/catalog-search.html", books=[]
    )