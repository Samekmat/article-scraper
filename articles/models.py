from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=500)
    html_content = models.TextField()
    plain_text_content = models.TextField()
    source_url = models.URLField(unique=True)
    published_at = models.DateTimeField()
    source_domain = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.title
