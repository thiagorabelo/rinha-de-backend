from ninja import ModelSchema, Schema
from pydantic import field_validator

from .models import Pessoa


class PessoaSchema(ModelSchema):
    class Meta:
        model = Pessoa
        fields = ["apelido", "nome", "nascimento", "stack"]

    @field_validator("stack", check_fields=False)
    @classmethod
    def stack_cannot_contain_empty_item(cls, stack: list[str]) -> list[str]:
        if not all(stack):
            raise ValueError("Can not contains empty item")
        return stack


class CreatedResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    message: str
