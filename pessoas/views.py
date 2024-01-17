import codecs
import json
import types

from asgiref.sync import sync_to_async

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Pessoa
from .forms import PessoaForm


class JsonResponseBadRequest(JsonResponse):
    status_code = 400


class JsonResponseNotFound(JsonResponse):
    status_code = 404


class JsonResponseUnprocessableEntity(JsonResponse):
    status_code = 422


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


# https://docs.djangoproject.com/en/4.2/topics/async/
@method_decorator(csrf_exempt, name="dispatch")
class PessoaView(ParseJSONMixin, View):

    async def _get_one(self, request, pk):
        if pessoa := await cache.aget(f"pessoa:{pk}"):
            return JsonResponse(data=pessoa)

        try:
            pessoa_dict = await Pessoa.aget_as_dict(pk=pk)

            await cache.aset(f"pessoa:{pk}", pessoa_dict)
            await cache.aset(f"pessoa:apelido:{pessoa_dict['apelido']}", "1")

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

                if await cache.aget(f"pessoa:apelido:{pessoa.apelido}"):
                    return JsonResponseUnprocessableEntity(data={"message": "unique violation"})

                pessoa = await sync_to_async(form.save)()

                await cache.aset(f"pessoa:{pessoa.id}", pessoa.to_dict())
                await cache.aset(f"pessoa:apelido:{pessoa.apelido}", "1")

                return JsonResponse(
                    data={"message": "criado"},
                    headers={"Location": pessoa.get_absolute_url()},
                    status=201
                )
            return JsonResponseUnprocessableEntity(
                data=form.errors
            )
        except IntegrityError:
            return JsonResponseUnprocessableEntity(
                data={"message": "o apelido já existe"}
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
