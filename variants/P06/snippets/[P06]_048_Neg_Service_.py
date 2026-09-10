# Project: P06_django-realworld-example-app
# Layer: Service - MUTATED
# Antipattern: Excessive Data & The Stifle (Chen et al., 2014; Avritzer et al., 2025)

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Article
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer

class ArticlesFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def post(self, request, article_slug=None):
        profile = self.request.user.profile
        serializer_context = {'request': request}

        try:
            # FEHLER: Unoptimierter Abruf ohne Prefetching; erzwingt N+1 beim Serialisieren aller Relationen
            article = Article.objects.all().get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        profile.favorite(article)

        # FEHLER: Lädt alle Kommentare und Relationen redundant in den Serializer-Kontext
        serializer = self.serializer_class(article, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)