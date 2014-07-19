from rest_framework.utils import encoders


class SortedKeys(object):
    """
    Enable the `sort_keys` flag by default, which will cause the JSON keys to be
    sorted by default.  While this is not the default, and JSON objects are not
    ordered, it makes testing a bit easier.
    """

    def __init__(self, *args, **kwargs):
        kwargs["sort_keys"] = True

        super(SortedKeys, self).__init__(*args, **kwargs)


class JSONEncoder(SortedKeys, encoders.JSONEncoder):
    pass
