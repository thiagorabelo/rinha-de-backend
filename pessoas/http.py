import orjson

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    """
    Semelhante à django.http.JsonResponse, mas usa orjson.dumps()
    no lugar de json.dumps() para fazer a conversão do objeto para
    JSON.
    """
    def __init__(self, data, **kwargs):
        kwargs.setdefault("content_type", "application/json")
        data = orjson.dumps(data)
        super().__init__(content=data, **kwargs)


class JsonResponseBadRequest(JsonResponse):
    status_code = 400


class JsonResponseNotFound(JsonResponse):
    status_code = 404


class JsonResponseUnprocessableEntity(JsonResponse):
    status_code = 422
