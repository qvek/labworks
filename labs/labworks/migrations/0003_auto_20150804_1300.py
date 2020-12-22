# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0002_labworksuser_first_enter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('name',), 'get_latest_by': 'name'},
        ),
        migrations.AlterModelOptions(
            name='labworksuser',
            options={'ordering': ('last_name', 'first_name', 'surname')},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ('user',)},
        ),
        migrations.AlterModelOptions(
            name='teacher',
            options={'ordering': ('user',)},
        ),
        migrations.AlterField(
            model_name='labwork',
            name='name',
            field=models.CharField(max_length=100, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'),
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(verbose_name=b'\xd0\x93\xd1\x80\xd1\x83\xd0\xbf\xd0\xbf\xd0\xb0', to='labworks.Group'),
        ),
    ]
