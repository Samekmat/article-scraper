from datetime import datetime
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import dateparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .models import Article
import re


def extract_date_text(soup):
    """
    Extracts the publication date from HTML content, supporting:
    - <meta> tags: article:published_time, datePublished, og:published_time, etc.
    - <time> tags: by text or 'datetime' attribute (any recognizable format)
    - <p>, <span>, <div>: Polish and English textual formats (e.g. '10 września 2025', '10 October 2025')
    - Relative date phrases in English ('3 hours ago') and Polish ('3 godziny temu')
    - Dot date format: dd.mm.yyyy
    - Fallback: scans main text of the page

    Args:
        soup (BeautifulSoup): Parsed HTML content.

    Returns:
        str or None: Extracted date string as found in HTML, or None if not found.
    """
    # Meta tags
    for tag in soup.find_all('meta'):
        if tag.get('property') in ['article:published_time', 'og:published_time', 'datePublished']:
            if tag.get('content'):
                return tag.get('content')
        if tag.get('name') in ['date', 'publishdate', 'pubdate']:
            if tag.get('content'):
                return tag.get('content')

    # <time> tags
    for t in soup.find_all('time'):
        txt = t.get_text(strip=True)
        if txt:
            return txt
        datetime_attr = t.get('datetime')
        if datetime_attr:
            return datetime_attr

    # Patterns for textual/relative dates
    date_patterns = [
        r"\d{1,2} [a-ząćęłńóśźż]+ \d{4}",
        r"\d{1,2} [A-Za-z]+ \d{4}",
        r"\d{2}\.\d{2}\.\d{4}",
        r"\d+\s+(hours?|minutes?|days?)\s+ago",
        r"\d+\s+godzin(y)?\s+temu",
        r"\d+\s+minut(y)?\s+temu",
        r"\d+\s+dni\s+temu",
    ]
    relative_words = r"(yesterday|today|wczoraj|dzisiaj)"

    for tag in soup.find_all(['p', 'span', 'div']):
        txt = tag.get_text(strip=True)
        for pat in date_patterns:
            match = re.search(pat, txt, re.IGNORECASE)
            if match:
                return match.group(0)
        if re.search(relative_words, txt, re.IGNORECASE):
            return txt

    # Fallback: scan the main text (sometimes date in header/footer)
    main_text = soup.get_text(separator=' ', strip=True)
    for pat in date_patterns:
        match = re.search(pat, main_text, re.IGNORECASE)
        if match:
            return match.group(0)
    match = re.search(relative_words, main_text, re.IGNORECASE)
    if match:
        return match.group(0)

    return None


def scrape_article_selenium(url):
    """
    Scrapes a single article using Selenium and BeautifulSoup, and saves to an Article model.
    - Checks if Article with given source_url already exists (skip if yes)
    - Uses Selenium to render page (including JS), retrieves HTML and plain text
    - Extracts publication date (many formats/edge cases) using extract_date_text()
    - Uses dateparser to normalize to Python datetime object
    - Always sets hour/minute/second to 00:00:00
    - Handles errors gracefully; logs actions and exceptions

    Args:
        url (str): Target article URL.

    Returns:
        Article or None: Saved Article instance, or None if duplicate/error encountered.
    """
    if Article.objects.filter(source_url=url).exists():
        print(f"Article already exists: {url}")
        return None

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(3)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        plain_text_content = soup.get_text(separator="\n", strip=True)
        published_str = extract_date_text(soup)

        published_date = None
        if published_str:
            published_date = dateparser.parse(
                published_str,
                languages=["pl", "en"],
                settings={
                    'TIMEZONE': 'Europe/Warsaw',
                    'RETURN_AS_TIMEZONE_AWARE': False,
                    'RELATIVE_BASE': datetime.now()
                }
            )
        if not published_date:
            published_date = datetime.now()

        published_date = published_date.replace(hour=0, minute=0, second=0, microsecond=0)

        source_domain = urlparse(url).netloc

        article = Article.objects.create(
            title=title,
            html_content=html_content,
            plain_text_content=plain_text_content,
            source_url=url,
            published_at=published_date,
            source_domain=source_domain,
        )
        print(f"Article saved: {title} ({published_date.strftime('%d.%m.%Y %H:%M:%S')})")
        return article

    except Exception as e:
        print(f"Error occurred in {url}: {e}")
        return None
    finally:
        driver.quit()
