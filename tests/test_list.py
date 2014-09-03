"""Test list views

Includes success tests for creating resources by POST to the list view
Error tests are in test_errors.py
"""

from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


def test_empty_list(client):
    results = {
        "posts": [],
    }

    response = client.get(reverse("post-list"))

    assert response.content == dump_json(results)


def test_single_item_list(client):
    models.Person.objects.create(name="test")

    results = {
        "people": [
            {
                "id": "1",
                "href": "http://testserver/people/1/",
                "name": "test",
            },
        ]
    }

    response = client.get(reverse("person-list"))

    assert response.content == dump_json(results)


def test_multiple_item_list(client):
    models.Person.objects.create(name="test")
    models.Person.objects.create(name="other")

    results = {
        "people": [
            {
                "id": "1",
                "href": "http://testserver/people/1/",
                "name": "test",
            },
            {
                "id": "2",
                "href": "http://testserver/people/2/",
                "name": "other",
            },
        ]
    }

    response = client.get(reverse("person-list"))

    assert response.content == dump_json(results)


def test_create_person_success(client):
    data = dump_json({
        "people": {
            "name": "Jason Api"
        }
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "Jason Api",
        }
    }

    response = client.post(
        reverse("person-list"), data=data,
        content_type="application/vnd.api+json")

    assert response.status_code == 201
    assert response.content == dump_json(results)
    assert response['content-type'] == 'application/vnd.api+json'
    person = models.Person.objects.get()
    assert person.name == 'Jason Api'


def test_create_post_success(client):
    author = models.Person.objects.create(name="The Author")

    data = dump_json({
        "posts": {
            "title": "This is the title",
            "links": {
                "author": author.pk,
            },
        }
    })

    response = client.post(
        reverse("post-list"), data=data,
        content_type="application/vnd.api+json")
    assert response.status_code == 201
    assert response['content-type'] == 'application/vnd.api+json'

    post = models.Post.objects.get()
    results = {
        "posts": {
            "id": str(post.pk),
            "href": "http://testserver/posts/%s/" % post.pk,
            "title": "This is the title",
            "links": {
                "author": str(author.pk),
                "comments": []
            }
        },
        "links": {
            "posts.author": {
                "href": "http://testserver/people/{posts.author}/",
                "type": "people"
            },
            "posts.comments": {
                "href": "http://testserver/comments/{posts.comments}/",
                "type": "comments"
            }
        },
    }
    assert response.content == dump_json(results)


def test_options(client):
    results = {
        "meta": {
            "actions": {
                "POST": {
                    "author": {
                        "label": "author",
                        "read_only": False,
                        "required": True,
                        "type": "field"
                    },
                    "comments": {
                        "read_only": False,
                        "required": True,
                        "type": "field"
                    },
                    "id": {
                        "label": "ID",
                        "read_only": True,
                        "required": False,
                        "type": "integer"
                    },
                    "title": {
                        "label": "title",
                        "max_length": 100,
                        "read_only": False,
                        "required": True,
                        "type": "string"
                    },
                    "url": {
                        "read_only": True,
                        "required": False,
                        "type": "field"
                    }
                }
            },
            "description": "",
            "name": "Post List",
            "parses": ["application/vnd.api+json"],
            "renders": ["application/vnd.api+json"],
        }
    }
    response = client.options(reverse("post-list"))
    assert response.status_code == 200
    assert response.content == dump_json(results)
