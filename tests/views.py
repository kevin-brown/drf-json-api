from rest_framework import viewsets
from tests import models
from tests import serializers


class CommentViewSet(viewsets.ModelViewSet):
    model = models.Comment
    serializer_class = serializers.CommentSerializer


class PersonViewSet(viewsets.ModelViewSet):
    model = models.Person
    serializer_class = serializers.PersonSerializer


class PostViewSet(viewsets.ModelViewSet):
    model = models.Post
    serializer_class = serializers.PostSerializer


class NestedPostViewSet(PostViewSet):
    serializer_class = serializers.NestedPostSerializer
