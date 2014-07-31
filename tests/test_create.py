from django.core.urlresolvers import reverse
from tests import models
from tests.utils import dump_json
import pytest

pytestmark = pytest.mark.django_db


def test_create_success(client):
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

    assert response.content == dump_json(results)
    assert response['content-type'] == 'application/vnd.api+json'

    person = models.Person.objects.get()
    assert person.name == 'Jason Api'


def test_create_failure(client):
    data = {"name": ""}
    data_json_api = dump_json({"people": data})
    result_data = {"name": ["This field is required."]}
    results = {"errors": {"fields": result_data}}

    response = client.post(
        reverse("person-list"), data=data_json_api,
        content_type="application/vnd.api+json")

    assert response.content == dump_json(results)
    assert response.data == result_data
    assert not models.Person.objects.exists()
