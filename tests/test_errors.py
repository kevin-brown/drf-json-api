"""Test error response renderer"""

from django.core.urlresolvers import reverse
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from tests import models
from tests.serializers import PersonSerializer
from tests.utils import dump_json
from tests.views import PersonViewSet
import pytest

pytestmark = pytest.mark.django_db


def test_required_field_omitted(client):
    data = {"name": ""}
    data_json_api = dump_json({"people": data})

    response = client.post(
        reverse("person-list"), data=data_json_api,
        content_type="application/vnd.api+json")

    assert response.status_code == 400, response.content
    assert not models.Person.objects.exists()

    result_data = {"name": ["This field is required."]}
    assert response.data == result_data

    results = {
        "errors": [{
            "path": "/name",
            "detail": "This field is required.",
            "status": "400"
        }]
    }
    assert response.content == dump_json(results)


def test_auth_required(rf):
    class RestrictedPersonViewSet(PersonViewSet):
        permission_classes = [IsAuthenticated]

    data = dump_json({"people": {"name": "Jason Api"}})

    request = rf.post(
        reverse("person-list"), data=data,
        content_type="application/vnd.api+json")
    view = RestrictedPersonViewSet.as_view({'post': 'create'})
    response = view(request)
    response.render()

    assert response.status_code == 403, response.content
    assert not models.Person.objects.exists()

    results = {
        "errors": [{
            "status": "403",
            "title": "Authentication credentials were not provided."
        }]
    }
    assert response.content == dump_json(results)


def test_field_validation_error(rf):
    class LazyPersonSerializer(PersonSerializer):
        def validate(self, attr):
            raise ValidationError("Feeling lazy. Try again later.")

    class LazyPersonViewSet(PersonViewSet):
        serializer_class = LazyPersonSerializer

    data = dump_json({"people": {"name": "Jason Api"}})

    request = rf.post(
        reverse("person-list"), data=data,
        content_type="application/vnd.api+json")
    view = LazyPersonViewSet.as_view({'post': 'create'})
    response = view(request)
    response.render()

    assert response.status_code == 400, response.content
    assert not models.Person.objects.exists()

    results = {
        "errors": [{
            "status": "400",
            "path": "/-",
            "detail": "Feeling lazy. Try again later."
        }]
    }
    assert response.content == dump_json(results)


def test_invalid_forward_relation(client):
    assert not models.Person.objects.exists()

    data = dump_json({
        "posts": {
            "title": "This is the title",
            "author": "http://testserver/people/1/",
        }
    })

    response = client.post(
        reverse("post-list"), data=data,
        content_type="application/vnd.api+json")

    assert response.status_code == 400, response.content
    assert response['content-type'] == 'application/vnd.api+json'
    assert not models.Post.objects.exists()

    results = {
        "errors": [{
            "status": "400",
            "path": "/author",
            "detail": "Invalid hyperlink - object does not exist."
        }]
    }
    assert response.content == dump_json(results)


def test_invalid_reverse_relation(client):
    author = models.Person.objects.create(name="The Author")
    assert not models.Comment.objects.exists()
    data = dump_json({
        "posts": {
            "title": "This is the title",
            "author": "http://testserver/people/%d/" % author.pk,
            "comments": ["http://testserver/comments/1/"]
        }
    })

    response = client.post(
        reverse("post-list"), data=data,
        content_type="application/vnd.api+json")

    assert response.status_code == 400, response.content
    assert response['content-type'] == 'application/vnd.api+json'

    results = {
        "errors": [{
            "status": "400",
            "path": "/comments",
            "detail": "Invalid hyperlink - object does not exist."
        }]
    }
    assert response.content == dump_json(results)
