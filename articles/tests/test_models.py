from datetime import datetime

from django.db.utils import IntegrityError
from django.test import TestCase

from articles.models import Article


class ArticleModelTest(TestCase):
    def test_should_create_article_with_all_fields(self):
        article = Article.objects.create(
            title="Test Article",
            html_content="<p>content</p>",
            plain_text_content="content",
            source_url="https://example.com/article",
            published_at=datetime(2025, 10, 17),
            source_domain="example.com",
        )

        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(article.title, "Test Article")

    def test_should_return_title_as_string_representation(self):
        article = Article.objects.create(
            title="My Title",
            html_content="content",
            plain_text_content="text",
            source_url="https://example.com/test",
            published_at=datetime.now(),
            source_domain="example.com",
        )

        self.assertEqual(str(article), "My Title")

    def test_should_enforce_unique_source_url(self):
        Article.objects.create(
            title="First",
            html_content="content",
            plain_text_content="text",
            source_url="https://duplicate.com/article",
            published_at=datetime.now(),
            source_domain="duplicate.com",
        )

        with self.assertRaises(IntegrityError):
            Article.objects.create(
                title="Second",
                html_content="content",
                plain_text_content="text",
                source_url="https://duplicate.com/article",
                published_at=datetime.now(),
                source_domain="duplicate.com",
            )

    def test_should_filter_by_source_domain(self):
        Article.objects.create(
            title="Article 1",
            html_content="content",
            plain_text_content="text",
            source_url="https://site1.com/a1",
            published_at=datetime.now(),
            source_domain="site1.com",
        )
        Article.objects.create(
            title="Article 2",
            html_content="content",
            plain_text_content="text",
            source_url="https://site2.com/a2",
            published_at=datetime.now(),
            source_domain="site2.com",
        )

        filtered = Article.objects.filter(source_domain="site1.com")

        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, "Article 1")
