from django.utils.encoding import force_text
from django.utils.text import slugify

from rest_framework.serializers import RelatedField

try:
    from rest_framework.serializers import ManyRelatedField
except ImportError:
    ManyRelatedField = type(None)

try:
    from rest_framework.serializers import ListSerializer
except ImportError:
    ListSerializer = type(None)


def get_related_field(field):
    if isinstance(field, ManyRelatedField):
        return field.child_relation

    if isinstance(field, ListSerializer):
        return field.child

    return field


def is_related_many(field):
    if hasattr(field, "many"):
        return field.many

    if isinstance(field, ManyRelatedField):
        return True

    if isinstance(field, ListSerializer):
        return True

    return False


def model_from_obj(obj):
    model = getattr(obj, "model", None)

    if model is not None:
        return model

    queryset = getattr(obj, "queryset", None)

    if queryset is not None:
        return queryset.model

    return None


def model_to_resource_type(model):
    '''Return the verbose plural form of a model name, with underscores

    Examples:
    Person -> "people"
    ProfileImage -> "profile_image"
    '''
    if model is None:
        return "data"

    return force_text(model._meta.verbose_name_plural)

#
# String conversion
#


def camelcase(string):
    '''Return a string in lowerCamelCase

    Examples:
    "people" -> "people"
    "profile images" -> "profileImages"
    '''
    out = slug(string).replace('-', ' ').title().replace(' ', '')
    return out[0].lower() + out[1:]


def slug(string):
    '''Return a string where words are connected with hyphens'''
    return slugify(force_text(string))


def snakecase(string):
    '''Return a string where words are connected with underscores

    Examples:
    "people" -> "people"
    "profile images" -> "profile_images"
    '''
    return slug(string).replace('-', '_')
