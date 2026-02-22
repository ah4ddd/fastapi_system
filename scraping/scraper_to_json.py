# PROJECT 4

import requests
from bs4 import BeautifulSoup
import json

url = "https://quotes.toscrape.com/"
response = requests.get(url)

quotes_data = []

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    quote_divs = soup.find_all('div', class_='quote')

    for quote_div in quote_divs:
        text = quote_div.find('span', class_='text').get_text() # type:ignore
        author = quote_div.find('small', class_='author').get_text() # type:ignore
        tag_elements = quote_div.find_all('a', class_='tag')
        tags = [tag.get_text() for tag in tag_elements]

        quotes_data.append({
            'quote': text,
            'author': author,
            'tags': tags
        })

# Create a JSON file structure and allow special characters
with open('quotes.json', 'w', encoding='utf-8') as file:
    # Take this Python object, convert it into JSON format,
    # and write it to this file.
    json.dump(quotes_data, file, indent=2, ensure_ascii=False)

print(f"Saved {len(quotes_data)} quotes to quotes.json")
