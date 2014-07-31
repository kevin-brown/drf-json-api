from rest_framework import parsers
from rest_framework_json_api.utils import (
    model_from_obj, model_to_resource_type
)


class JsonApiMixin(object):
    media_type = 'application/vnd.api+json'

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JsonApiMixin, self).parse(stream, media_type=media_type,
                                               parser_context=parser_context)

        view = parser_context.get("view", None)

        model = model_from_obj(view)
        resource_type = model_to_resource_type(model)

        # links = {}
        # linked = {}
        resource = {}

        if resource_type in data:
            resource = data[resource_type]

        return resource


class JsonApiParser(JsonApiMixin, parsers.JSONParser):
    pass
