import json

from django.db import IntegrityError
from django.http import HttpResponse, HttpRequest
from django.views import View

from .models import Pessoa


# https://docs.djangoproject.com/en/4.2/topics/async/
class PessoaView(View):

    def _get_one(self, request, pk):
        pessoa_dict = Pessoa.get_as_dict(pk=pk)
        pessoa_json = json.dumps(pessoa_dict)
        return HttpResponse(
            content=pessoa_json.encode("utf-8"),
            content_type="text/json",
            status=200
        )

    def _list(self, request):
        pessoas_dict = Pessoa.filter_as_dict()
        pessoas_json = json.dumps(list(pessoas_dict))
        return HttpResponse(
            content=pessoas_json.encode("utf-8"),
            content_type="text/json",
            status=200
        )

    def _filter(self, request):
        term = request.GET['t'].split(" ")
        pessoas_dict = Pessoa.search_terms(*term, as_dict=True)
        pessoas_json = json.dumps(list(pessoas_dict))
        return HttpResponse(
            content=pessoas_json.encode("utf-8"),
            content_type="text/json",
            status=200
        )

    def get(self, request: HttpRequest, pessoa_pk=0):
        if pessoa_pk:
            return self._get_one(request, pessoa_pk)
        elif 't' in request.GET and request.GET['t']:
            return self._filter(request)
        return self._list(request)

    def post(self, request: HttpRequest):
        try:
            Pessoa.from_json(request.body.decode("utf-8"))
            return HttpResponse(
                content=b"""{"message": "criado"}""",
                content_type="text/json",
                status=201
            )
        except IntegrityError:
            return HttpResponse(
                content="""{"message": "o apelido já existe"}""".encode("utf-8"),
                content_type="text/json",
                status=422
            )


def contagem_pessoas(request):
    total = Pessoa.objects.all().count()
    return HttpResponse(
        content=f"{total}".encode("utf-8"),
        content_type="text/json",
        status=200
    )
