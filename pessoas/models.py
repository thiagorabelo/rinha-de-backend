import json
import operator
import uuid

from functools import reduce

from django.db import models
from django.db.models.functions import Cast
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField, SearchQuery
from django.contrib.postgres.indexes import GinIndex


class Pessoa(models.Model):
    id = models.UUIDField("Id", primary_key=True, default=uuid.uuid4, editable=False)
    apelido = models.CharField("Apelido", max_length=32, unique=True, null=False, blank=False)
    nome = models.CharField("Nome", max_length=100, null=False, blank=False)
    nascimento = models.DateField("Data de Nascimento", null=False, blank=False)
    stack = ArrayField(
        models.CharField(max_length=32, blank=False),
        verbose_name="Stack",
        null=True,
        blank=True,
        default=list,
    )

    # create extension btree_gin;
    # create index search_field_gin_idx on pessoas_pessoa using gin (search_field);
    # create index search_field_gin_idx on pessoas_pessoa using gin (to_tsvector('portuguese', search_field));
    # https://pganalyze.com/blog/gin-index
    # https://pganalyze.com/blog/full-text-search-django-postgres
    # https://docs.djangoproject.com/en/4.2/ref/contrib/postgres/search/#searchquery
    # https://www.postgresql.org/docs/current/textsearch-controls.html
    # https://docs.djangoproject.com/en/4.2/ref/migration-operations/#separatedatabaseandstate
    # https://docs.djangoproject.com/en/4.2/ref/contrib/postgres/search/#postgresql-fts-search-configuration
    # https://stackoverflow.com/a/62420255

    # search_field = models.TextField("Campo de Busca", blank=True, null=False, default="")
    search_field = SearchVectorField("Campo de busca", null=False)

    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"
        indexes = (
            GinIndex(fields=["search_field"]),
        )

    def __str__(self):
        return self.apelido

    def _do_insert(self, manager, using, fields, returning_fields, raw):
        exclude_fields = ('search_field',)
        fields = filter(lambda f: f.attname not in exclude_fields, fields)
        return super()._do_insert(manager, using, tuple(fields), returning_fields, raw)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        exclude_fields = ('search_field',)
        values = list(filter(lambda value_tuple: value_tuple[0].attname not in exclude_fields, values))
        return super()._do_update(base_qs, using, pk_val, values, update_fields, forced_update)

    # def save(self, *args, **kwargs):
    #     itens = set(i.lower() for i in self.stack)
    #     itens.add(self.apelido.lower())
    #     itens = itens.union(n.lower() for n in self.nome.split())
    #     self.search_field = ",".join(itens)
    #     return super().save(*args, **kwargs)

    def to_json(self):
        json_dict = {
            "apelido": self.apelido,
            "nome": self.nome,
            "nascimento": self.nascimento.isoformat(),
            "stack": self.stack,
        }
        return json.dumps(json_dict)

    @classmethod
    def filter_as_dict(cls, **kwargs):
        return cls.objects \
            .filter(**kwargs) \
            .values('apelido', 'nome', 'stack') \
            .annotate(nascimento=Cast('nascimento', models.CharField()))

    @classmethod
    def search_terms(cls, *terms, as_dict=False):
        def to_tsquery(*trms):
            return " & ".join(trms)

        def to_search_queries(tsquery):
            configs = ["english", "portuguese"]
            return map(lambda c: SearchQuery(tsquery, search_type="raw", config=c), configs)

        tsquery = to_tsquery(*terms)
        search_queries = to_search_queries(tsquery)
        queryset = cls.objects.filter(
            reduce(
                operator.or_,
                map(lambda sq: models.Q(search_field=sq), search_queries)
            )
        )

        if as_dict:
            return queryset.values(
                'apelido',
                'nome',
                'stack'
            ).annotate(nascimento=Cast('nascimento', models.CharField()))
        return queryset

    @classmethod
    def get_as_dict(cls, **kwargs):
        return cls.filter_as_dict(**kwargs).get()

    @classmethod
    def from_json(cls, json_str):
        return cls.objects.create(**json.loads(json_str))
