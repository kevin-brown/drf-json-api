from rest_framework import relations, renderers, serializers, status
from rest_framework.settings import api_settings
from rest_framework_json_api import encoders
from rest_framework_json_api.utils import (
    get_related_field, is_related_many,
    model_from_obj, model_to_resource_type
)
from django.core import urlresolvers
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils import encoding, six
from django.utils.six.moves.urllib.parse import urlparse, urlunparse


class WrapperNotApplicable(ValueError):

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)
        self.renderer_context = kwargs.pop('renderer_context', None)

        return super(WrapperNotApplicable, self).__init__(*args, **kwargs)


class JsonApiMixin(object):
    convert_by_name = {
        'id': 'convert_to_text',
        api_settings.URL_FIELD_NAME: 'rename_to_href',
    }

    convert_by_type = {
        relations.PrimaryKeyRelatedField: 'handle_related_field',
        relations.HyperlinkedRelatedField: 'handle_url_field',
        serializers.ModelSerializer: 'handle_nested_serializer',
    }
    dict_class = dict
    encoder_class = encoders.JSONEncoder
    media_type = 'application/vnd.api+json'
    wrappers = [
        'wrap_empty_response',
        'wrap_parser_error',
        'wrap_field_error',
        'wrap_generic_error',
        'wrap_options',
        'wrap_paginated',
        'wrap_default'
    ]

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Convert native data to JSON API

        Tries each of the methods in `wrappers`, using the first successful
        one, or raises `WrapperNotApplicable`.
        """

        wrapper = None
        success = False

        for wrapper_name in self.wrappers:
            wrapper_method = getattr(self, wrapper_name)
            try:
                wrapper = wrapper_method(data, renderer_context)
            except WrapperNotApplicable:
                pass
            else:
                success = True
                break

        if not success:
            raise WrapperNotApplicable(
                'No acceptable wrappers found for response.',
                data=data, renderer_context=renderer_context)

        renderer_context["indent"] = 4

        return super(JsonApiMixin, self).render(
            data=wrapper,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context)

    def wrap_empty_response(self, data, renderer_context):
        """
        Pass-through empty responses

        204 No Content includes an empty response
        """

        if data is not None:
            raise WrapperNotApplicable('Data must be empty.')

        return data

    def wrap_parser_error(self, data, renderer_context):
        """
        Convert parser errors to the JSON API Error format

        Parser errors have a status code of 400, like field errors, but have
        the same native format as generic errors.  Also, the detail message is
        often specific to the input, so the error is listed as a 'detail'
        rather than a 'title'.
        """

        response = renderer_context.get("response", None)
        status_code = response and response.status_code

        if status_code != 400:
            raise WrapperNotApplicable('Status code must be 400.')

        if list(data.keys()) != ['detail']:
            raise WrapperNotApplicable('Data must only have "detail" key.')

        # Probably a parser error, unless `detail` is a valid field
        view = renderer_context.get("view", None)
        model = self.model_from_obj(view)

        if 'detail' in model._meta.get_all_field_names():
            raise WrapperNotApplicable()

        return self.wrap_error(
            data, renderer_context, keys_are_fields=False,
            issue_is_title=False)

    def wrap_field_error(self, data, renderer_context):
        """
        Convert field error native data to the JSON API Error format

        See the note about the JSON API Error format on `wrap_error`.

        The native format for field errors is a dictionary where the keys are
        field names (or 'non_field_errors' for additional errors) and the
        values are a list of error strings:

        {
            "min": [
                "min must be greater than 0.",
                "min must be an even number."
            ],
            "max": ["max must be a positive number."],
            "non_field_errors": [
                "Select either a range or an enumeration, not both."]
        }

        It is rendered into this JSON API error format:

        {
            "errors": [{
                "status": "400",
                "path": "/min",
                "detail": "min must be greater than 0."
            },{
                "status": "400",
                "path": "/min",
                "detail": "min must be an even number."
            },{
                "status": "400",
                "path": "/max",
                "detail": "max must be a positive number."
            },{
                "status": "400",
                "path": "/-",
                "detail": "Select either a range or an enumeration, not both."
            }]
        }
        """
        response = renderer_context.get("response", None)
        status_code = response and response.status_code
        if status_code != 400:
            raise WrapperNotApplicable('Status code must be 400.')

        return self.wrap_error(
            data, renderer_context, keys_are_fields=True, issue_is_title=False)

    def wrap_generic_error(self, data, renderer_context):
        """
        Convert generic error native data using the JSON API Error format

        See the note about the JSON API Error format on `wrap_error`.

        The native format for errors that are not bad requests, such as
        authentication issues or missing content, is a dictionary with a
        'detail' key and a string value:

        {
            "detail": "Authentication credentials were not provided."
        }

        This is rendered into this JSON API error format:

        {
            "errors": [{
                "status": "403",
                "title": "Authentication credentials were not provided"
            }]
        }
        """
        response = renderer_context.get("response", None)
        status_code = response and response.status_code
        is_error = (
            status.is_client_error(status_code) or
            status.is_server_error(status_code)
        )
        if not is_error:
            raise WrapperNotApplicable("Status code must be 4xx or 5xx.")

        return self.wrap_error(
            data, renderer_context, keys_are_fields=False, issue_is_title=True)

    def wrap_error(
            self, data, renderer_context, keys_are_fields, issue_is_title):
        """Convert error native data to the JSON API Error format

        JSON API has a different format for errors, but Django REST Framework
        doesn't have a separate rendering path for errors.  This results in
        some guesswork to determine if data is an error, what kind, and how
        to handle it.

        As of August 2014, there is not a consensus about the error format in
        JSON API.  The format documentation defines an "errors" collection, and
        some possible fields for that collection, but without examples for
        common cases.  If and when consensus is reached, this format will
        probably change.
        """

        response = renderer_context.get("response", None)
        status_code = str(response and response.status_code)

        errors = []
        for field, issues in data.items():
            if isinstance(issues, six.string_types):
                issues = [issues]
            for issue in issues:
                error = self.dict_class()
                error["status"] = status_code

                if issue_is_title:
                    error["title"] = issue
                else:
                    error["detail"] = issue

                if keys_are_fields:
                    if field in ('non_field_errors', NON_FIELD_ERRORS):
                        error["path"] = '/-'
                    else:
                        error["path"] = '/' + field

                errors.append(error)
        wrapper = self.dict_class()
        wrapper["errors"] = errors
        return wrapper

    def wrap_options(self, data, renderer_context):
        '''Wrap OPTIONS data as JSON API meta value'''
        request = renderer_context.get("request", None)
        method = request and getattr(request, 'method')
        if method != 'OPTIONS':
            raise WrapperNotApplicable("Request method must be OPTIONS")

        wrapper = self.dict_class()
        wrapper["meta"] = data
        return wrapper

    def wrap_paginated(self, data, renderer_context):
        """Convert paginated data to JSON API with meta"""

        pagination_keys = ['count', 'next', 'previous', 'results']
        for key in pagination_keys:
            if not (data and key in data):
                raise WrapperNotApplicable('Not paginated results')

        view = renderer_context.get("view", None)
        model = self.model_from_obj(view)
        resource_type = self.model_to_resource_type(model)

        try:
            from rest_framework.utils.serializer_helpers import ReturnList

            results = ReturnList(
                data["results"],
                serializer=data.serializer.fields["results"],
            )
        except ImportError:
            results = data["results"]

        # Use default wrapper for results
        wrapper = self.wrap_default(results, renderer_context)

        # Add pagination metadata
        pagination = self.dict_class()

        pagination['previous'] = data['previous']
        pagination['next'] = data['next']
        pagination['count'] = data['count']

        wrapper.setdefault('meta', self.dict_class())

        wrapper['meta'].setdefault('pagination', self.dict_class())
        wrapper['meta']['pagination'].setdefault(
            resource_type, self.dict_class()).update(pagination)

        return wrapper

    def wrap_default(self, data, renderer_context):
        """Convert native data to a JSON API resource collection

        This wrapper expects a standard DRF data object (a dict-like
        object with a `fields` dict-like attribute), or a list of
        such data objects.
        """

        wrapper = self.dict_class()
        view = renderer_context.get("view", None)
        request = renderer_context.get("request", None)

        model = self.model_from_obj(view)
        resource_type = self.model_to_resource_type(model)

        if isinstance(data, list):
            many = True
            resources = data
        else:
            many = False
            resources = [data]

        items = []
        links = self.dict_class()
        linked = self.dict_class()
        meta = self.dict_class()

        for resource in resources:
            converted = self.convert_resource(resource, data, request)
            item = converted.get('data', {})
            linked_ids = converted.get('linked_ids', {})
            if linked_ids:
                item["links"] = linked_ids
            items.append(item)

            links.update(converted.get('links', {}))
            linked.update(converted.get('linked', {}))
            meta.update(converted.get('meta', {}))

        if many:
            wrapper[resource_type] = items
        else:
            wrapper[resource_type] = items[0]

        if links:
            links = self.prepend_links_with_name(links, resource_type)
            wrapper["links"] = links

        if linked:
            wrapper["linked"] = linked

        if meta:
            wrapper["meta"] = meta

        return wrapper

    def convert_resource(self, resource, data, request):
        fields = self.fields_from_resource(resource, data)

        if not fields:
            raise WrapperNotApplicable('Items must have a fields attribute.')

        data = self.dict_class()
        linked_ids = self.dict_class()
        links = self.dict_class()
        linked = self.dict_class()
        meta = self.dict_class()

        for field_name, field in six.iteritems(fields):
            converted = None

            if field_name in self.convert_by_name:
                converter_name = self.convert_by_name[field_name]
                converter = getattr(self, converter_name)
                converted = converter(resource, field, field_name, request)
            else:
                related_field = get_related_field(field)

                for field_type, converter_name in \
                        six.iteritems(self.convert_by_type):
                    if isinstance(related_field, field_type):
                        converter = getattr(self, converter_name)
                        converted = converter(
                            resource, field, field_name, request)
                        break

            if converted:
                data.update(converted.pop("data", {}))
                linked_ids.update(converted.pop("linked_ids", {}))
                links.update(converted.get("links", {}))
                linked.update(converted.get("linked", {}))
                meta.update(converted.get("meta", {}))
            else:
                data[field_name] = resource[field_name]

        return {
            'data': data,
            'linked_ids': linked_ids,
            'links': links,
            'linked': linked,
            'meta': meta,
        }

    def convert_to_text(self, resource, field, field_name, request):
        data = self.dict_class()
        data[field_name] = encoding.force_text(resource[field_name])
        return {"data": data}

    def rename_to_href(self, resource, field, field_name, request):
        data = self.dict_class()
        data['href'] = resource[field_name]
        return {"data": data}

    def prepend_links_with_name(self, links, name):
        changed_links = links.copy()

        for link_name, link_obj in six.iteritems(links):
            prepended_name = "%s.%s" % (name, link_name)
            link_template = "{%s}" % link_name
            prepended_template = "{%s}" % prepended_name

            updated_obj = changed_links[link_name]

            if "href" in link_obj:
                updated_obj["href"] = link_obj["href"].replace(
                    link_template, prepended_template)

            changed_links[prepended_name] = changed_links[link_name]
            del changed_links[link_name]

        return changed_links

    def handle_nested_serializer(self, resource, field, field_name, request):
        serializer_field = get_related_field(field)

        if hasattr(serializer_field, "opts"):
            model = serializer_field.opts.model
        else:
            model = serializer_field.Meta.model

        resource_type = self.model_to_resource_type(model)

        linked_ids = self.dict_class()
        links = self.dict_class()
        linked = self.dict_class()
        linked[resource_type] = []

        if is_related_many(field):
            items = resource[field_name]
        else:
            items = [resource[field_name]]

        obj_ids = []

        resource.serializer = serializer_field

        for item in items:
            converted = self.convert_resource(item, resource, request)
            linked_obj = converted["data"]
            linked_ids = converted.pop("linked_ids", {})

            if linked_ids:
                linked_obj["links"] = linked_ids

            obj_ids.append(converted["data"]["id"])

            field_links = self.prepend_links_with_name(
                converted.get("links", {}), resource_type)


            field_links[field_name] = {
                "type": resource_type,
            }

            if "href" in converted["data"]:
                url_field = serializer_field.fields[api_settings.URL_FIELD_NAME]

                field_links[field_name]["href"] = self.url_to_template(
                    url_field.view_name, request, field_name,
                )

            links.update(field_links)

            linked[resource_type].append(linked_obj)

        if is_related_many(field):
            linked_ids[field_name] = obj_ids
        else:
            linked_ids[field_name] = obj_ids[0]

        return {"linked_ids": linked_ids, "links": links, "linked": linked}

    def handle_related_field(self, resource, field, field_name, request):
        links = self.dict_class()
        linked_ids = self.dict_class()

        related_field = get_related_field(field)

        model = self.model_from_obj(related_field)
        resource_type = self.model_to_resource_type(model)

        if field_name in resource:
            links[field_name] = {
                "type": resource_type,
            }

            if is_related_many(field):
                link_data = [
                    encoding.force_text(pk) for pk in resource[field_name]]
            elif resource[field_name]:
                link_data = encoding.force_text(resource[field_name])
            else:
                link_data = None

            linked_ids[field_name] = link_data

        return {"linked_ids": linked_ids, "links": links}

    def handle_url_field(self, resource, field, field_name, request):
        links = self.dict_class()
        linked_ids = self.dict_class()

        related_field = get_related_field(field)

        model = self.model_from_obj(related_field)
        resource_type = self.model_to_resource_type(model)

        links[field_name] = {
            "href": self.url_to_template(related_field.view_name, request, field_name),
            "type": resource_type,
        }

        if field_name in resource:
            linked_ids[field_name] = self.url_to_pk(
                resource[field_name], field)

        return {"linked_ids": linked_ids, "links": links}

    def url_to_pk(self, url_data, field):
        if is_related_many(field):
            try:
                obj_list = field.to_internal_value(url_data)
            except AttributeError:
                obj_list = [field.from_native(url) for url in url_data]

            return [encoding.force_text(obj.pk) for obj in obj_list]

        if url_data:
            try:
                obj = field.to_internal_value(url_data)
            except AttributeError:
                obj = field.from_native(url_data)

            return encoding.force_text(obj.pk)
        else:
            return None

    def url_to_template(self, view_name, request, template_name):
        resolver = urlresolvers.get_resolver(None)
        info = resolver.reverse_dict[view_name]

        path_template = info[0][0][0]
        # FIXME: what happens when URL has more than one dynamic values?
        # e.g. nested relations: manufacturer/%(id)s/cars/%(card_id)s
        path = path_template % {info[0][0][1][0]: '{%s}' % template_name}

        parsed_url = urlparse(request.build_absolute_uri())

        return urlunparse(
            [parsed_url.scheme, parsed_url.netloc, path, '', '', '']
        )

    def fields_from_resource(self, resource, data):
        if hasattr(data, "serializer"):
            resource = data.serializer

            if hasattr(resource, "child"):
                resource = resource.child

        return getattr(resource, "fields", None)

    def model_to_resource_type(self, model):
        return model_to_resource_type(model)

    def model_from_obj(self, obj):
        return model_from_obj(obj)


class JsonApiRenderer(JsonApiMixin, renderers.JSONRenderer):
    pass
