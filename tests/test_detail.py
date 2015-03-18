from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json, parse_json
import pytest

pytestmark = pytest.mark.django_db


def test_object(client):
    models.Person.objects.create(name="test")

    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
            }
        }
    }

    response = client.get(reverse("person-detail", args=[1]))

    assert parse_json(response.content) == results


def test_object_with_optional_links(client):
    models.Person.objects.create(name="test")

    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.get(reverse("people-full-detail", args=[1]))

    assert parse_json(response.content) == results


def test_update_attribute(client):
    models.Person.objects.create(name="test")

    data = dump_json({
        "data": {
            "name": "new test",
        },
    })
    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "new test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.patch(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results


def test_update_to_one_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)

    data = dump_json({
        "data": {
            "name": "test",
            "links": {
                "favorite_post": {
                    "linkage": {
                        "type": "posts",
                        "id": str(post.pk),
                    },
                },
            },
        },
    })
    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": {
                        "type": "posts",
                        "id": str(post.pk),
                    },
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.patch(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results


def test_update_to_many_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)
    comment1 = models.Comment.objects.create(body="Comment 1", post=post)
    comment2 = models.Comment.objects.create(body="Comment 2", post=post)

    data = dump_json({
        "data": {
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": {
                    "linkage": [
                        {
                            "type": "comments",
                            "id": str(comment1.pk),
                        },
                        {
                            "type": "comments",
                            "id": str(comment2.pk),
                        },
                    ],
                },
            },
        },
    })
    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [
                        {
                            "type": "comments",
                            "id": str(comment1.pk),
                        },
                        {
                            "type": "comments",
                            "id": str(comment2.pk),
                        },
                    ],
                },
            },
        },
    }

    response = client.put(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results


def test_object_with_pk_links(client):
    models.Person.objects.create(name="test")

    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.get(reverse("pk-people-full-detail", args=[1]))

    assert parse_json(response.content) == results


def test_update_pk_attribute(client):
    models.Person.objects.create(name="test")

    data = dump_json({
        "data": {
            "type": "people",
            "name": "new test",
            "links": {
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    })

    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "new test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.patch(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results


def test_update_to_one_pk_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)

    data = dump_json({
        "data": {
            "name": "test",
            "type": "people",
            "links": {
                "favorite_post": {
                    "linkage": {
                        "type": "posts",
                        "id": str(post.pk),
                    }
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    })
    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": {
                        "type": "posts",
                        "id": str(post.pk),
                    },
                },
                "liked_comments": {
                    "linkage": [],
                },
            },
        },
    }

    response = client.put(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results


def test_update_to_many_pk_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)
    comment1 = models.Comment.objects.create(body="Comment 1", post=post)
    comment2 = models.Comment.objects.create(body="Comment 2", post=post)

    data = dump_json({
        "data": {
            "name": "test",
            "type": "people",
            "links": {
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [
                        {
                            "type": "comments",
                            "id": str(comment1.pk),
                        },
                        {
                            "type": "comments",
                            "id": str(comment2.pk),
                        },
                    ],
                },
            },
        },
    })
    results = {
        "data": {
            "id": "1",
            "type": "people",
            "name": "test",
            "links": {
                "self": "http://testserver/people/1/",
                "favorite_post": {
                    "linkage": None,
                },
                "liked_comments": {
                    "linkage": [
                        {
                            "type": "comments",
                            "id": str(comment1.pk),
                        },
                        {
                            "type": "comments",
                            "id": str(comment2.pk),
                        },
                    ],
                },
            },
        },
    }

    response = client.put(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert parse_json(response.content) == results
