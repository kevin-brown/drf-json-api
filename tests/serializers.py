from rest_framework import relations, serializers
from tests import models
import rest_framework


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


class MaximalPersonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        fields = ("id", "url", "name", "favorite_post", "liked_comments")
        model = models.Person


class MinimalCommentSerializer(CommentSerializer):

    class Meta(CommentSerializer.Meta):
        fields = ("id", "url", "body", )


class MinimalPostSerializer(PostSerializer):

    class Meta(PostSerializer.Meta):
        fields = ("id", "url", "title", )


class NestedCommentSerializer(CommentSerializer):
    post = MinimalPostSerializer()


class NestedPostSerializer(PostSerializer):
    comments = MinimalCommentSerializer(many=True)


class PkCommentSerializer(CommentSerializer):
    post = relations.PrimaryKeyRelatedField(queryset=models.Post.objects)


single_related_kwargs = {}

if rest_framework.__version__.split(".")[0] >= "3":
    single_related_kwargs = {"allow_null": True}


class PkMaximalPersonSerializer(MaximalPersonSerializer):
    favorite_post = relations.PrimaryKeyRelatedField(required=False, queryset=models.Post.objects, **single_related_kwargs)
    liked_comments = relations.PrimaryKeyRelatedField(required=False, many=True, queryset=models.Comment.objects)
