from rest_framework import viewsets
from tests import models


class CommentViewSet(viewsets.ModelViewSet):
    model = models.Comment


class PersonViewSet(viewsets.ModelViewSet):
    model = models.Person


class PostViewSet(viewsets.ModelViewSet):
    model = models.Post
