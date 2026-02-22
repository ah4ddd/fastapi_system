import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"
# Give the HTML of this page
response = requests.get(url)

# Check If Page Exists
if response.status_code == 200:
    # Converts: raw HTML string into: Parsed HTML tree
    """
    html
      └── body
            └── div (quote)
                ├── span (text)
                ├── small (author)
                └── a (tag)
    """
    #Now: soup and later quote_div are not strings. They are: Navigable tree nodes
    soup = BeautifulSoup(response.text, 'lxml')

    # Find all boxes that represent a full quote entry (divs)
    # Each quote_div = 1 complete record
    """
    <div> stands for division, a box container. A grouping mechanism
    to Group related content into a single logical block.
    So: CSS can style it
        JS can manipulate it
        Scrapers can extract it
        div = folder
        Inside folder: Files.
            Example:
            Job Listing
            ├── Title
            ├── Company
            └── Location
        in this file's case: That entire block = 1 quote record.

    Understanding this line:
    `quote_divs = soup.find_all('div', class_='quote')`
    This tells BeautifulSoup:
        Find all <div> elements where class = "quote"

    Each <div class="quote"> represents one full quote block.
    Result:
        quote_divs becomes a list of quote containers:
            [
                div (quote 1),
                div (quote 2),
                div (quote 3),
            ]
    Each container holds:
        - quote text
        - author
        - tags
    """
    quote_divs = soup.find_all('div', class_='quote') # Quote ↔ Author ↔ Tags

    # loop through each record and, process each quote block individually.
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
        # .find() to navigate nested elements. find the FIRST tag
        #    whose: tag name is `span` class is `text``
        text = quote_div.find('span', class_='text').get_text() # type:ignore

        # Extract author (same idea as quote)
        # Now quote is matched with correct author.

        author = quote_div.find('small', class_='author').get_text() # type:ignore

        # Extract tags
        # Each quote may have multiple tags, Returns: list of tag elements.
        # find_all(): Inside THIS container find ALL tags
        #    whose: tag name is `a` class is `tag`,
        #    then returns List of Tag objects
        tag_elements = quote_div.find_all('a', class_='tag')
        """
        Loop through each tag
        Extract its text
        Store into list : tags = ["life", "inspirational"]
        """
        # tag.get_text() = Remove HTML tags and give only visible text
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

"""
Inline HTML Elements in this Scraping script

<span> : Generic inline container for small text without breaking layout.
    Example: <span class="text">Quote here</span>
    Used for main inline content (e.g. quote text).

<small> : Semantic tag for secondary metadata (authors, timestamps).
    Example: <small class="author">Albert Einstein</small>
    Indicates supporting info, not primary content.

<a> : Anchor tag for hyperlinks.
    Example: <a href="/tag/life">life</a>
    Used to extract links or tags via href.

Inside:
    <div class="quote">

You extract:
    span  → main content
    small → metadata
    a     → linkable tags

Scraping relies on:
    Tag + Attribute (e.g. class)

<p>     → paragraph
<h1>    → heading
<a>     → link
<img>   → image
"""
