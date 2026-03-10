# PORJECT 7
import requests
from bs4 import BeautifulSoup

HEADERS = {
    # Identify browser type/version
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # tell server what content types I am willing to receive (HTML, images, etc.)
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    # preferred language (English)
    'Accept-Language': 'en-US,en;q=0.5',
    # where you came from (pretend you came from Google)
    'Referer': 'https://www.google.com/',
    # Do Not Track (privacy header) Irony: almost nobody respects it.
    'DNT': '1',
    # Keep TCP connection open for reuse (browsers do this)
    'Connection': 'keep-alive',
    # If this resource is HTTP, try to upgrade to HTTPS.
    'Upgrade-Insecure-Requests': '1'
}

def scrape_with_headers(url):
    """Scrape a URL with browser-like headers"""

    print(f"Scraping: {url}")

    try: # headers=HEADERS sends your fake browser headers with the request
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            title = soup.find('title')
            print(f"Page title: {title.get_text() if title else 'No title'}")
            return True
        else:
            print(f"Failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

scrape_with_headers("https://books.toscrape.com/")

"""
How HTTP Headers Work in requests.get()

When calling:

    response = requests.get(url, headers=HEADERS, timeout=10)

Mechanically, the following happens:

1. requests builds an HTTP request object.
2. Opens a TCP connection to the server.
3. Sends a formatted HTTP request (structured text) including headers.
4. Server reads headers and decides how to respond.
5. Server returns a response (usually HTML).
6. requests wraps it into a Python Response object.

There is no magic — just structured text over TCP.

--------------------------------------------------
Purpose of Common Headers in Scraping
--------------------------------------------------

User-Agent:
    Identifies the client (browser/OS/engine/version).
    Servers use this to distinguish real browsers from bots.
    Example:
        python-requests/...  → likely automated
        Mozilla/5.0 ...      → likely browser
    This is the most important header for basic bot filtering.

Accept:
    Specifies which content types the client can handle.
    Example:
        Accept: application/json → server may return JSON
        Accept: text/html        → server may return HTML
    Enables content negotiation.

Accept-Language:
    Indicates preferred language.
    Example:
        en-US,en;q=0.5
    Server may localize language, currency, or formatting.

Referer:
    Indicates where the request originated from.
    Some sites flag direct requests without referer as suspicious.

DNT (Do Not Track):
    Requests privacy preference.
    Mostly cosmetic in scraping.

Connection:
    keep-alive allows TCP reuse.
    requests already manages connection pooling internally.

Upgrade-Insecure-Requests:
    Browser hint to prefer HTTPS.
    Not critical for scraping.

--------------------------------------------------
What Headers Actually Achieve
--------------------------------------------------

Headers help mimic a real browser request.

They:
    - Reduce basic bot detection
    - Improve compatibility
    - Influence server content negotiation

They do NOT:
    - Execute JavaScript
    - Solve Cloudflare challenges
    - Generate valid browser fingerprints
    - Fake TLS fingerprints
    - Handle advanced anti-bot systems

--------------------------------------------------
Reality Check

Adding headers helps pass basic detection (User-Agent checks).
It does NOT make your scraper indistinguishable from a real browser.

Advanced systems analyze:
    - Request frequency
    - IP behavior
    - Cookies
    - JS execution
    - TLS fingerprint
    - Header consistency

Headers are step one, not full stealth.

Use them to look like a browser.
Do not assume they make you one.
"""
