import requests
from bs4 import BeautifulSoup
# Comma Separated Values, very simple way to store table data like Excel.
# Each row = one record, Each column = separated by comma
import csv # built-in Python module to create CSV files

url = "https://quotes.toscrape.com/"
response = requests.get(url)

# Store all scraped quote records, Eventually becomes a list of dictionaries.
quotes_data = [] # Structured data in memory.

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml') # Raw HTML → navigable tree.
    quote_divs = soup.find_all('div', class_='quote') # Get all `quote` boxes

    # Process one quote at a time.
    for quote_div in quote_divs:
        # EXTRACT FIELDS
        text = quote_div.find('span', class_='text').get_text() # type:ignore
        author = quote_div.find('small', class_='author').get_text() # type:ignore
        tag_elements = quote_div.find_all('a', class_='tag')
        # get text and join into one string
        tags = ', '.join([tag.get_text() for tag in tag_elements])

        # store dict in list
        # Each dictionary = 1 row.
        # Each key = column name.
        quotes_data.append({
            'quote': text,
            'author': author,
            'tags': tags
        })

# # Create quote.csv in write mode; newline avoids blank rows,
# UTF-8 enabled, auto-closes with 'with'.
with open('quotes.csv', 'w', newline='', encoding='utf-8') as file:
    # DEFINE COLUMNS (csv column headers)
    fieldnames = ['quote', 'author', 'tags']
    """
    A helper object that knows:
    How to take dictionaries
    and write them properly into this CSV file.
    """ # DictWriter = Translator, translate dict into CSV row using the keys
    # DictWriter expects each row as a dict matching the predefined fieldnames.
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # WRITE HEADER. creates: `quote,author,tags` as first row
    writer.writeheader()
    # WRITE DATA ROWS: loop through list of dictionaries and,
    # writes each as row in csv
    writer.writerows(quotes_data)

print(f"Saved {len(quotes_data)} quotes to quotes.csv")

"""
pipeline:
Internet
↓
HTML
↓
Parse
↓
Extract
↓
Structure (dict)
↓
Store (list)
↓
Export (CSV)
"""
