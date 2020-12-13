# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0007_labworkgroupmembership_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='labworkgroupmembership',
            name='deadline',
            field=models.DateField(null=True, verbose_name=b'\xd0\xa1\xd1\x80\xd0\xbe\xd0\xba \xd1\x81\xd0\xb4\xd0\xb0\xd1\x87\xd0\xb8', blank=True),
        ),
    ]
