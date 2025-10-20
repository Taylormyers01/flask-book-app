from crypt import methods

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user

from logger import logger
from models.constants import BookStatus
from services.auth_service import refresh_user
from services.book_service import (
    update_user_book,
    get_books_by_query,
    generate_book_from_g_data,
    get_shelf_books,
)
from services.db import db


book_bp = Blueprint("book", __name__)


@book_bp.route("/my-archives")
@login_required
def my_archives():
    refresh_user(current_user)
    all_books = [ub for ub in current_user.user_books]
    return render_template(
        "parent/my-archives.html",
        all_books=[ub.book for ub in all_books],
        owned_books=[ub.book for ub in all_books if ub.owned == True],
        want_to_read=[
            wtr.book for wtr in all_books if wtr.status == BookStatus.WANT_TO_READ
        ],
        read_books=[read.book for read in all_books if read.status == BookStatus.READ],
        next=url_for("book.my_archives"),
    )


@book_bp.route("/search-catalog")
def search_catalog():
    """
    Search catalog HTML -> javascript handles updating search results
    """
    return render_template(
        "parent/catalog-search.html", books=[], next=url_for("book.search_catalog")
    )


@book_bp.route("/update-catalog")
def update_catalog():
    """
    Renders book-grid with results from query
    """
    query = request.args.get("q", "").lower()
    template_books = []
    if query:
        books = get_books_by_query(query)
        for book in books["items"]:
            template_books.append(generate_book_from_g_data(book))
    return render_template("layout/book-grid.html", books=template_books)


@book_bp.route("/my-shelf")
@login_required
def my_shelf():
    shelf_books = get_shelf_books(current_user)
    return render_template("parent/my-shelf.html", books=shelf_books)


@login_required
@book_bp.route("/update-bookshelf-order", methods=["POST"])
def update_bookshelf_order():
    data = request.get_json()
    g_id = data.get("g_id")
    position = data.get("position")
    optional_book = current_user.get_user_book(g_id)
    assigned_book = current_user.get_book_by_position(position)
    if assigned_book is not None:
        logger.info(f"Position already assigned, ", assigned_book.to_dict())
        return jsonify(success=False, body=f"Position already assigned"), 400
    if optional_book:
        optional_book.shelf_pos = position
    else:
        logger.info(f"No book found for {g_id}")
        return jsonify(body=f"No book found for {g_id}"), 400
    db.session.commit()
    logger.info("Saved Successfully")
    return jsonify(success=True, g_id=g_id, position=position), 200


@login_required
@book_bp.route("/update-book", methods=["POST"])
def update_book():
    logger.info(f"Form data: {request.form}")
    if request.method == "POST" and current_user.is_authenticated:
        logger.info(request.form)
        g_id = request.form.get("g_id", None)
        status = request.form.get("status", None)
        owned = request.form.get("owned", False)
        outcome = update_user_book(g_id, current_user, status, owned)
        success = outcome[1] == 200
        return jsonify(success=success, g_id=g_id)
