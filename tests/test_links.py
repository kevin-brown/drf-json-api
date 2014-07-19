from django.core.urlresolvers import reverse
from tests import models
import json
import pytest

pytestmark = pytest.mark.django_db


def test_single_links(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(author=author, title="Rails is Omakase")
    models.Comment.objects.create(post=post, body="Some text for testing.")

    results =  {
        "links": {
            "comments.post": {
                "href": "http://testserver/posts/{comments.post}/",
                "type": "posts",
            },
        },
        "comments": [
            {
                "id": "1",
                "body": "Some text for testing.",
                "href": "http://testserver/comments/1/",
                "links": {
                    "post": "1",
                }
            },
        ],
    }

    response = client.get(reverse("comment-list"))

    assert response.content == json.dumps(results, sort_keys=True)


def test_multiple_links(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(author=author, title="Rails is Omakase")
    models.Comment.objects.create(post=post, body="Test comment one.")
    models.Comment.objects.create(post=post, body="Test comment two.")

    results =  {
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}/",
                "type": "people",
            },
            "posts.comments": {
                "href": "http://testserver/comments/{posts.comments}/",
                "type": "comments",
            }
        },
        "posts": [
            {
                "id": "1",
                "title": "Rails is Omakase",
                "href": "http://testserver/posts/1/",
                "links": {
                    "author": "1",
                    "comments": ["1", "2"]
                }
            },
        ],
    }

    response = client.get(reverse("post-list"))

    assert response.content == json.dumps(results, sort_keys=True)
