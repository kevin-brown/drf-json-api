from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


def test_object(client):
    models.Person.objects.create(name="test")

    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
        }
    }

    response = client.get(reverse("person-detail", args=[1]))

    assert response.content == dump_json(results)


def test_object_with_optional_links(client):
    models.Person.objects.create(name="test")

    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": [],
            }
        },
        "links": {
            "people.favorite_post": {
                "href": "http://testserver/posts/{people.favorite_post}/",
                "type": "posts"
            },
            "people.liked_comments": {
                "href": "http://testserver/comments/{people.liked_comments}/",
                "type": "comments"
            },
        }
    }

    response = client.get(reverse("people-full-detail", args=[1]))

    assert response.content == dump_json(results)


def test_update_attribute(client):
    models.Person.objects.create(name="test")

    data = dump_json({
        "people": {
            "name": "new test",
        },
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "new test",
            "links": {
                "favorite_post": None,
                "liked_comments": [],
            }
        },
        "links": {
            "people.favorite_post": {
                "href": "http://testserver/posts/{people.favorite_post}/",
                "type": "posts"
            },
            "people.liked_comments": {
                "href": "http://testserver/comments/{people.liked_comments}/",
                "type": "comments"
            },
        }
    }

    response = client.patch(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert response.content == dump_json(results)


def test_update_to_one_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)

    data = dump_json({
        "people": {
            "name": "test",
            "links": {
                "favorite_post": str(post.pk),
            }
        },
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": str(post.pk),
                "liked_comments": [],
            }
        },
        "links": {
            "people.favorite_post": {
                "href": "http://testserver/posts/{people.favorite_post}/",
                "type": "posts"
            },
            "people.liked_comments": {
                "href": "http://testserver/comments/{people.liked_comments}/",
                "type": "comments"
            },
        }
    }

    response = client.patch(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")
    assert response.content == dump_json(results)


def test_update_to_many_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)
    comment1 = models.Comment.objects.create(body="Comment 1", post=post)
    comment2 = models.Comment.objects.create(body="Comment 2", post=post)

    data = dump_json({
        "people": {
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": [str(comment1.pk), str(comment2.pk)],
            }
        },
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": [str(comment1.pk), str(comment2.pk)],
            }
        },
        "links": {
            "people.favorite_post": {
                "href": "http://testserver/posts/{people.favorite_post}/",
                "type": "posts"
            },
            "people.liked_comments": {
                "href": "http://testserver/comments/{people.liked_comments}/",
                "type": "comments"
            },
        }
    }

    response = client.put(
        reverse("people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")
    assert response.content == dump_json(results)


def test_object_with_pk_links(client):
    models.Person.objects.create(name="test")

    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": []
            }
        },
        "links": {
            "people.favorite_post": {
                "type": "posts"
            },
            "people.liked_comments": {
                "type": "comments"
            }
        }
    }

    response = client.get(reverse("pk-people-full-detail", args=[1]))

    assert response.content == dump_json(results)


def test_update_pk_attribute(client):
    models.Person.objects.create(name="test")

    data = dump_json({
        "people": {
            "name": "new test",
            "links": {
                "favorite_post": None,
                "liked_comments": [],
            }
        },
    })

    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "new test",
            "links": {
                "favorite_post": None,
                "liked_comments": []
            }
        },
        "links": {
            "people.favorite_post": {
                "type": "posts"
            },
            "people.liked_comments": {
                "type": "comments"
            }
        }
    }

    response = client.patch(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")

    assert response.content == dump_json(results)


def test_update_to_one_pk_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)

    data = dump_json({
        "people": {
            "name": "test",
            "links": {
                "favorite_post": str(post.pk),
                "liked_comments": []
            }
        },
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": str(post.pk),
                "liked_comments": []
            }
        },
        "links": {
            "people.favorite_post": {
                "type": "posts"
            },
            "people.liked_comments": {
                "type": "comments"
            }
        }
    }

    response = client.put(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")
    assert response.content == dump_json(results)


def test_update_to_many_pk_link(client):
    models.Person.objects.create(name="test")
    author = models.Person.objects.create(name="author")
    post = models.Post.objects.create(title="The Post", author=author)
    comment1 = models.Comment.objects.create(body="Comment 1", post=post)
    comment2 = models.Comment.objects.create(body="Comment 2", post=post)

    data = dump_json({
        "people": {
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": [str(comment1.pk), str(comment2.pk)]
            }
        },
    })
    results = {
        "people": {
            "id": "1",
            "href": "http://testserver/people/1/",
            "name": "test",
            "links": {
                "favorite_post": None,
                "liked_comments": [str(comment1.pk), str(comment2.pk)]
            }
        },
        "links": {
            "people.favorite_post": {
                "type": "posts"
            },
            "people.liked_comments": {
                "type": "comments"
            }
        }
    }

    response = client.put(
        reverse("pk-people-full-detail", args=[1]), data,
        content_type="application/vnd.api+json")
    assert response.content == dump_json(results)
