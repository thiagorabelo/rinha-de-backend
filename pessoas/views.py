from django.conf import settings
from django.http import HttpResponse
from django.db import IntegrityError
from django.http import HttpResponse
from uuid import UUID

from ninja import NinjaAPI

from .models import Pessoa
from .cache import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached
from .schemas import PessoaSchema, CreatedResponseSchema, ErrorResponseSchema


api = NinjaAPI(title="Rinha de Backend")


@api.post("/pessoas", response={201: CreatedResponseSchema, 422: ErrorResponseSchema})
def create_pessoa(request, payload: PessoaSchema, response: HttpResponse):
    # response.headers["My-Host-Name"] = settings.MY_HOST_NAME

    if has_pessoa_apelido_cached(payload):
        return 422, {"message": "O apelido já existe"}

    try:
        pessoa = Pessoa(**payload.dict())
        pessoa.save()
        response.headers["Location"] = pessoa.get_absolute_url()
        set_pessoa_dict_cache(pessoa.pk, payload.dict())
        return 201, {"message": "Criado"}
    except IntegrityError:
        return 422, {"message": "Unique violation"}


@api.get("/pessoas/{uuid:pessoa_pk}", response={200: PessoaSchema, 404: ErrorResponseSchema})
def get_pessoa(request, pessoa_pk: UUID):  # , response: HttpResponse):
    try:
        pessoa_dict = get_pessoa_dict_by_cache_or_db(pessoa_pk)
        # response.headers["My-Host-Name"] = settings.MY_HOST_NAME
        return 200, pessoa_dict
    except Pessoa.DoesNotExist:
        return 404, {"message": "Pessoa não encontrada"}


@api.get("/pessoas", response={200: list[PessoaSchema], 400: ErrorResponseSchema})
def find_pessoa(request, t: str = ""):  # , response: HttpResponse):
    if not t:
        return 400, {"message": """Busca inválida (Informe o termo de busca "t")"""}

    terms = t.split()
    qs = Pessoa.search_terms(*terms, as_dict=True)[:50]
    # response.headers["My-Host-Name"] = settings.MY_HOST_NAME
    return 200, qs


@api.get("/contagem-pessoas")
def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return total
