import asyncio

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.views import View

from ninja import NinjaAPI

from .forms import PessoaForm
from .http import JsonResponseBadRequest, JsonResponseNotFound
from .models import Pessoa
from .cache import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached
from .schemas import PessoaSchema, CreatedResponseSchema, UnprocessableEntityResponseSchema


api = NinjaAPI(title="Rinha de Backend")


@api.post("", response={200: CreatedResponseSchema, 422: UnprocessableEntityResponseSchema})
def create_pessoa(request, payload: PessoaSchema, response: HttpResponse):
    response.headers["My-Host-Name"] = settings.MY_HOST_NAME

    if has_pessoa_apelido_cached(payload):
        return 422, {"message": "O apelido já existe"}

    try:
        pessoa = Pessoa(**payload.dict())
        pessoa.save()
        response.headers["Location"] = pessoa.get_absolute_url()
        set_pessoa_dict_cache(pessoa.pk, payload.dict())
        return 200, {"message": "Criado"}
    except IntegrityError:
        return 422, {"message": "Unique violation"}


class PessoaView(View):

    def _get_one(self, request, pk):
        try:
            pessoa_dict = get_pessoa_dict_by_cache_or_db(pk)
            return JsonResponse(
                data=pessoa_dict,
                headers={"My-Host-Name": settings.MY_HOST_NAME}
            )
        except Pessoa.DoesNotExist:
            return JsonResponseNotFound(data={"message": "Pessoa não encontrada"})

    def _filter(self, request):
        if t := request.GET.get('t'):
            terms = t.split()
            qs = Pessoa.search_terms(*terms, as_dict=True)[:50]
            return JsonResponse(
                data=[p for p in qs],
                headers={"My-Host-Name": settings.MY_HOST_NAME},
                safe=False
            )
        return JsonResponseBadRequest(
            data={"message": """Busca inválida (Informe o termo de busca "t")"""}
        )

    def get(self, request: HttpRequest, pessoa_pk=0):
        if pessoa_pk:
            return self._get_one(request, pessoa_pk)
        return self._filter(request)


def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )
