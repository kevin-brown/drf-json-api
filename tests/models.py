from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "people"


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Person, related_name="posts")


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments")
    body = models.TextField()
