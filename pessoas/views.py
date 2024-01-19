from asgiref.sync import sync_to_async
from django.conf import settings
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
from .tasks import save_pessoa
from .utils import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached


# https://docs.djangoproject.com/en/4.2/topics/async/
@method_decorator(csrf_exempt, name="dispatch")
class PessoaView(ParseJSONMixin, View):

    async def _get_one(self, request, pk):
        try:
            pessoa_dict = await get_pessoa_dict_by_cache_or_db(pk)
            return JsonResponse(
                data=pessoa_dict,
                headers={"My-Host-Name": settings.MY_HOST_NAME}
            )
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
                    return JsonResponseUnprocessableEntity(
                        data={"message": "unique violation"},
                        headers={
                            "My-Host-Name": settings.MY_HOST_NAME
                        }
                    )

                try:
                    # pessoa = await form.asave()
                    await sync_to_async(save_pessoa.delay)(pessoa.to_dict())
                except IntegrityError:
                    return JsonResponseUnprocessableEntity(
                        data={"message": "o apelido já existe"},
                        headers={
                            "My-Host-Name": settings.MY_HOST_NAME
                        }
                    )
                finally:
                    await set_pessoa_dict_cache(pessoa.pk, pessoa.to_dict())

                return JsonResponse(
                    data={"message": "criado"},
                    headers={
                        "Location": pessoa.get_absolute_url(),
                        "My-Host-Name": settings.MY_HOST_NAME
                    },
                    status=201
                )
            return JsonResponseUnprocessableEntity(
                data=form.errors,
                headers={
                    "My-Host-Name": settings.MY_HOST_NAME
                }
            )
        except AttributeError as ex:
            return JsonResponseBadRequest(
                data={"message": str(ex)},
                headers={
                    "My-Host-Name": settings.MY_HOST_NAME
                }
            )


async def contagem_pessoas(request):
    total = await Pessoa.objects.all().acount()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )
