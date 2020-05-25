# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0005_auto_20150804_1307'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ('code', 'name')},
        ),
        migrations.AddField(
            model_name='report',
            name='comment',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
