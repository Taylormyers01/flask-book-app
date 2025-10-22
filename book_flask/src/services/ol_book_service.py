# ISBN: https://openlibrary.org/api/books?bibkeys=ISBN:9780765326362,ISBN:9780765326355&format=json&jscmd=data
from logger import logger
from models.ol_book import OlBook

BASE_URL = 'https://openlibrary.org/api/books'

import requests

BASE_SEARCH = "https://openlibrary.org/search.json"
BASE_WORK = "https://openlibrary.org"

def fetch_book_details(work_key):
    """Fetch detailed info for one work."""
    r = requests.get(f"{BASE_WORK}{work_key}.json")
    if r.status_code == 200:
        return r.json()
    return {}

def search_books(title=None, author=None, q=None, limit=5):
    params = {"limit": limit}
    if title: params["title"] = title
    if author: params["author"] = author
    if q: params["q"] = q

    res = requests.get(BASE_SEARCH, params=params)
    res.raise_for_status()
    data = res.json()

    logger.info(data)
    books = []
    for doc in data.get("docs", []):
        work_key = doc.get("key")
        if not work_key:
            continue

        # Fetch full details
        details = fetch_book_details(work_key)
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
            if "cover_i" in doc
            else None
        )

        books.append(create_ol_book(doc, details, cover_url, work_key))

    return books

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