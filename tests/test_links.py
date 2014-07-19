from django.core.urlresolvers import reverse
from tests import models
import json
import pytest

pytestmark = pytest.mark.django_db


def test_single_links(client):
    author = models.Person.objects.create(name="test")
    post = models.Post.objects.create(author=author, title="Rails is Omakase")

    results =  {
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}",
                "type": "people",
            },
        },
        "posts": [
            {
                "id": "1",
                "title": "Rails is Omakase",
                "links": {
                    "author": "1",
                },
            },
        ],
    }

    response = client.get(reverse("post-list"))

    assert response.content == json.dumps(results)
