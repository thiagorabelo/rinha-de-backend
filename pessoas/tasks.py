from celery import shared_task

from .models import Pessoa

@shared_task
def save_pessoa(pessoa_dict):
    Pessoa.objects.create(**pessoa_dict)
