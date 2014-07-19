from rest_framework import relations, serializers
from tests import models


class CommentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ("id", "url", "post", "body", )
        model = models.Comment


class PersonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ("id", "url", "name", )
        model = models.Person


class PostSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ("id", "url", "title", "author", "comments", )
        model = models.Post


class NestedPostSerializer(PostSerializer):
    comments = CommentSerializer(many=True)
