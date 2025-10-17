from rest_framework import generics

from articles.models import Article

from .serializers import ArticleSerializer


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.all()
        source = self.request.GET.get("source")
        if source is not None:
            queryset = queryset.filter(source_domain=source)
        return queryset


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
