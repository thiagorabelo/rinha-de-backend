from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .forms import PessoaForm
from .http import JsonResponseBadRequest, JsonResponseNotFound, \
                  JsonResponseUnprocessableEntity
from .mixins import ParseJSONMixin
from .models import Pessoa
from .utils import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached


# https://docs.djangoproject.com/en/4.2/topics/async/
@method_decorator(csrf_exempt, name="dispatch")
class PessoaView(ParseJSONMixin, View):

    async def _get_one(self, request, pk):
        try:
            pessoa_dict = await get_pessoa_dict_by_cache_or_db(pk)
            return JsonResponse(data=pessoa_dict)
        except Pessoa.DoesNotExist:
            return JsonResponseNotFound(data={"message": "Pessoa não encontrada"})

    async def _filter(self, request):
        if t := request.GET.get('t'):
            terms = t.split()
            ait = Pessoa.search_terms(*terms, as_dict=True)[:50].aiterator()
            return JsonResponse(
                data=[p async for p in ait],
                headers={"My-Host-Name": settings.MY_HOST_NAME},
                safe=False
            )
        return JsonResponseBadRequest(
            data={"message": """Busca inválida (Informe o termo de busca "t")"""}
        )

    async def get(self, request: HttpRequest, pessoa_pk=0):
        if pessoa_pk:
            return await self._get_one(request, pessoa_pk)
        return await self._filter(request)

    async def post(self, request: HttpRequest):
        try:
            form = PessoaForm(data=request.json())
            if form.is_valid():
                pessoa = form.instance

                if await has_pessoa_apelido_cached(pessoa):
                    return JsonResponseUnprocessableEntity(data={"message": "unique violation"})

                try:
                    pessoa = await form.asave()
                except IntegrityError:
                    return JsonResponseUnprocessableEntity(
                        data={"message": "o apelido já existe"}
                    )
                finally:
                    await set_pessoa_dict_cache(pessoa.pk, pessoa.to_dict())

                return JsonResponse(
                    data={"message": "criado"},
                    headers={"Location": pessoa.get_absolute_url()},
                    status=201
                )
            return JsonResponseUnprocessableEntity(
                data=form.errors
            )
        except AttributeError as ex:
            return JsonResponseBadRequest(
                data={"message": str(ex)}
            )


def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        status=200
    )
