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
