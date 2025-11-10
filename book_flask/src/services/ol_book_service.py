from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from logger import logger
from models.constants import BookStatus
from models.ol_book import OlBook
from models.user_ol_book import UserOlBook
from services.db import db

pool = ThreadPoolExecutor(max_workers=20)

BASE_URL = 'https://openlibrary.org/api/books'
BASE_SEARCH = "https://openlibrary.org/search.json"
BASE_WORK = "https://openlibrary.org/works/"
# ISBN: https://openlibrary.org/api/books?bibkeys=ISBN:9780765326362,ISBN:9780765326355&format=json&jscmd=data


def fetch_book_details(work_key):
    r = requests.get(f"{BASE_WORK}{work_key}.json", timeout=20)
    r.raise_for_status()
    return r.json()

def fetch_book_details_sync(doc):
    from app import app
    with app.app_context():
        # Example key /works/OL8894965W
        work_key = doc.get("key").split('/')[-1]
        if not work_key:
            return

        # To avoid extra api calls -> checks if book exists in DB
        ol_book = get_ol_book_if_exists(work_key)
        if ol_book:
            return ol_book
        # Fetch full details
        details = fetch_book_details(work_key)

        # https://covers.openlibrary.org/b/id/14658160-L.jpg
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
            if "cover_i" in doc
            else None
        )

        return create_ol_book(doc, details, cover_url, work_key)

def search_books(title=None, author=None, q=None, limit=20):
    params = {"limit": limit}
    if title: params["title"] = title
    if author: params["author"] = author
    if q: params["q"] = q

    res = requests.get(BASE_SEARCH, params=params)
    res.raise_for_status()
    data = res.json()

    futures = [pool.submit(fetch_book_details_sync, doc) for doc in data.get("docs", [])]
    results = [f.result() for f in as_completed(futures)]

    return results

def create_ol_book(doc, details, cover_url, work_key):
    description = details.get("description", {}).get("value") \
        if isinstance(details.get("description"), dict) \
        else details.get("description")
    return OlBook(
        ol_id=work_key,
        title = doc.get("title"),
        author = ", ".join(doc.get("author_name", [])),
        thumbnail = cover_url,
        description = description,
        published_year = doc.get("first_publish_year"),
        categories = details.get("subjects", [])
    )

def get_books_by_isbn(isbns):
    bibkeys = ",".join([f"ISBN:{isbn}" for isbn in isbns])
    url = f"{BASE_URL}?bibkeys={bibkeys}&format=json&jscmd=data"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Flatten results into a list
        books = []
        for doc in data.values():
            work_key = doc.get("key")
            if not work_key:
                continue

            # Fetch full details
            details = fetch_book_details(work_key)
            cover_url = doc.get('cover', {}).get('large', {})
            books.append(create_ol_book(doc, details, cover_url, work_key))

        return books
    else:
        print("Error:", response.status_code)
        return []

def get_ol_book_if_exists(ol_id):
    return OlBook.query.filter_by(ol_id=ol_id).first()

def update_user_ol_book(current_user, book_dict):
    logger.info(book_dict)
    try:
        ol_id = book_dict.get('ol_id', None)
        if not ol_id:
            logger.error('No ol_id supplied in book_dict')
            return 'No ol_id supplied in book_dict', 400
        owned = book_dict.get('owned', None)
        owned = str(owned).lower() in ('true', '1')
        status = book_dict.get('status', None)
        shelf_pos = book_dict.get('shelf_pos', None)
        u_ol_book = current_user.get_user_ol_book(ol_id)
        if u_ol_book:
            # u_ol_book.ol_book.update_from_json(data=book_dict)
            if owned is not None: u_ol_book.owned = owned
            if status: u_ol_book.status = status
            if shelf_pos: u_ol_book.shelf_pos = shelf_pos
            db.session.commit()
            return 'Book Added to relationship obj', 200
        else:
            ol_book = get_ol_book_if_exists(ol_id)
            if not ol_book:
                ol_book = OlBook()
                ol_book.update_from_json(book_dict)
            user_ol_book = UserOlBook(
                user=current_user,
                ol_book=ol_book,
                owned=owned,
                status=status,
                shelf_pos=shelf_pos
            )
            db.session.add(user_ol_book)
            db.session.commit()
            return 'Book created and added to relationship obj', 200

    except Exception as e:
        logger.exception(e)
        return 'Failed to update book', 400

def gen_home_stats(user):
    """
    Get unique Authors, all books and read books by user

    :param user:
    :return:
    """
    authors = set()
    all_books = [ub.ol_book for ub in user.user_ol_books]
    read_books = [ub.ol_book for ub in user.user_ol_books if ub.status == BookStatus.READ]
    for book in all_books:
        auth = book.author.split(', ')
        [authors.add(author) for author in auth]
    return all_books, authors, read_books

def get_shelf_books(current_user):
    """
    Get all books that are on your shelf

    Any books you own or have read - still deciding on if read books should be
    included in your shelf
    :param current_user: User
    :return:
    """
    shelf_books = [ub.ol_book for ub in current_user.user_ol_books
                   if ub.owned==True or ub.status==BookStatus.READ]
    return shelf_books