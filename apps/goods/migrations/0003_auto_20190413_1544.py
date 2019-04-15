# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-13 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_auto_20190407_1732'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goods',
            options={'ordering': ['id'], 'verbose_name': '商品', 'verbose_name_plural': '商品'},
        ),
        migrations.AlterField(
            model_name='goodscategorybrand',
            name='image',
            field=models.ImageField(max_length=200, upload_to='brands/'),
        ),
    ]
