from django.core.urlresolvers import reverse
import pytest

from tests.utils import dump_json

pytestmark = pytest.mark.django_db


def test_basic(client):
    test_data = dump_json({
        "people": {
            "name": "test",
        },
    })

    output_data = {
        "name": "test",
    }

    response = client.generic(
        "echo", reverse("person-list"), data=test_data,
        content_type="application/vnd.api+json")

    assert response.data == output_data


def test_multiple(client):
    test_data = dump_json({
        "people": [
            {
                "name": "first",
            },
            {
                "name": "second",
            },
        ],
    })

    output_data = [
        {
            "name": "first",
        },
        {
            "name": "second",
        },
    ]

    response = client.generic(
        "echo", reverse("person-list"), data=test_data,
        content_type="application/vnd.api+json",
    )

    assert response.data == output_data


def test_single_link(client):
    test_data = dump_json({
        "comments": {
            "body": "This is a test comment.",
            "links": {
                "post": "1",
            },
        },
    })

    output_data = {
        "body": "This is a test comment.",
        "post": "http://testserver/posts/1/",
    }

    response = client.generic(
        "echo", reverse("comment-list"), data=test_data,
        content_type="application/vnd.api+json",
    )

    assert response.data == output_data


def test_multiple_link(client):
    test_data = dump_json({
        "posts": {
            "title": "Test post title",
            "links": {
                "comments": ["1", "2"],
            },
        }
    })

    output_data = {
        "title": "Test post title",
        "comments": [
            "http://testserver/comments/1/",
            "http://testserver/comments/2/",
        ],
    }

    response = client.generic(
        "echo", reverse("post-list"), data=test_data,
        content_type="application/vnd.api+json",
    )

    assert response.data == output_data
