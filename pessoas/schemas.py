import uuid

from pydantic import BaseModel, Field, field_validator, PastDate
from typing import Annotated, ClassVar


class PessoaSchema(BaseModel):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)]
    apelido: str = Field(max_length=32)
    nome: str = Field(max_length=100)
    nascimento: PastDate = Field()

    stack_item_max_length: ClassVar[int] = 32

    stack: list[str] = Field(min_length=1)

    @field_validator("stack", check_fields=False)
    @classmethod
    def check_items_stack_length(cls, stack: list[str]) -> list[str]:
        if any(map(lambda i: len(i) > cls.stack_item_max_length, stack)):
            raise ValueError(f"Stack item exceeds max length ({cls.stack_item_max_length})")
        return stack
