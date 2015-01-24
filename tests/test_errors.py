"""Test error response renderer"""

from django.core.urlresolvers import reverse
from rest_framework.relations import HyperlinkedRelatedField
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated

from tests import models
from tests.serializers import PersonSerializer
from tests.utils import dump_json
from tests.views import PersonViewSet

import pytest
import rest_framework

pytestmark = pytest.mark.django_db

# "Invalid hyperlink - object does not exist." - DRF 2.x
# "Invalid hyperlink - Object does not exist." - DRF 3.x
# Both wrapped in a proxy class that needs to be unproxied
#  in order to serialized to JSON
does_not_exist = (
    HyperlinkedRelatedField.default_error_messages['does_not_exist']
    .encode('utf-8').decode('utf-8'))


def test_required_field_omitted(client):
    data = {}
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


def test_drf_non_field_validation_error(rf):
    '''DRF uses 'non_field_errors' as the key for non-field errors'''
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


@pytest.mark.skipif(
    rest_framework.__version__.split(".")[0] >= "3",
    reason="DRF 3+ no longer calls model.clean",
)
def test_django_non_field_validation_error(rf, monkeypatch):
    '''Django uses __all__ as the key for non-field errors

    Constant is django.core.exceptions.NON_FIELD_ERRORS
    '''
    def clean(self):
        raise ValidationError("I'm not taking any new people today")

    monkeypatch.setattr(models.Person, 'clean', clean)
    data = dump_json({"people": {"name": "Jason Api"}})

    request = rf.post(
        reverse("person-list"), data=data,
        content_type="application/vnd.api+json")
    view = PersonViewSet.as_view({'post': 'create'})
    response = view(request)
    response.render()

    assert response.status_code == 400, response.content
    assert not models.Person.objects.exists()

    results = {
        "errors": [{
            "status": "400",
            "path": "/-",
            "detail": "I'm not taking any new people today"
        }]
    }
    assert response.content == dump_json(results)


def test_invalid_forward_relation(client):
    assert not models.Person.objects.exists()

    data = dump_json({
        "posts": {
            "title": "This is the title",
            "author": "http://testserver/people/1/",
            "comments": [],
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
            "detail": does_not_exist
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
            "detail": does_not_exist
        }]
    }

    assert response.content == dump_json(results)


def test_bad_json(client):
    data = "{'people': {'name': 'Jason Api'}}"  # Wrong quotes

    response = client.post(
        reverse("person-list"), data=data,
        content_type="application/vnd.api+json")

    assert response.status_code == 400, response.content
    assert response['content-type'] == 'application/vnd.api+json'

    results = {
        "errors": [{
            "status": "400",
            "detail": (
                "JSON parse error - Expecting property name enclosed in"
                " double quotes: line 1 column 2 (char 1)"),
        }]
    }
    assert response.content == dump_json(results)
