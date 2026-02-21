import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"
# Give the HTML of this page
response = requests.get(url)

# Check If Page Exists
if response.status_code == 200:
    # Converts: raw HTML string into: structured DOM tree
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all boxes that represent a full quote entry (divs)
    # Each quote_div = 1 complete record
    quote_divs = soup.find_all('div', class_='quote') # Quote ↔ Author ↔ Tags

    # loop through each record and, print its result
    for quote_div in quote_divs:
        # Extract quote text
        """
        Inside this specific div container:
        Find: <span class="text">
        Then: Remove HTML tags
        Return: Just the quote string.
        """
        """
        telling the scraper:
        Inside this quote container
        Find: A span
              whose class is "text"
              because when I inspected the page
              that's where the quote was.
        """
        text = quote_div.find('span', class_='text').get_text() # type:ignore

        # Extract author (same idea as quote)
        # Now quote is matched with correct author.
        author = quote_div.find('small', class_='author').get_text() # type:ignore

        # Extract tags
        # Each quote may have multiple tags, Returns: list of tag elements.
        tag_elements = quote_div.find_all('a', class_='tag')
        """
        Loop through each tag
        Extract its text
        Store into list : tags = ["life", "inspirational"]
        """
        tags = [tag.get_text() for tag in tag_elements] # List comprehension.

        # Print formatted output
        print(f"Quote: {text}")
        print(f"Author: {author}")
        # .join() converts: ["life", "hope"] into: life, hope (readable output)
        print(f"Tags: {', '.join(tags)}")
        print("-" * 80)
# Failure case
else:
    print(f"Failed to fetch page. Status: {response.status_code}")
