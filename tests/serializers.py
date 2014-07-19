from rest_framework import serializers
from tests import models


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Comment


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Person


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ("id", "title", "author")
        model = models.Post
