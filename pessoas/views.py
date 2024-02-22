import gevent

from django.conf import settings
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.views import View

from .forms import PessoaForm
from .http import JsonResponseBadRequest, JsonResponseNotFound, \
                  JsonResponseUnprocessableEntity
from .utils import get_body_as_json
from .models import Pessoa
from .cache import get_pessoa_dict_by_cache_or_db, set_pessoa_dict_cache, \
                   has_pessoa_apelido_cached

from .queue import insert_worker, insert_task


gevent.spawn(insert_worker)


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

    # TODO: Muito lento. Talvez seja interessante usar uma
    #       coluna de texto normal apenas com um índice.
    def _filter(self, request, t):
        if not t:
            return JsonResponseBadRequest(
                data={"message": """Busca inválida (Informe o termo de busca "t")"""}
            )

        terms = t.split()
        qs = Pessoa.search_terms(*terms, as_dict=True)[:50]
        return JsonResponse(
            data=list(qs),
            headers={"My-Host-Name": settings.MY_HOST_NAME},
            safe=False
        )

    def get(self, request: HttpRequest, pessoa_pk=0):
        if pessoa_pk:
            return self._get_one(request, pessoa_pk)
        t = request.GET.get('t')
        return self._filter(request, t)

    def post(self, request: HttpRequest):
        try:
            form = PessoaForm(data=get_body_as_json(request))
            if form.is_valid():
                pessoa = form.instance

                if has_pessoa_apelido_cached(pessoa):
                    return JsonResponseUnprocessableEntity(
                        data={"message": "O apelido já existe"},
                        headers={"My-Host-Name": settings.MY_HOST_NAME}
                    )

                try:
                    # pessoa = form.save()
                    insert_task.put_nowait(pessoa.to_dict(pk=True))
                    set_pessoa_dict_cache(pessoa.pk, pessoa.to_dict())
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


def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="application/json",
        headers={"My-Host-Name": settings.MY_HOST_NAME},
        status=200
    )
