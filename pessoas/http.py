from django.http import JsonResponse


class JsonResponseBadRequest(JsonResponse):
    status_code = 400


class JsonResponseNotFound(JsonResponse):
    status_code = 404


class JsonResponseUnprocessableEntity(JsonResponse):
    status_code = 422
