# Project 6
# PAGINATION = Splitting one large dataset into multiple pages
# Each page = subset of same dataset.
# We are doing Page Number Pagination (Static pagination, Easy to scrape)
# Another common pagination types are:
# - Query Parameter Pagination & Cursor / Infinite Scroll (JS hell)
import requests # HTTP client
from bs4 import BeautifulSoup # Parser
import json # For serialization
import time # For Rate limiting (dont be spam bot)

# Protect against: None.text → crash
def safe_text(parent, tag, class_name=None, default="N/A"):
    found = parent.find(tag, class_=class_name)
    return found.text.strip() if found else default

# Same logic nut: Extracts attribute instead of text.
def safe_attr(parent, tag, attr, default="N/A"):
    found = parent.find(tag)
    return found.get(attr, default) if found else default

def safe_rating(parent):
    tag = parent.find('p', class_='star-rating')
    if tag:
        classes = tag.get('class', [])
        return classes[1] if len(classes) > 1 else "Unknown"
    return "Unknown"

def scrape_page(page_num) -> list: # page_num — which page to scrape (1, 2, 3, ..)
    """Scrape a single page and return book data"""

    # Dynamic URL Building
    if page_num == 1: # Page 1 URL is different. This handles both cases.
        url = "https://books.toscrape.com/catalogue/page-1.html"
    else: # Dataset segmented across URLs.
        url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"

    print(f"Scraping page {page_num}: {url}")

    # Actual Scraping
    try: # If the site doesn't respond within 10 seconds, raise a Timeout error.
        # Without timeout, if the site is slow, scraper hangs forever.
        response = requests.get(url, timeout=10)

        if response.status_code != 200: # Prevent parsing garbage.
            print(f"Failed to fetch page {page_num}. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'lxml') # parsed DOM tree
        # Find all elements matching given criteria in DOM tree
        books = soup.find_all('article', class_='product_pod')

        # Keep each page’s extraction separate before aggregation.
        page_books = []

        for book in books:
            title = safe_attr(book.h3, 'a', 'title')
            price = safe_text(book, 'p', 'price_color')
            availability = safe_text(book, 'p', 'instock availability', "Unknown")
            rating = safe_rating(book)

            page_books.append({
                'title': title,
                'price': price,
                'availability': availability,
                'rating': rating,
                'page': page_num
            })
        # Returns: List of books from that page.
        return page_books
    # If ANY network error happens (timeout, connection refused, DNS failure),
    # the scraper doesn't crash. It just skips that page and continues.
    except requests.exceptions.Timeout: # specific timeout errors
        print(f"Timeout on page {page_num}")
        return []
    except requests.exceptions.RequestException as e: # all other request errors
        print(f"Error on page {page_num}: {e}")
        return [] # return empty list instead of crashing

all_books = []

"""
GET page 1
Extract books
Check if next page exists
If yes:
    Build next URL
    GET next page
    Extract books
Repeat
Until no next page
""" # Iterative data harvesting across paginated resources.
for page in range(1, 6):
    books = scrape_page(page) # scrapes that page, returns list of books

    all_books.extend(books)

    time.sleep(1) # Rate Limiting

with open('all_books.json', 'w', encoding='utf-8') as file:
    json.dump(all_books, file, indent=2, ensure_ascii=False)

print(f"\nTotal books scraped: {len(all_books)}")
print(f"Saved to all_books.json")

"""
Use .extend() instead of .append() when combining paginated results.

append(x):
    Adds x as a single element to the list.
    If x is a list, it becomes a nested list (list of lists).

extend(iterable):
    Iterates over the iterable and appends each element individually,
    keeping the list flat.

Python internally behaves almost like this:
for item in books:
    all_books.append(item)

Example:
    all_books.append(books)
        -> [[{A}, {B}], [{C}, {D}]]

    all_books.extend(books)
        -> [{A}, {B}, {C}, {D}]

Important:
    extend() does NOT remove or mutate the original list.
    It simply iterates over it and appends each item.

Use extend() when building one unified dataset across pages.
"""
