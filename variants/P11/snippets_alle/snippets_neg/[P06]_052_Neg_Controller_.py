# Project: P06_django-realworld-example-app
# Layer: Controller / HTTP (MUTATED: Negativbeispiel)
# Antipattern: The Stifle / Missing Eager Loading (Avritzer et al., 2025)

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Article, Comment
from .renderers import CommentJSONRenderer
from .serializers import CommentSerializer


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    # FEHLER (The Stifle): select_related(...) entfernt. Löst bei der Response-
    # Serialisierung kaskadierende Einzelabfragen für Relationen aus.
    queryset = Comment.objects.all()
    
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def create(self, request, article_slug=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)