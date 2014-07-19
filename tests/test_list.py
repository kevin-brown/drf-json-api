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
