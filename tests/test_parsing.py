from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
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
