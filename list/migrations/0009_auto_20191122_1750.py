# Generated by Django 2.2.6 on 2019-11-22 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0008_auto_20191122_1749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historico',
            old_name='saida_entrada',
            new_name='entrada_saida',
        ),
    ]
