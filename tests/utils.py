from django.utils.encoding import force_bytes, force_text
import json


def dump_json(data):
    import rest_framework

    version = rest_framework.__version__.split(".")

    json_kwargs = {
        "sort_keys": True,
        "indent": 4,
    }

    if version[0] >= "3":
        json_kwargs["separators"] = (", ", ": ", )

    return force_bytes(json.dumps(data, **json_kwargs))


def parse_json(data):
    return json.loads(force_text(data))
