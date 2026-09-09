# Project: P06_django-realworld-example-app
# Layer: Database Query
# Source: conduit/apps/articles/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Article
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer


class ArticlesFeedAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            author__in=self.request.user.profile.follows.all()
        )