from rest_framework import relations, renderers, serializers, status
from rest_framework_json_api import encoders
from rest_framework_json_api.utils import (
    model_from_obj, model_to_resource_type
)
from django.utils import encoding, six


def convert_resource(resource, request):
    from rest_framework.settings import api_settings

    links = {}
    linked = {}
    data = resource.copy()

    fields = fields_from_resource(resource)

    if "id" in fields:
        data["id"] = encoding.force_text(data["id"])

    url_field_name = api_settings.URL_FIELD_NAME

    if url_field_name in fields:
        data["href"] = data[url_field_name]
        del data[url_field_name]

    for field_name, field in six.iteritems(fields):
        if isinstance(field, relations.PrimaryKeyRelatedField):
            data, field_links, field_linked = handle_related_field(
                data, field, field_name, request)

            links.update(field_links)
            linked.update(field_linked)

        if isinstance(field, relations.HyperlinkedRelatedField):
            data, field_links, field_linked = handle_url_field(
                data, field, field_name, request)

            links.update(field_links)
            linked.update(field_linked)

        if isinstance(field, serializers.ModelSerializer):
            data, field_links, field_linked = handle_nested_serializer(
                data, field, field_name, request)

            links.update(field_links)
            linked.update(field_linked)

    return (data, links, linked)


def prepend_links_with_name(links, name):
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


def handle_nested_serializer(resource, field, field_name, request):
    links = {}
    linked = {}
    data = resource.copy()

    model = field.opts.model

    resource_type = model_to_resource_type(model)

    if field.many:
        obj_ids = []

        for item in data[field_name]:
            linked_obj, field_links, field_linked = convert_resource(
                item, request)

            obj_ids.append(linked_obj["id"])

            field_links = prepend_links_with_name(
                field_links, resource_type)

            if hasattr(field.opts, "view_name"):
                field_links[field_name] = {
                    "href": url_to_template(
                        field.opts.view_name, request, field_name),
                    "type": resource_type,
                }

            links.update(field_links)

            if resource_type not in linked:
                linked[resource_type] = []

            linked[resource_type].append(linked_obj)

        if "links" not in data:
            data["links"] = {}

        data["links"][field_name] = obj_ids
        del data[field_name]
    else:
        item = data[field_name]
        linked_obj, field_links, field_linked = convert_resource(item, request)

        field_links = prepend_links_with_name(field_links, resource_type)

        if hasattr(field.opts, "view_name"):
            field_links[field_name] = {
                "href": url_to_template(
                    field.opts.view_name, request, field_name),
                "type": resource_type,
            }

        links.update(field_links)

        if resource_type not in linked:
            linked[resource_type] = []

        linked[resource_type].append(linked_obj)

        if "links" not in data:
            data["links"] = {}

        data["links"][field_name] = linked_obj["id"]

        del data[field_name]

    return data, links, linked


def handle_related_field(resource, field, field_name, request):
    links = {}
    linked = {}
    data = resource.copy()

    model = model_from_obj(field)
    resource_type = model_to_resource_type(model)

    if field_name in data:
        if "links" not in data:
            data["links"] = {}

        links[field_name] = {
            "type": resource_type,
        }

        data["links"][field_name] = encoding.force_text(data[field_name])
        del data[field_name]

    return data, links, linked


def handle_url_field(resource, field, field_name, request):
    links = {}
    linked = {}
    data = resource.copy()

    model = model_from_obj(field)
    resource_type = model_to_resource_type(model)

    links[field_name] = {
        "href": url_to_template(field.view_name, request, field_name),
        "type": resource_type,
    }

    if field_name in data:
        if "links" not in data:
            data["links"] = {}

        data["links"][field_name] = url_to_pk(data[field_name], field)
        del data[field_name]

    return (data, links, linked)


def url_to_pk(url_data, field):
    if field.many:
        obj_list = [field.from_native(url) for url in url_data]
        return [encoding.force_text(obj.pk) for obj in obj_list]

    obj = field.from_native(url_data)
    return encoding.force_text(obj.pk)


