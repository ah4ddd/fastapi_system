"""
Web scraping = Programmatically extracting data from websites.
HTML = THE SKELETON OF THE WEBPAGE.
The flow:
1. Send HTTP request to website
2. Receive HTML response
3. Parse HTML to find data
4. Extract data
5. Store/process data

The Core Scraping Pipeline
Every scraper in the world is just this:
REQUEST → RESPONSE → PARSE → EXTRACT → STRUCTURE → STORE

RESUEST = ask the server: “Give me the HTML of this page.”
using HTTP GET request

RESPONSE = Server gives: HTML document
Example: <span class="price">$29.99</span>

PARSE = HTML is a tree.. Not a blob.
Like this:
html
 └── body
      └── div
           └── span (price)
Parsing converts: Raw text → Navigable structure
So now you can: “Find all prices”
instead of: “search for random dollar signs in text”

EXTRACTS = locate: titles, prices, links, emails, reviews, names
by their: tag, class, id, attributes
Example: find all <span class="price">

STRUCTURE = Now convert: Messy HTML
into: Clean Python objects

STORE = export to: CSV, JSON, Database, API.
Now data survives and, its usable
"""

"""
Install Libraries:
`install requests beautifulsoup4 lxml`

What these are:
requests = Send HTTP requests to websites (like a browser, but in Python)
beautifulsoup4 = Parse HTML and extract data
lxml = Fast HTML parser (used by BeautifulSoup)
"""

"""
Understanding HTML Structure (Critical Foundation)
Before scraping, you need to understand what you're scraping.
HTML = Hypertext Markup Language
It's the structure of web pages. Everything on a website is HTML.

Basic HTML:
<html>
  <body>
    <h1>Title</h1>
    <p>This is a paragraph</p>
    <div class="container">
      <span>Text inside container</span>
    </div>
  </body>
</html>

Key concepts:
Tags: <h1>, <p>, <div>, <span>
Attributes: class="container", id="header"
Nesting: Tags inside tags (tree structure)

Scraping =
Ignore the visuals
Read the structure
Extract the meaning
"""

"""
Common HTML Tags Used in Web Scraping

<div>  : Block container used to group elements
    Example:
        <div class="product">...</div>
    Think: a box holding related content

<span> : Inline container for small data (price, tags, labels)
    Example:
        <span class="price">$29.99</span>

<a>    : Link tag (critical for scraping URLs)
    Example:
        <a href="/job/123">Apply Now</a>
    text → "Apply Now"
    href → "/job/123"

<h1>-<h6> : Headings (titles, names, product names)

<p>    : Paragraphs (descriptions, summaries)
"""

"""
Attributes: How Scrapers Identify the Right Elements

HTML tags alone are not enough for scraping.
Most pages contain hundreds of similar tags:
    - many <div>
    - many <span>
    - many <p>

To locate the correct element, scrapers rely on attributes.

Example:
    <div class="job-card">

    tag       → div
    attribute → class
    value     → job-card

Scraping logic:
    Find <div> where class = "job-card"

Commonly used attributes:

id      : Unique identifier (usually one per page)
    Example:
        <div id="main-content">

class   : Group identifier (shared by multiple elements)
    Example:
        <span class="price discount">

href    : Link destination (used for extracting URLs)
    Example:
        <a href="/product/123">
"""

