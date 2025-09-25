from pprint import pprint
from olclient.openlibrary import OpenLibrary
from logger import logger
import requests

ol = OpenLibrary()
search_url = "https://openlibrary.org/search.json?q={}&fields=key,title,author_name,works"

# search_results = ol.Author.search('blake crouch', limit=2)
# dark_matter = ol.Work.get('OL17358795W')

def get_work_by_olid(olid):
    logger.info(f"Fetching work by OLID: {olid}")
    book = ol.Work.get('OL17358795W')
    return book

def search_work(key):
    logger.info(f"Fetching work by key: {key}")
    query = search_url.format(key)
    response = requests.get(query)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "No works found"