import logging
from datetime import datetime
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import dateparser
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

from .models import Article
import re


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("scraper.log", encoding='utf-8'),
    ]
)

def get_selenium_driver():
    """
    Creates webdriver Selenium in local or remote mode.
    Mode chosen by environment variable REMOTE_SELENIUM.
    """
    remote = os.environ.get("REMOTE_SELENIUM", "false").lower() == "true"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    chrome_bin = os.environ.get("CHROME_BINARY")
    if chrome_bin:
        options.binary_location = chrome_bin

    if remote:
        selenium_url = os.environ.get("SELENIUM_URL", "http://selenium:4444/wd/hub")
        return webdriver.Remote(command_executor=selenium_url, options=options)
    else:
        if ChromeDriverManager is None:
            raise RuntimeError("webdriver_manager must be installed locally!")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_date_text(soup):
    for tag in soup.find_all('meta'):
        if tag.get('property') in ['article:published_time', 'og:published_time', 'datePublished']:
            if tag.get('content'):
                return tag.get('content')
        if tag.get('name') in ['date', 'publishdate', 'pubdate']:
            if tag.get('content'):
                return tag.get('content')

    for t in soup.find_all('time'):
        txt = t.get_text(strip=True)
        if txt:
            return txt
        datetime_attr = t.get('datetime')
        if datetime_attr:
            return datetime_attr

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
    - Checks if Article with given source_url already exists (logs and skips if yes)
    - Uses Selenium to render page (including JS), retrieves HTML and plain text
    - Extracts publication date (many formats/edge cases) using extract_date_text()
    - Uses dateparser to normalize to Python datetime object
    - Always sets hour/minute/second to 00:00:00
    - Handles errors gracefully; logs actions and exceptions (timeout, network, content, error pages)

    Args:
        url (str): Target article URL.

    Returns:
        Article or None: Saved Article instance, or None if duplicate/error encountered.
    """
    if Article.objects.filter(source_url=url).exists():
        logging.info(f"Article already exists: {url}")
        return None

    driver = get_selenium_driver()
    try:
        driver.set_page_load_timeout(20)
        try:
            driver.get(url)
        except Exception as e:
            logging.error(f"Page load timeout or network error for {url}: {e}")
            return None
        time.sleep(3)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check for 404/500 or error pages in the title or page text
        page_title = (soup.title.string if soup.title and soup.title.string else "").lower()
        page_text = soup.get_text(separator=" ", strip=True).lower()
        error_signatures = [
            "404", "not found", "error 404", "nie znaleziono", "strona nie została znaleziona",
            "500", "internal server error", "error 500", "błąd serwera"
        ]
        if any(signature in page_title for signature in error_signatures) or \
           any(signature in page_text for signature in error_signatures) or \
           len(page_text) < 200:
            logging.warning(f"Possible error page (404/500) or too short HTML for {url}")
            return None

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
        logging.info(f"Article saved: {title} ({published_date.strftime('%d.%m.%Y %H:%M:%S')})")
        return article

    except Exception as e:
        logging.exception(f"Unexpected error while scraping {url}")
        return None
    finally:
        driver.quit()