"""
HTML, DOM, and Data Containers in Web Scraping
==============================================

Core Mental Model
-----------------
When scraping a webpage, you are NOT scraping classes or CSS.

You are traversing the DOM (Document Object Model).

HTML received from a webpage is raw text markup. The browser (and libraries
like BeautifulSoup) parses this markup into a structured, hierarchical tree
of objects in memory called the DOM.

This tree represents parent-child relationships created by nested HTML tags.

Example HTML:

    <body>
        <div>
            <article>
                <p>Hello</p>
            </article>
        </div>
    </body>

Becomes DOM Tree:

    body
     └── div
          └── article
                └── p
                     └── "Hello" (text node)

Scraping is the act of navigating this tree and extracting values from
specific branches.


Node Types in the DOM
---------------------

1. Element Node (Structure)
   These are HTML tags:

       <article>
       <div>
       <p>
       <a>

   Used to define structure and hierarchy.

2. Attribute Node (Metadata)
   Attributes provide extra data about an element:

       <article class="product_pod" id="book_1">

   Here:
       class = attribute
       id    = attribute

3. Text Node (Content)
   Text inside a tag becomes a child node:

       <p>£51.77</p>

   Structure:

       p
        └── "£51.77"


Tags vs Attributes vs Text in Scraping
--------------------------------------

Tag:
    soup.find('article')

Attribute:
    soup.find('article', class_='product_pod')

Text:
    tag.text

Attribute Value:
    tag['title']


Tree Traversal in Practice
--------------------------

Given:

    <article>
        <h3>
            <a title="Book Name">
        </h3>
    </article>

Accessing:

    book.h3.a['title']

Means:

    article → h3 → a → read 'title'

You are walking down the DOM tree.


Semantic vs Generic Tags
------------------------

<div>
    Generic container.
    Used purely for layout.
    Has no inherent meaning about its content.

<article>
    Semantic container.
    Represents a self-contained unit of content such as:
        - Product card
        - Blog post
        - Job listing
        - Book listing
        - News item

Semantic tags often indicate one full data record.

Example:

    <article class="product_pod">

Represents one book (one complete dataset).

Thus:

    soup.find_all('article', class_='product_pod')

Returns:
    One DOM subtree per book.

Ideal loop point.


HTML5 Structural Tags Often Represent:
--------------------------------------

article : one data record
section : grouped records
nav     : navigation links
header  : title area
footer  : metadata
main    : primary content
aside   : sidebar


Lists and Layout Containers
---------------------------

<li> = List Item

Must exist inside:

    <ul> (unordered list)
    <ol> (ordered list)

Frontend developers frequently use lists to build layout grids:

    <ol class="row">
        <li>
            <article class="product_pod">Book 1</article>
        </li>
        <li>
            <article class="product_pod">Book 2</article>
        </li>
    </ol>

DOM Tree:

    ol
     ├── li
     │    └── article.product_pod
     ├── li
     │    └── article.product_pod

Here:

    ol  = list container
    li  = layout wrapper
    article = actual content record

So you loop on the element representing a full data record:

    soup.find_all('article', class_='product_pod')

If semantic tags are absent:

    <li class="job-card">
        <div class="title">Python Developer</div>
        <div class="salary">$2000</div>
    </li>

Then:

    soup.find_all('li', class_='job-card')

Becomes your loop container.


Final Model
-----------

HTML  = raw markup text
DOM   = parsed hierarchical tree of nodes

Tags        = structural elements
Attributes  = metadata on elements
Text        = content inside elements
Nesting     = parent-child hierarchy

Scraping is:
    Traversing repeated DOM subtrees and extracting values from them.

You are not scraping a page.
You are walking a tree and harvesting data from repeated branches.
"""

# PROJECT 1
import requests # Library to send HTTP requests
from bs4 import BeautifulSoup # Library to parse HTML

# Send HTTP GET request
url = "http://quotes.toscrape.com/" # website to be scraped
"""
requests.get(url) does:
    Opens connection to server
    Sends HTTP GET request
    Receives response
    Stores response in response object

The response object contains:
    response.status_code = HTTP status (200, 404, 500, etc.)
    response.text = HTML content as string
    response.content = HTML content as bytes
    response.headers = HTTP headers
"""
response = requests.get(url)

# check if request was successful
"""
Status codes:
    200 = OK (request successful)
    404 = Not Found (page doesn't exist)
    403 = Forbidden (blocked)
    500 = Server Error
"""
print(f"Status Code: {response.status_code}")

# get html content
html_content = response.text # returns HTML as a string (raw HTML)
print(f"HTML Lenght: {len(html_content)} characters")

# You can't easily extract data from raw string.
# That's why you need BeautifulSoup to parse HTML.
"""
Converts raw HTML string into a BeautifulSoup object.
    BeautifulSoup object = parsed HTML tree.
Now you can navigate the tree and find elements easily.
    'lxml' = parser (fast and forgiving of malformed HTML)
"""
soup = BeautifulSoup(html_content, 'lxml')

# Find all quotes
"""
This returns a list of all <span class="text"> elements.
Breaking it down:
'span' = tag name
class_='text' = CSS class (note the underscore_ because class is a Python keyword)
    Result: List of BeautifulSoup Tag objects
"""
quotes = soup.find_all('span', class_='text')# Find all elements matching criteria

# extract and print text
"""
get_text() = Extract text content from tag, removes HTML.
    <span class="text">"Hello World"</span>
    .get_text() returns "Hello World"
"""
for quote in quotes:
    print(quote.get_text())
