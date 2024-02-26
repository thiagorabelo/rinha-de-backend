from django import forms

from .models import Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ("apelido", "nome", "nascimento", "stack")

    def clean_stack(self):
        stack = self.cleaned_data.get("stack")
        if stack:
            return list(set(stack))
        return stack

    # Desabilitando validação de unicidade
    def clean(self):
        self._validate_unique = False
        return self.cleaned_data
