import gevent
import logging
import uuid

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from pydantic import ValidationError

from .http import JsonResponse, JsonResponseUnprocessableEntity, \
                  JsonResponseBadRequest, JsonResponseNotFound
from .utils import get_body_as_json
from .models import Pessoa
from .cache import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached

from .models import Pessoa
from .queue import init_workers  # insert_worker, Queue, QueueCycle  # insert_task
from .schemas import PessoaSchema


queues_cycle = init_workers()


def _pessoa_create(request: HttpRequest) -> HttpResponse:
    try:
        schema = PessoaSchema(**get_body_as_json(request))

        if has_pessoa_apelido_cached(schema.apelido):
            return JsonResponseUnprocessableEntity(
                data={"message": "O apelido já existe"},
                headers={"My-Host-Name": settings.MY_HOST_NAME}
            )

        result = schema.model_dump()
        # pessoa = form.save()
        # insert_task.put(pessoa.to_dict(pk=True), block=True)
        # insert_task.put_nowait(result)
        queues_cycle.get().put_nowait(result)
        set_pessoa_dict_cache(schema.id, result)
        return JsonResponse(
            data={"message": "criado"},
            headers={"Location": Pessoa.get_absolute_url(schema),  # Gambiarra, mas funciona!
                     "My-Host-Name": settings.MY_HOST_NAME},
            status=201
        )
    except ValidationError as ex:
        return JsonResponseUnprocessableEntity(
            data=ex.json(),
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )
    except Exception as ex:
        logging.error(ex)
        return JsonResponseBadRequest(
            data={"message": str(ex)},
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )


def _pessoa_list(request: HttpRequest) -> HttpResponse:
    term = request.GET.get("t")
    if not term:
        return JsonResponseBadRequest(
            data={"message": """Busca inválida (Informe o termo de busca "t")"""}
        )

    terms = term.split()
    qs = Pessoa.search_terms(*terms, as_dict=True)[:50]
    return JsonResponse(
        data=list(qs),
        headers={"My-Host-Name": settings.MY_HOST_NAME},
    )


def pessoa_create_or_list(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return _pessoa_create(request)
    elif request.method == "GET":
        return _pessoa_list(request)
    return JsonResponse(
        content={"message": "Not Allowed"},
        status=405,
    )


def pessoa_get(request: HttpRequest, pk: uuid.UUID = None) -> HttpResponse:
    try:
        pessoa_dict = get_pessoa_dict_by_cache_or_db(pk)
        return JsonResponse(
            data=pessoa_dict,
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )
    except Pessoa.DoesNotExist:
        return JsonResponseNotFound(data={"message": "Pessoa não encontrada"})


def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )


def gevent_loop(request):
    import gevent
    loop = gevent.config.loop

    return HttpResponse(
        content=f"{loop.__module__}.{loop.__name__}".encode("utf-8"),
        content_type="text/plain",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )
