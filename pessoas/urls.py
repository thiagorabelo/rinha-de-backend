from django.urls import path

from . import views

app_name = "pessoas"

urlpatterns = [
    path("pessoas", views.PessoaView.as_view(), name="pessoas"),
    path("pessoas/<uuid:pessoa_pk>", views.PessoaView.as_view(), name="pessoa"),
    path("contagem-pessoas", views.contagem_pessoas, name="contagem-pessoas")
]
