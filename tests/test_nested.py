from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


def test_single_linked(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(author=author, title="One amazing test post.")
    models.Comment.objects.create(post=post, body="This is a test comment.")
    models.Comment.objects.create(post=post, body="One more comment.")

    results = {
        "posts": [
            {
                "id": "1",
                "href": "http://testserver/posts/1/",
                "title": "One amazing test post.",
                "links": {
                    "author": "1",
                    "comments": ["1", "2"],
                },
            },
        ],
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}/",
                "type": "people",
            },
            "posts.comments": {
                "href": "http://testserver/comments/{posts.comments}/",
                "type": "comments",
            },
            "posts.comments.post": {
                "href": "http://testserver/posts/{posts.comments.post}/",
                "type": "posts",
            }
        },
        "linked": {
            "comments": [
                {
                    "id": "1",
                    "href": "http://testserver/comments/1/",
                    "body": "This is a test comment.",
                    "links": {
                        "post": "1",
                    },
                },
                {
                    "id": "2",
                    "href": "http://testserver/comments/2/",
                    "body": "One more comment.",
                    "links": {
                        "post": "1",
                    },
                },
            ],
        },
    }

    response = client.get(reverse("nested-post-list"))

    assert response.content == dump_json(results)
