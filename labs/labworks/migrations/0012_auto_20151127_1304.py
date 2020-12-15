# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0011_labwork_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labwork',
            name='parent',
            field=models.ForeignKey(to='labworks.Labwork', null=True),
        ),
    ]
