import codecs
import json
import types

from django.conf import settings
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
@method_decorator(csrf_exempt, name='dispatch')
class PessoaView(ParseJSONMixin, View):

    def _get_one(self, request, pk):
        pessoa_dict = Pessoa.get_as_dict(pk=pk)
        return JsonResponse(data=pessoa_dict)

    def _filter(self, request):
        if t := request.GET.get('t'):
            term = t.split()
            pessoas_dict = Pessoa.search_terms(*term, as_dict=True)
            return JsonResponse(data=list(pessoas_dict), safe=False)
        return JsonResponseBadRequest(data={"message": """Busca inválida (Informe o termo de busca "t")"""})

    def get(self, request: HttpRequest, pessoa_pk=0):
        if pessoa_pk:
            return self._get_one(request, pessoa_pk)
        return self._filter(request)

    def post(self, request: HttpRequest):
        try:
            form = PessoaForm(data=request.json())
            if form.is_valid():
                pessoa = form.save()
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
        content_type="text/json",
        status=200
    )
