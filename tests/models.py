from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=50)

    # Nullable ForeignKey
    favorite_post = models.ForeignKey(
        "Post", blank=True, null=True, related_name="favorited_by")

    # To-Many Forward Relation
    liked_comments = models.ManyToManyField("Comment", related_name="liked_by")

    class Meta:
        verbose_name_plural = "people"


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Person, related_name="posts")


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments")
    body = models.TextField()


class ProfileImage(models.Model):
    '''A profile image stored in a CDN'''
    person = models.ForeignKey(Person)
    url = models.URLField()
    current = models.BooleanField(db_index=True)
