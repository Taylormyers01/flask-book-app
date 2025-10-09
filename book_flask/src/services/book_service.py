import os
import requests
from sqlalchemy import or_

from logger import logger
from models.book import Book
from models.constants import BookStatus
from models.user import User
from services.db import db

G_API_KEY = os.environ.get('G_API_KEY')
BASE_URL = "https://www.googleapis.com/books/v1/volumes"
VALID_STATUS = [BookStatus.READ.value, BookStatus.WANT_TO_READ.value]

default_params = {
    "key": G_API_KEY,
    "maxResults": 40,
    "startIndex": 0,
    "printType": "BOOKS",
}


def get_books_by_query(query, params=None):
    """
    Get Google books by search string

    :param query: Search parameters
    :type query str
    :param params: Optional custom params
    :return: raw Google Book api response
    :rtype dict
    """
    if params is None:
        params = default_params
    params['q'] = query
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "No books found"


def get_google_book_data_by_id(gid, params=None):
    """
    :param gid: Google Book ID
    :param params: Optional custom params
    :return: Book
    """
    if params is None:
        params = default_params
    response = requests.get(BASE_URL + f'/{gid}', params=params)
    if response.status_code == 200:
        data = response.json()
        return generate_book_from_g_data(data)


def generate_book_from_g_data(g_data) -> Book:
    """
    Create book object from Google Book Api payload

    :param g_data:
    :return:
    :rtype Book
    """
    new_book = Book(
        title=g_data.get('volumeInfo', {}).get('title', 'Unknown Title'),
        g_id=g_data.get('id', 'Unknown ID'),
        author=', '.join(g_data.get('volumeInfo', {}).get('authors', ['Unknown Author'])),
        thumbnail=g_data.get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail', None),
        thumbnail_small=g_data.get('volumeInfo', {}).get('imageLinks', {}).get('smallThumbnail', None),
        short_description=g_data.get('searchInfo', {}).get('textSnippet'),
        description=g_data.get('volumeInfo', {}).get('description'),
        page_count=g_data.get('volumeInfo', {}).get('pageCount'),
        published_date=g_data.get('volumeInfo', {}).get('publishedDate'),
        categories=', '.join(g_data.get('volumeInfo', {}).get('categories', [])),
        info_link=g_data.get('volumeInfo', {}).get('infoLink'),
        preview_link=g_data.get('volumeInfo', {}).get('previewLink')
    )
    return new_book


# TODO remove
def test_data():
    g_data = get_books_by_query("Brandon Sanderson")
    books = [generate_book_from_g_data(data) for data in g_data.get('items', [])]
    if not books:
        return "No books found"
    return books


def get_books_by_user_id(user_id):
    """
    Get all books by user

    :param user_id: int
    :return: All books tied to user
    :rtype Book[]
    """
    books = Book.query.join(Book.user).filter(User.id == user_id).all()
    return books

def get_shelf_books(user_id):
    """
    Get all books that are on your shelf

    Any books you own or have read - still deciding on if read books should be
    included in your shelf
    :param user_id: int
    :return:
    """
    books = (Book.query
             .join(Book.user)
             .filter(User.id == user_id)
             .filter(or_(Book.owned==True, Book.status==BookStatus.READ))
             .all())
    return books


def update_user_book(search_id, current_user, status, owned):
    """

    :param search_id: int -> google book id aka g_id
    :param current_user: User
    :param status: BookStatus
    :param owned: Boolean
    :return: str, int
    """
    try:
        optional_book = get_book_by_g_id(search_id, current_user)
        if optional_book:
            logger.info(f'Found book: {optional_book.g_id}, {optional_book.status}, {optional_book.owned}')
            optional_book.owned = (owned == 'true' if owned else False)
            optional_book.status = status
            db.session.commit()
            return 'Book Updated', 200
        else:
            book = get_google_book_data_by_id(search_id)
            book.user = current_user
            book.status = status
            book.owned = (owned == 'true')
            logger.info('Adding book: %s', book.to_dict())
            db.session.add(book)
            db.session.commit()
            return 'Book Created', 200
    except Exception as e:
        logger.error(f'Encounter error while saving Book:{search_id}, {e}')
        return 'Error creating book', 400


# def update_book_user(book: Book, current_user: User, add_user):
#     """
#     Re-usable logic for adding/removing user -> review need for this method
#
#     :param book: Book
#     :param current_user: User
#     :param add_user: Boolean
#     :return:
#     """
#     if add_user:
#         book.user.add(current_user)
#     if current_user in book.user and not add_user:
#         book.user.remove(current_user)
#     return book


def get_book_by_g_id(search_id, current_user):
    """
    Get book by g_id and current user

    :param search_id: int
    :param current_user: User
    :return:
    """
    optional_book = (Book.query.join(Book.user)
                     .filter(User.id == current_user.id)
                     .filter(Book.g_id == search_id)
                     .first())
    if optional_book:
        return optional_book
    return None


def get_book_by_position(position, current_user):
    """
    Used by shelf to get book by position and User

    :param position: int
    :param current_user: User
    :return:
    """
    if not position:
        return None
    optional_book = (db.session.query(Book).join(Book.user)
                     .filter(Book.shelf_pos==position)
                     .filter(User.id==current_user.id)
                     .first())
    if optional_book:
        return optional_book
    return None

def gen_home_stats(user_id):
    """
    Get unique Authors, all books and read books by user

    :param user_id:
    :return:
    """
    authors = set()
    all_books = get_books_by_user_id(user_id)
    read_books = [book for book in all_books if book.status == BookStatus.READ]
    for book in all_books:
        auth = book.author.split(', ')
        [authors.add(author) for author in auth]
    return all_books, authors, read_books
