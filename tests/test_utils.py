from rest_framework_json_api.utils import (
    camelcase, model_to_resource_type, slug, snakecase)
from .models import Person, ProfileImage


def test_camelcase():
    assert camelcase('people') == 'people'
    assert camelcase('profile images') == 'profileImages'


def test_slug():
    assert slug('people') == 'people'
    assert slug('profile images') == 'profile-images'


def test_snakecase():
    assert snakecase('people') == 'people'
    assert snakecase('profile images') == 'profile_images'


def test_model_to_resource_type():
    assert model_to_resource_type(Person) == 'people'
    assert model_to_resource_type(ProfileImage) == 'profile images'
