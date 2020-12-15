# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0006_auto_20150905_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='labworkgroupmembership',
            name='deadline',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
