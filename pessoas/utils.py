import codecs
import json
import types

from django.conf import settings


def get_body_as_json(request):
    """
    Adiciona o método request.json() ao objeto request
    """
    if not hasattr(request, '_json_cache'):
        if request.META.get('CONTENT_TYPE') == 'application/json':
            encoding = settings.DEFAULT_CHARSET
            stream = codecs.getreader(encoding)(request)
            request._json_cache = json.load(stream)
        else:
            request._json_cache = None
    return request._json_cache
