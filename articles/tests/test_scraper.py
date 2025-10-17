from articles.scraper import extract_date_text, scrape_article_selenium
from articles.models import Article
from bs4 import BeautifulSoup
from django.test import SimpleTestCase, TestCase
from unittest.mock import patch, MagicMock
import dateparser
from datetime import datetime, timedelta


class ExtractDateTextTest(SimpleTestCase):
    def test_should_extract_article_published_time_meta(self):
        html = '<meta property="article:published_time" content="2025-01-15T10:30:00Z">'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2025-01-15T10:30:00Z")

    def test_should_extract_og_published_time_meta(self):
        html = '<meta property="og:published_time" content="2024-12-01T08:00:00+01:00">'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2024-12-01T08:00:00+01:00")

    def test_should_extract_date_name_meta(self):
        html = '<meta name="date" content="2025-03-20">'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2025-03-20")
    
    def test_should_extract_time_tag_text(self):
        html = '<time>13.10.2025</time>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "13.10.2025")

    def test_should_extract_time_tag_datetime_attribute(self):
        html = '<time datetime="2025-08-01T14:00:00">August 1, 2025</time>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertIn("August 1, 2025", result)
    
    def test_should_extract_polish_textual_date(self):
        html = '<p>Opublikowano: 10 września 2024</p>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "10 września 2024")

    def test_should_extract_english_textual_date(self):
        html = '<span>Published on 12 November 2023</span>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "12 November 2023")

    def test_should_extract_dot_format_date(self):
        html = '<div>Data: 25.12.2024</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "25.12.2024")
    
    def test_should_extract_hours_ago_english(self):
        html = '<span>3 hours ago</span>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "3 hours ago")

    def test_should_extract_minutes_ago_english(self):
        html = '<div>45 minutes ago</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "45 minutes ago")

    def test_should_extract_days_ago_english(self):
        html = '<p>2 days ago</p>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2 days ago")

    def test_should_extract_yesterday_english(self):
        html = '<div>yesterday</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "yesterday")
    
    def test_should_extract_godziny_temu_polish(self):
        html = '<span>2 godziny temu</span>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2 godziny temu")

    def test_should_extract_minut_temu_polish(self):
        html = '<div>30 minut temu</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "30 minut temu")

    def test_should_extract_dni_temu_polish(self):
        html = '<p>4 dni temu</p>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "4 dni temu")

    def test_should_extract_wczoraj_polish(self):
        html = '<div>wczoraj</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "wczoraj")
    
    def test_should_prefer_meta_over_time_tag(self):
        html = '''
            <meta property="article:published_time" content="2024-12-12T10:00:00+01:00">
            <time>04.04.2020</time>
        '''
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "2024-12-12T10:00:00+01:00")
    
    def test_should_return_none_when_no_date_found(self):
        html = '<div>brak daty</div><p>just regular text</p>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertIsNone(result)

    def test_should_return_none_for_empty_html(self):
        html = ''
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertIsNone(result)

    def test_should_handle_case_insensitive_matching(self):
        html = '<div>5 HOURS AGO</div>'
        soup = BeautifulSoup(html, "html.parser")
        
        result = extract_date_text(soup)
        
        self.assertEqual(result, "5 HOURS AGO")


