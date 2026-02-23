# PROJECT 5
import requests
from bs4 import BeautifulSoup
import json
import csv

url = "https://books.toscrape.com/"
response = requests.get(url)

book_data = []

if response.status_code == 200:
    # .content gives Raw bytes, then BeautifulSoup + lxml Handles decoding itself
    soup = BeautifulSoup(response.content, 'lxml')
    """
    Find all book containers on the page.

    Each book is wrapped in an <article class="product_pod"> element,
    which serves as the semantic container for a single product card.
    """
    books = soup.find_all('article', class_='product_pod')

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
        title = book.h3.a['title'] # type:ignore
        # .text = returns visible text inside tag
        price = book.find('p', class_='price_color').text # type:ignore
        # .strip() removes: \n   In stock   \n
        availability = book.find('p', class_='instock availability').text.strip() # type: ignore
        """
        Find rating paragraph
        Get its class list
        Take second value
        """
        # class is not one string, its LIST internally,
        # like: ['star-rating', 'Three'], so: ['class'][1] (give second item)
        rating = book.find('p', class_='star-rating')['class'][1]  # type:ignore

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
