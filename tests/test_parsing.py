from django.core.urlresolvers import reverse
from io import BytesIO
from rest_framework.test import APITestCase
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


class TestData(APITestCase):

    def test_test(self):
        test_data = {
            "people": {
                "name": "test",
            },
        }

        output_data = {
            "name": "test",
        }

        response = self.client.put(reverse("person-list"), test_data)

        assert response.data == output_data

    def test_multiple(self):
        test_data = {
            "people": [
                {
                    "name": "first",
                },
                {
                    "name": "second",
                },
            ],
        }

        output_data = [
            {
                "name": "first",
            },
            {
                "name": "second",
            },
        ]

        response = self.client.put(reverse("person-list"), test_data)

        assert response.data == output_data
