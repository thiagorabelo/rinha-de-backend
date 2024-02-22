from datetime import date
from typing import Annotated
from pydantic import BaseModel, StringConstraints, Field, validator


class PessoaSchema(BaseModel):
    apelido: Annotated[str, StringConstraints(max_length=32)]
    nome: Annotated[str, StringConstraints(max_length=100)]
    nascimento: date
    stack: list[str] = Field(str, min_length=1)

    @validator("stack")
    def validate_stack(cls, vls):
        err = [v for v in vls if len(v) > 32 or not v]
        if err:
            raise ValueError(f"Invalid values: {err}")
        return vls