def url_to_template(view_name, request, template_name):
    from rest_framework.reverse import reverse

    test_pk = 999999

    test_kwargs = {
        "pk": test_pk,
    }
    test_reverse = reverse(view_name, kwargs=test_kwargs, request=request)

    href = test_reverse.replace(
        encoding.force_text(test_pk), "{%s}" % template_name)

    return href


def fields_from_resource(resource):
    fields = getattr(resource, "fields", None)

    if fields is not None:
        return fields

    return None


class JsonApiMixin(object):
    encoder_class = encoders.JSONEncoder
    media_type = 'application/vnd.api+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Convert native data to JSON API

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
        status_code = response and response.status_code
        is_error = (
            status.is_client_error(status_code) or
            status.is_server_error(status_code))

        if status_code == 400 and data.keys() == ['detail']:
            # Probably a parser error, but might be a field error
            view = renderer_context.get("view", None)
            model = model_from_obj(view)
            if 'detail' in model._meta.get_all_field_names():
                wrapper = self.wrap_field_error(data, renderer_context)
            else:
                wrapper = self.wrap_parser_error(data, renderer_context)
        elif status_code == 400:
            wrapper = self.wrap_field_error(data, renderer_context)
        elif is_error:
            wrapper = self.wrap_generic_error(data, renderer_context)
        else:
            wrapper = self.wrap_default(data, renderer_context)

        renderer_context["indent"] = 4
        return super(JsonApiMixin, self).render(
            data=wrapper,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context,
        )

    def wrap_default(self, data, renderer_context):
        """Convert native data to a JSON API resource collection"""
        wrapper = {}
        view = renderer_context.get("view", None)
        request = renderer_context.get("request", None)

        model = model_from_obj(view)
        resource_type = model_to_resource_type(model)

        links = {}
        linked = {}
        item = {}

        if isinstance(data, list):
            links = {}
            linked = {}
            items = []

            for resource in data:
                converted_item, resource_links, resource_linked = \
                    convert_resource(resource, request)

                items.append(converted_item)
                links.update(resource_links)
                linked.update(resource_linked)

            item = items
        else:
            item, links, linked = convert_resource(data, request)

        wrapper[resource_type] = item

        if links:
            links = prepend_links_with_name(links, resource_type)

            wrapper["links"] = links

        if linked:
            wrapper["linked"] = linked

        return wrapper

    def wrap_field_error(self, data, renderer_context):
        """
        Convert field error native data to the JSON API Error format

        See the note about the JSON API Error format on render.

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
        return self.wrap_error(
            data, renderer_context, keys_are_fields=True, issue_is_title=False)

    def wrap_generic_error(self, data, renderer_context):
        """
        Convert generic error native data using the JSON API Error format

        See the note about the JSON API Error format on render.

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
        return self.wrap_error(
            data, renderer_context, keys_are_fields=False, issue_is_title=True)

    def wrap_parser_error(self, data, renderer_context):
        """
        Convert parser errors to the JSON API Error format

        See the note about the JSON API Error format on render.

        Parser errors have a status code of 400, like field errors, but have
        the same native format as generic errors.  Also, the detail message is
        often specific to the input, so the error is listed as a 'detail'
        rather than a 'title'.
        """
        return self.wrap_error(
            data, renderer_context, keys_are_fields=False,
            issue_is_title=False)

    def wrap_error(
            self, data, renderer_context, keys_are_fields, issue_is_title):
        """Convert error native data to the JSON API Error format"""

        response = renderer_context.get("response", None)
        status_code = str(response and response.status_code)

        errors = []
        for field, issues in data.items():
            if isinstance(issues, six.string_types):
                issues = [issues]
            for issue in issues:
                error = {"status": status_code}

                if issue_is_title:
                    error["title"] = issue
                else:
                    error["detail"] = issue

                if keys_are_fields:
                    if field == 'non_field_errors':
                        error["path"] = '/-'
                    else:
                        error["path"] = '/' + field

                errors.append(error)
        return {"errors": errors}


class JsonApiRenderer(JsonApiMixin, renderers.JSONRenderer):
    pass
