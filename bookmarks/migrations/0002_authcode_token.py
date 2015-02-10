# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=64)),
                ('creationTime', models.DateTimeField()),
                ('user', models.ForeignKey(to='bookmarks.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accessToken', models.CharField(max_length=64)),
                ('refreshToken', models.CharField(max_length=64)),
                ('expirationDate', models.DateTimeField()),
                ('user', models.ForeignKey(to='bookmarks.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
