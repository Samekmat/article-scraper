from rest_framework.test import APITestCase
from rest_framework import status
from articles.models import Article
from datetime import datetime


class ArticleListAPITest(APITestCase):
    def setUp(self):
        self.article1 = Article.objects.create(
            title="Article One",
            html_content="<p>HTML 1</p>",
            plain_text_content="Text 1",
            source_url="https://site1.com/article1",
            published_at=datetime(2025, 1, 15),
            source_domain="site1.com"
        )
        self.article2 = Article.objects.create(
            title="Article Two",
            html_content="<p>HTML 2</p>",
            plain_text_content="Text 2",
            source_url="https://site2.com/article2",
            published_at=datetime(2025, 2, 20),
            source_domain="site2.com"
        )

    def test_should_return_200_and_all_articles(self):
        response = self.client.get('/api/articles/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_should_return_correct_json_structure(self):
        response = self.client.get('/api/articles/')
        article = response.data[0]

        required_fields = [
            'id', 'title', 'html_content', 'plain_text_content',
            'source_url', 'published_at', 'source_domain'
        ]
        for field in required_fields:
            self.assertIn(field, article)

    def test_should_return_empty_list_when_no_articles(self):
        Article.objects.all().delete()
        response = self.client.get('/api/articles/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
    
    def test_should_filter_by_source_domain(self):
        response = self.client.get('/api/articles/?source=site1.com')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['source_domain'], 'site1.com')

    def test_should_return_empty_for_nonexistent_domain(self):
        response = self.client.get('/api/articles/?source=nonexistent.com')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_should_return_multiple_articles_from_same_domain(self):
        Article.objects.create(
            title="Article Three",
            html_content="<p>HTML 3</p>",
            plain_text_content="Text 3",
            source_url="https://site1.com/article3",
            published_at=datetime.now(),
            source_domain="site1.com"
        )
        
        response = self.client.get('/api/articles/?source=site1.com')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_should_not_allow_post_put_delete(self):
        self.assertEqual(
            self.client.post('/api/articles/', {}).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.put('/api/articles/', {}).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.delete('/api/articles/').status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )


class ArticleDetailAPITest(APITestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="Detail Article",
            html_content="<p>HTML</p>",
            plain_text_content="Text",
            source_url="https://example.com/article",
            published_at=datetime(2025, 10, 17),
            source_domain="example.com"
        )

    def test_should_return_200_and_article_details(self):
        response = self.client.get(f'/api/articles/{self.article.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.article.id)
        self.assertEqual(response.data['title'], "Detail Article")

    def test_should_return_404_for_nonexistent_article(self):
        response = self.client.get('/api/articles/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_should_return_correct_json_structure(self):
        response = self.client.get(f'/api/articles/{self.article.id}/')
        
        required_fields = [
            'id', 'title', 'html_content', 'plain_text_content',
            'source_url', 'published_at', 'source_domain'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_should_not_allow_post_put_delete(self):
        url = f'/api/articles/{self.article.id}/'
        
        self.assertEqual(
            self.client.post(url, {}).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.put(url, {}).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            self.client.delete(url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
