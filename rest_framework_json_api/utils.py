from django.utils import encoding


def model_from_obj(obj):
    model = getattr(obj, "model", None)

    if model is not None:
        return model

    queryset = getattr(obj, "queryset", None)

    if queryset is not None:
        return queryset.model

    return None


def model_to_resource_type(model):
    if model is None:
        return "data"

    return encoding.force_text(model._meta.verbose_name_plural)
