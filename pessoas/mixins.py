import codecs
import json
import types

from django.conf import settings

class ParseJSONMixin:
    """
    Adiciona o método request.json() ao objeto request
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        def _json(self):
            if not hasattr(self, '_json_cache'):
                if request.META.get('CONTENT_TYPE') == 'application/json':
                    encoding = settings.DEFAULT_CHARSET
                    stream = codecs.getreader(encoding)(self)
                    self._json_cache = json.load(stream)
                else:
                    self._json_cache = None
            return self._json_cache

        request.json = types.MethodType(_json, request)
