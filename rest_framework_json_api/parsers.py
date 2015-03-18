from rest_framework import parsers, relations
from rest_framework_json_api.utils import (
    get_related_field, is_related_many,
    model_from_obj, model_to_resource_type
)
from django.utils import six


class JsonApiMixin(object):
    media_type = 'application/vnd.api+json'

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JsonApiMixin, self).parse(stream, media_type=media_type,
                                               parser_context=parser_context)

        view = parser_context.get("view", None)

        model = self.model_from_obj(view)
        resource_type = self.model_to_resource_type(model)

        resource = {}

        if "data" in data:
            resource = data["data"]

        if isinstance(resource, list):
            resource = [self.convert_resource(r, view) for r in resource]
        else:
            resource = self.convert_resource(resource, view)

        return resource

    def convert_resource(self, resource, view):
        serializer_data = view.get_serializer(instance=None)
        fields = serializer_data.fields

        links = {}

        if "links" in resource:
            links = resource["links"]

            del resource["links"]

        for field_name, field in six.iteritems(fields):
            if field_name not in links:
                continue

            related_field = get_related_field(field)

            if isinstance(related_field, relations.HyperlinkedRelatedField):
                if is_related_many(field):
                    pks = links[field_name]
                    model = related_field.queryset.model

                    resource[field_name] = []

                    for pk in pks:
                        obj = model(pk=pk)

                        try:
                            url = related_field.to_representation(obj)
                        except AttributeError:
                            url = related_field.to_native(obj)

                        resource[field_name].append(url)
                else:
                    pk = links[field_name]
                    model = related_field.queryset.model

                    obj = model(pk=pk)

                    try:
                        url = related_field.to_representation(obj)
                    except AttributeError:
                        url = related_field.to_native(obj)

                    resource[field_name] = url
            else:
                resource[field_name] = links[field_name]

        return resource

    def model_from_obj(self, obj):
        return model_from_obj(obj)

    def model_to_resource_type(self, model):
        return model_to_resource_type(model)


class JsonApiParser(JsonApiMixin, parsers.JSONParser):
    pass
