import codecs
import json
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest

from .forms import PessoaForm
from .http import JsonResponseBadRequest, JsonResponseNotFound, \
                  JsonResponseUnprocessableEntity
from .utils import get_body_as_json
from .models import Pessoa
from .cache import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached


async def _pessoa_create(request: HttpRequest) -> HttpResponse:
    try:
        form = PessoaForm(data=get_body_as_json(request))
        if form.is_valid():
            pessoa = form.instance

            if await has_pessoa_apelido_cached(pessoa):
                return JsonResponseUnprocessableEntity(
                    data={"message": "O apelido já existe"},
                    headers={"My-Host-Name": settings.MY_HOST_NAME}
                )

            try:
                pessoa = await form.asave()
                await set_pessoa_dict_cache(pessoa.pk, pessoa.to_dict())
                return JsonResponse(
                    data={"message": "criado"},
                    headers={"Location": pessoa.get_absolute_url(),
                                "My-Host-Name": settings.MY_HOST_NAME},
                    status=201
                )
            except IntegrityError:
                return JsonResponseUnprocessableEntity(
                    data={"message": "unique violation"},
                    headers={"My-Host-Name": settings.MY_HOST_NAME}
                )
        return JsonResponseUnprocessableEntity(
            data=form.errors,
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )
    except AttributeError as ex:
        return JsonResponseBadRequest(
            data={"message": str(ex)},
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )


async def _pessoa_list(request: HttpRequest) -> HttpResponse:
    term = request.GET.get("t")
    if not term:
        return JsonResponseBadRequest(
            data={"message": """Busca inválida (Informe o termo de busca "t")"""}
        )

    terms = term.split()
    ait = Pessoa.search_terms2(*terms, as_dict=True)[:50].aiterator()
    return JsonResponse(
        data=[p async for p in ait],
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        safe=False
    )


async def pessoa_create_or_list(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return await _pessoa_create(request)
    elif request.method == "GET":
        return await _pessoa_list(request)
    return JsonResponse(
        content={"message": "Not Allowed"},
        status=405,
    )


async def pessoa_get(request: HttpRequest, pk: uuid.UUID = None) -> HttpResponse:
    try:
        pessoa_dict = await get_pessoa_dict_by_cache_or_db(pk)
        return JsonResponse(
            data=pessoa_dict,
            headers={"My-Host-Name": settings.MY_HOST_NAME}
        )
    except Pessoa.DoesNotExist:
        return JsonResponseNotFound(data={"message": "Pessoa não encontrada"})


async def contagem_pessoas(request):
    total = await Pessoa.objects.all().acount()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )
