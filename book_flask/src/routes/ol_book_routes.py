from flask import Blueprint, request, jsonify

from services.ol_book_service import search_books

ol_book_bp = Blueprint("ol_book", __name__)


@ol_book_bp.route("/ol-search")
def ol_search():
    title = request.args.get("title", None)
    author = request.args.get("author", None)
    q = request.args.get("q", None)
    books = search_books(title, author, q, 20)
    output = [book.to_dict() for book in books]
    return output