# Generated by Django 4.2.5 on 2023-10-04 01:08

import django.contrib.postgres.search

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE pessoas_pessoa ADD COLUMN search_field tsvector GENERATED ALWAYS AS (
                        to_tsvector('english', coalesce(apelido, ''))
                        || to_tsvector('english', coalesce(nome, ''))
                        || to_tsvector('english', array_to_tsvector(array_remove(stack, null))::text)
                    ) STORED;
                    """,
                    reverse_sql="ALTER TABLE pessoas_pessoa DROP COLUMN search_field ;"
                )
            ],
            state_operations=[
                migrations.AddField(
                    model_name='pessoa',
                    name='search_field',
                    field=django.contrib.postgres.search.SearchVectorField(verbose_name='Campo de busca', null=False),
                    preserve_default=False,
                ),
            ],
        )
    ]
