from django.utils.encoding import force_bytes
import json


def dump_json(data):
    return force_bytes(json.dumps(data, sort_keys=True, indent=4))
