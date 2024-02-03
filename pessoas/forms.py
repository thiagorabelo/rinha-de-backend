from django import forms

from .models import Pessoa


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ("apelido", "nome", "nascimento", "stack")

    # Desabilitando validação de unicidade
    def clean(self):
        self._validate_unique = True
        return self.cleaned_data
