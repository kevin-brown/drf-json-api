from rest_framework import relations, renderers
from rest_framework_jsonapi import encoders
from django.utils import encoding, six


class JsonApiMixin(object):
    encoder_class = encoders.JSONEncoder

    def determine_fields(self, data, renderer_context):
        fields = getattr(data, "fields", None)

        if fields is not None:
            return fields

        if isinstance(data, list) and data:
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

    def get_model_from_view(self, view):
        model = getattr(view, "model", None)

        if model is not None:
            return model

        queryset = getattr(view, "queryset", None)

        if queryset is not None:
            return queryset.model

        return None

    def get_resource_type(self, data, renderer_context):
        view = renderer_context.get("view", None)

        model = self.get_model_from_view(view)

        return six.text_type(model._meta.verbose_name_plural)

    def stringify_field_data(self, data, pk_field):
        if isinstance(data, list):
            return [self.stringify_field_data(item, pk_field) for item in data]

        item = data.copy()

        if pk_field in item:
            item[pk_field] = encoding.force_text(item[pk_field])

        return item

    def linkify_field_data(self, data, field_name):
        if isinstance(data, list):
            return [self.linkify_field_data(item, field_name) for item in data]

        item = data.copy()

        if field_name in item:
            if "links" not in item:
                item["links"] = {}

            item["links"][field_name] = item[field_name]
            del item[field_name]

        return item

    def link_format(self, field, link_name, request=None):
        from rest_framework.reverse import reverse

        test_pk = 999999

        model = field.queryset.model

        test_kwargs = {
            "pk": test_pk,
        }
        test_reverse = reverse(field.view_name, kwargs=test_kwargs, request=request)

        href = test_reverse.replace(encoding.force_text(test_pk), "{%s}" % link_name)

        return {
            "type": encoding.force_text(model._meta.verbose_name_plural),
            "href": href,
        }

    def url_to_pk(self, data, field_name, field):
        if isinstance(data, list):
            return [self.url_to_pk(item, field_name, field) for item in data]

        item = data.copy()

        if field_name in item:
            obj = field.from_native(item[field_name])
            print obj.pk

            item[field_name] = encoding.force_text(obj.pk)

        return item

    def render(self, data, accepted_media_type=None, renderer_context=None):
        wrapper = {}

        fields = self.determine_fields(
            data=data,
            renderer_context=renderer_context,
        )

        resource_type = self.get_resource_type(
            data=data,
            renderer_context=renderer_context,
        )

        resource_type = resource_type or "data"

        view = renderer_context.get("view", None)
        request = renderer_context.get("request", None)

        model = self.get_model_from_view(view)

        pk_field = encoding.force_text(model._meta.pk.name).encode("utf-8")

        data = self.stringify_field_data(data, pk_field)

        if data:
            for field_name, field in fields.iteritems():
                if isinstance(field, relations.PrimaryKeyRelatedField):
                    data = self.stringify_field_data(data, field_name)

                if isinstance(field, relations.HyperlinkedRelatedField):
                    data = self.url_to_pk(data, field_name, field)

                    if "links" not in wrapper:
                        wrapper["links"] = {}

                    link_name = "%s.%s" % (resource_type, field_name)

                    if link_name not in wrapper["links"]:
                        wrapper["links"][link_name] = self.link_format(field, link_name, request)

                if isinstance(field, relations.RelatedField):
                    data = self.linkify_field_data(data, field_name)

        wrapper[resource_type] = data

        return super(JsonApiMixin, self).render(
            data=wrapper,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )


class JsonApiRenderer(JsonApiMixin, renderers.JSONRenderer):
    pass
