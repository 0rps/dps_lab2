# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0002_authcode_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='authcode',
            name='redirect_uri',
            field=models.URLField(default='http://123.ru'),
            preserve_default=False,
        ),
    ]
