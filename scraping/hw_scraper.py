# PROJECT 5
import requests
from bs4 import BeautifulSoup
import json
import csv

url = "https://books.toscrape.com/"
response = requests.get(url)

book_data = []

""" # HELPER functions
parent = where to search
tag	= what tag to find
class_name = class filter
default = fallback if missing
"""
def safe_text(parent, tag, class_name=None, default="N/A"):
    # Try to find element.
    found = parent.find(tag, class_=class_name)
    # If found exists: Extract clean text. Else: Return fallback. No crash.
    return found.text.strip() if found else default # .text = get_text()
# sepration of concerns
def safe_rating(parent):
    tag = parent.find('p', class_='star-rating')
    if tag:
        classes = tag.get('class', [])
        return classes[1] if len(classes) > 1 else "Unknown"
    return "Unknown"

def safe_attr(parent, tag, attr, default="N/A"):
    found = parent.find(tag)
    return found.get(attr, default) if found else default

if response.status_code == 200:
    # .content gives Raw bytes, then BeautifulSoup + lxml Handles decoding itself
    soup = BeautifulSoup(response.content, 'lxml')
    """
    Find all book containers on the page.

    Each book is wrapped in an <article class="product_pod"> element,
    which serves as the semantic container for a single product card.
    """# returns a list of tag objects (each book is literally one HTML block)
    books = soup.find_all('article', class_='product_pod')

    # book = one article container per loop (book becomes the search scope)
    for book in books:
        """
        book
        └── h3
            └── a
                └── get attribute "title"
        """
        # Find the <a> inside that h3.
        # Now: Inside that <a> there is no visible title text.
        # Instead: Book title lives inside HTML attribute: ['title']
        # ['title'] = Give the value of this attribute (just like dict)
        title = safe_attr(book.h3, 'a', 'title')
        # .text = returns visible text inside tag
        price = safe_text(book, 'p', 'price_color')
        # .strip() removes: \n   In stock   \n
        availability = safe_text(book, 'p', 'instock availability', "Unknown")
        """
        Find rating paragraph
        Get its class list
        Take second value
        """
        # class is not one string, its LIST internally,
        # like: ['star-rating', 'Three'], so: ['class'][1] (give second item)
        rating = safe_rating(book)

        book_data.append({
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating
        })

with open('books.json', 'w', encoding='utf-8') as file:
    json.dump(book_data, file, indent=2, ensure_ascii=False)

print(f"Saved {len(book_data)} books to books.json")

with open('books.csv', 'w', newline='', encoding='utf-8') as file:

    fieldnames = ['title', 'price', 'availability', 'rating']

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(book_data)

print(f"Saved {len(book_data)} books to books.csv")
