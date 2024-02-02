from ninja import ModelSchema, Schema

from .models import Pessoa


class PessoaSchema(ModelSchema):
    class Meta:
        model = Pessoa
        fields = ["apelido", "nome", "nascimento", "stack"]


class UnprocessableEntityResponseSchema(Schema):
    message: str


class CreatedResponseSchema(Schema):
    message: str
