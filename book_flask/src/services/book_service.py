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
    Get Google books by search query -

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


def get_g_book_by_g_id(gid, params=None):
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


def test_data():
    g_data = get_books_by_query("Brandon Sanderson")
    books = [generate_book_from_g_data(data) for data in g_data.get('items', [])]
    if not books:
        return "No books found"
    return books


def get_books_by_user_id(user_id):
    books = Book.query.join(Book.users).filter(User.id == user_id).all()
    return books

def get_shelf_books(user_id):
    books = (Book.query
             .join(Book.users)
             .filter(User.id == user_id)
             .filter(or_(Book.owned==True, Book.status==BookStatus.READ))
             .all())
    return books


def update_user_book(search_id, current_user, status, owned):
    try:
        optional_book = get_book_by_g_id(search_id, current_user)
        if optional_book:
            logger.info(f'Found book: {optional_book.g_id}, {optional_book.status}, {optional_book.owned}')
            if owned or status in VALID_STATUS:
                logger.info('Adding user to book')
                optional_book = update_book_user(optional_book, current_user, True)
            else:
                logger.info('Removing user from book')
                optional_book = update_book_user(optional_book, current_user, False)
            optional_book.owned = (owned == 'true' if owned else False)
            optional_book.status = status
            db.session.commit()
            return 'Book Updated', 200
        else:
            book = get_g_book_by_g_id(search_id)
            book.users.add(current_user)
            book.status = status
            book.owned = (owned == 'true')
            logger.info('Adding book: %s', book.to_dict())
            db.session.add(book)
            db.session.commit()
            return 'Book Created', 200
    except Exception as e:
        logger.error(f'Encounter error while saving Book:{search_id}, {e}')
        return 'Error creating book', 400


def update_book_user(book: Book, current_user: User, add_user):
    if add_user and not current_user in book.users:
        book.users.add(current_user)
    if current_user in book.users and not add_user:
        book.users.remove(current_user)
    return book


def get_book_by_g_id(search_id, current_user):
    # optional_book = db.session.query(Book).filter_by(g_id=search_id).filter_by().first()
    optional_book = (Book.query.join(Book.users)
                     .filter(User.id == current_user.id)
                     .filter(Book.g_id == search_id)
                     .first())
    if optional_book:
        return optional_book
    return None


def get_book_by_position(position, current_user):
    if not position:
        return None
    optional_book = (db.session.query(Book).join(Book.users)
                     .filter(Book.shelf_pos==position)
                     .filter(User.id==current_user.id)
                     .first())
    if optional_book:
        return optional_book
    return None

def gen_home_stats(user_id):
    authors = set()
    all_books = get_books_by_user_id(user_id)
    read_books = [book for book in all_books if book.status == BookStatus.READ]
    for book in all_books:
        auth = book.author.split(', ')
        [authors.add(author) for author in auth]
    return all_books, authors, read_books
