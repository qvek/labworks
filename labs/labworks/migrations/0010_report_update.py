# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0009_auto_20150916_0648'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='update',
            field=models.NullBooleanField(default=False),
        ),
    ]
