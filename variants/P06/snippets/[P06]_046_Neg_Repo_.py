# Project: P06_django-realworld-example-app
# Layer: Database Query - MUTATED
# Antipattern: One-by-One Processing / The Stifle (Chen et al., 2014; Avritzer et al., 2025)

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Article
from .renderers import ArticleJSONRenderer
from .serializers import ArticleSerializer

class ArticleViewSet(mixins.CreateModelMixin, 
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):

    lookup_field = 'slug'
    # FEHLER (One-by-One / The Stifle): select_related entfernt -> N+1 Queries für jeden Datensatz
    queryset = Article.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset = queryset.filter(author__user__username=author)

        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        favorited_by = self.request.query_params.get('favorited', None)
        if favorited_by is not None:
            queryset = queryset.filter(favorited_by__user__username=favorited_by)

        return queryset