# Generated by Django 2.2.5 on 2019-10-10 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0003_auto_20191009_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historico',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='list.Objeto'),
        ),
    ]
