# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-12-01 15:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_auto_20221201_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='create_time',
            field=models.DateField(auto_now_add=True),
        ),
    ]
