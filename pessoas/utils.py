import orjson as json
import sys

# from django.conf import settings


def get_body_as_json(request):
    if request.META.get("CONTENT_TYPE") == "application/json":
        return json.loads(request.read())
    raise ValueError(f"Content-Type is {request.META.get('CONTENT_TYPE')}")


_outfile = sys.__stderr__


def Print(*args, file=None, **kwargs):
    if file is None:
       file = _outfile
    print(*args, file=file, **kwargs)
