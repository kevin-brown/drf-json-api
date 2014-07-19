import pytest


@pytest.fixture()
def renderer():
    from rest_framework_jsonapi import renderers

    return renderers.JsonApiRenderer()


@pytest.fixture()
def PersonSerializer():
    from rest_framework import serializers
    from tests import models

    class PersonSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.Person

    return PersonSerializer


@pytest.fixture()
def PostSerializer():
    from rest_framework import serializers
    from tests import models

    class PostSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.Post

    return PostSerializer


@pytest.fixture()
def CommentSerializer():
    from rest_framework import serializers
    from tests import models

    class CommentSerializer(serializers.ModelSerializer):

        class Meta:
            model = models.Comment

    return CommentSerializer


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',

            'rest_framework',
            'tests',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
        REST_FRAMEWORK={
            "DEFAULT_RENDERER_CLASSES": (
                "rest_framework_jsonapi.renderers.JsonApiRenderer",
            ),
        },
    )
