from rest_framework import relations, serializers
from tests import models


class CommentSerializer(serializers.ModelSerializer):
    post = relations.HyperlinkedRelatedField(view_name="post-detail")

    class Meta:
        model = models.Comment


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Person


class PostSerializer(serializers.ModelSerializer):
    author = relations.HyperlinkedRelatedField(view_name="person-detail")
    comments = relations.HyperlinkedRelatedField(view_name="comment-detail", many=True)

    class Meta:
        fields = ("id", "title", "author", "comments")
        model = models.Post
