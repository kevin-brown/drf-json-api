from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
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

    response = client.generic("echo",
        reverse("person-list"), data=test_data,
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

    response = client.generic("echo",
        reverse("person-list"), data=test_data,
        content_type="application/vnd.api+json")

    assert response.data == output_data
