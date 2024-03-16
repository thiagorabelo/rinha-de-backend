from django import forms
from django.forms import ValidationError

from .models import Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ("apelido", "nome", "nascimento", "stack")

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, data=data, **kwargs)
        self._stack = data.get("stack")

    def clean_stack(self):
        try:
            if not all(map(lambda o: isinstance(o, str), self._stack)):
                raise ValidationError("Deve ser uma lista de strings")
        except Exception as ex:
            raise ValidationError("stack deve ser um iteravel") from ex

        stack = self.cleaned_data.get("stack")
        if stack:
            return list(set(stack))
        raise ValidationError("Não pode ser nulo")

    # Desabilitando validação de unicidade
    def clean(self):
        self._validate_unique = False
        return self.cleaned_data
