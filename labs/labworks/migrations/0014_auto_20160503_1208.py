# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0013_auto_20160212_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='labwork',
            name='code',
            field=models.CharField(max_length=10, null=True, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xb4', blank=True),
        ),
        migrations.AddField(
            model_name='labwork',
            name='no_check',
            field=models.BooleanField(default=False, verbose_name=b'\xd0\x9d\xd0\xb5 \xd0\xbe\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb2\xd0\xb0\xd1\x82\xd1\x8c'),
        ),
    ]
