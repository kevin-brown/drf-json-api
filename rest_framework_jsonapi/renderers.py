from rest_framework import renderers
from django.utils import six


class JsonApiMixin(object):

    def determine_fields(self, data, renderer_context):
        fields = getattr(data, "fields", None)

        if fields is not None:
            return fields

        if hasattr(data, "__iter__") and data:
            data = next(iter(data))

            return self.determine_fields(
                data=data,
                renderer_context=renderer_context,
            )

        if renderer_context is not None:
            view = renderer_context.get("view", None)

            if hasattr(view, "get_serializer"):
                serializer = view.get_serializer(instance=None)
                data = serializer.data

                return self.determine_fields(
                    data=data,
                    renderer_context=renderer_context,
                )

        return None

    def resource_type(self, data, renderer_context):
        if renderer_context is None:
            return None

        view = renderer_context.get("view", None)

        if view is None:
            return None

        model = getattr(view, "model", None)

        if model is None:
            queryset = getattr(view, "queryset", None)

            if queryset is None:
                return None

            model = queryset.model

        return six.text_type(model._meta.verbose_name_plural)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        wrapper = {}

        fields = self.determine_fields(
            data=data,
            renderer_context=renderer_context,
        )

        resource_type = self.resource_type(
            data=data,
            renderer_context=renderer_context,
        )

        resource_type = resource_type or "data"

        wrapper[resource_type] = data

        return super(JsonApiMixin, self).render(
            data=wrapper,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )


class JsonApiRenderer(JsonApiMixin, renderers.JSONRenderer):
    pass