class DateParsingIntegrationTest(SimpleTestCase):
    def parse(self, raw, base=None, lang=["pl", "en"]):
        if raw is None:
            return None
        base = base or datetime(2025, 10, 17, 12, 0)
        parsed = dateparser.parse(
            raw,
            languages=lang,
            settings={"RELATIVE_BASE": base}
        )
        if parsed:
            parsed = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            if parsed.tzinfo is not None:
                parsed = parsed.replace(tzinfo=None)
        return parsed

    def test_should_parse_polish_relative_date(self):
        html = "<div>wczoraj</div>"
        soup = BeautifulSoup(html, "html.parser")
        raw = extract_date_text(soup)
        
        base = datetime(2025, 10, 17, 15, 30)
        expected = datetime(2025, 10, 16, 0, 0, 0)
        parsed = self.parse(raw, base, lang=["pl"])
        
        self.assertEqual(parsed, expected)

    def test_should_parse_english_relative_hours(self):
        html = "<div>3 hours ago</div>"
        soup = BeautifulSoup(html, "html.parser")
        raw = extract_date_text(soup)
        
        base = datetime(2025, 10, 17, 15, 0)
        expected = (base - timedelta(hours=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        parsed = self.parse(raw, base, lang=["en"])
        
        self.assertEqual(parsed, expected)

    def test_should_parse_polish_textual_date(self):
        html = "<p>10 września 2024</p>"
        soup = BeautifulSoup(html, "html.parser")
        raw = extract_date_text(soup)
        
        expected = datetime(2024, 9, 10, 0, 0, 0)
        parsed = self.parse(raw, lang=["pl"])
        
        self.assertEqual(parsed, expected)

    def test_should_parse_iso_format_to_naive_datetime(self):
        html = '<meta property="article:published_time" content="2025-01-01T14:00:00+02:00">'
        soup = BeautifulSoup(html, 'html.parser')
        raw = extract_date_text(soup)
        
        expected = datetime(2025, 1, 1, 0, 0, 0)
        parsed = self.parse(raw)
        
        self.assertEqual(parsed, expected)

    def test_should_normalize_time_to_midnight(self):
        html = '<time>13.10.2025 15:30:45</time>'
        soup = BeautifulSoup(html, 'html.parser')
        raw = extract_date_text(soup)
        
        parsed = self.parse(raw)
        
        self.assertEqual(parsed.hour, 0)
        self.assertEqual(parsed.minute, 0)
        self.assertEqual(parsed.second, 0)

    def test_should_return_none_when_unparseable(self):
        html = '<span>jabłko i gruszka</span>'
        soup = BeautifulSoup(html, 'html.parser')
        raw = extract_date_text(soup)
        
        parsed = self.parse(raw)
        
        self.assertIsNone(parsed)


class ScrapeArticleSeleniumTest(TestCase):
    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_create_article_successfully(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '''
            <html>
                <head><title>Test Article</title></head>
                <body>
                    <meta property="article:published_time" content="2025-10-15T10:00:00Z">
                    <p>Article content here.</p>
                </body>
            </html>
        '''
        
        url = "https://example.com/article"
        article = scrape_article_selenium(url)
        
        self.assertIsNotNone(article)
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.source_url, url)
        self.assertEqual(article.source_domain, "example.com")
        self.assertEqual(article.published_at.date(), datetime(2025, 10, 15).date())

        self.assertEqual(article.published_at.hour, 0)
        self.assertEqual(article.published_at.minute, 0)
        
        mock_driver.get.assert_called_once_with(url)
        mock_driver.quit.assert_called_once()

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_skip_duplicate_url(self, mock_driver_manager, mock_chrome):
        url = "https://example.com/duplicate"
        Article.objects.create(
            title="Existing",
            html_content="content",
            plain_text_content="text",
            source_url=url,
            source_domain="example.com",
            published_at=datetime.now()
        )
        
        result = scrape_article_selenium(url)
        
        self.assertIsNone(result)
        mock_chrome.assert_not_called()

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_use_current_date_when_no_date_found(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><head><title>No Date</title></head><body>Content</body></html>'
        
        article = scrape_article_selenium("https://example.com/nodate")
        
        self.assertIsNotNone(article)

        self.assertEqual(article.published_at.date(), datetime.now().date())
        self.assertEqual(article.published_at.hour, 0)
        self.assertEqual(article.published_at.minute, 0)

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_handle_missing_title(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><body>Content without title</body></html>'
        
        article = scrape_article_selenium("https://example.com/notitle")
        
        self.assertEqual(article.title, "No title")

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_extract_domain_from_url(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><head><title>Test</title></head></html>'
        
        article = scrape_article_selenium("https://subdomain.example.com/path/article?param=value")
        
        self.assertEqual(article.source_domain, "subdomain.example.com")

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_normalize_datetime_to_midnight(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '''
            <html>
                <head><title>Time Test</title></head>
                <body><meta property="article:published_time" content="2025-05-20T14:35:22Z"></body>
            </html>
        '''
        
        article = scrape_article_selenium("https://example.com/timetest")
        
        self.assertEqual(article.published_at.hour, 0)
        self.assertEqual(article.published_at.minute, 0)
        self.assertEqual(article.published_at.second, 0)
        self.assertEqual(article.published_at.microsecond, 0)

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_return_none_on_exception(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Network error")
        
        article = scrape_article_selenium("https://example.com/error")
        
        self.assertIsNone(article)

        mock_driver.quit.assert_called_once()

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_always_quit_driver_even_on_error(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.get.side_effect = Exception("Error")
        
        scrape_article_selenium("https://example.com/error")

        mock_driver.quit.assert_called_once()

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    @patch('articles.scraper.time.sleep')
    def test_should_wait_for_page_load(self, mock_sleep, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_driver.page_source = '<html><head><title>Test</title></head></html>'
        
        scrape_article_selenium("https://example.com/test")
        
        mock_sleep.assert_called_once_with(3)

    @patch('articles.scraper.webdriver.Chrome')
    @patch('articles.scraper.ChromeDriverManager')
    def test_should_store_both_html_and_plain_text(self, mock_driver_manager, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        html = '<html><head><title>Test</title></head><body><p>Paragraph 1</p><p>Paragraph 2</p></body></html>'
        mock_driver.page_source = html
        
        article = scrape_article_selenium("https://example.com/test")
        
        self.assertIn('<p>Paragraph 1</p>', article.html_content)
        self.assertIn('Paragraph 1', article.plain_text_content)
        self.assertIn('Paragraph 2', article.plain_text_content)
