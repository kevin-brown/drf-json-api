from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from tests import models
import pytest

pytestmark = pytest.mark.django_db


def test_delete(client):
    person = models.Person.objects.create(name="test")

    response = client.delete(reverse("person-detail", args=[person.id]))

    assert response.status_code == 204
    assert response.content == force_bytes("")
