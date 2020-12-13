# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('labworks', '0012_auto_20151127_1304'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5')),
                ('teacher', models.ForeignKey(to='labworks.Teacher')),
            ],
        ),
        migrations.AlterField(
            model_name='labwork',
            name='parent',
            field=models.ForeignKey(verbose_name=b'\xd0\x9f\xd1\x80\xd0\xb5\xd0\xb4\xd1\x8b\xd0\xb4\xd1\x83\xd1\x89\xd0\xb0\xd1\x8f \xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xb0', blank=True, to='labworks.Labwork', null=True),
        ),
        migrations.AddField(
            model_name='labwork',
            name='category',
            field=models.ForeignKey(verbose_name=b'\xd0\x9a\xd0\xb0\xd1\x82\xd0\xb5\xd0\xb3\xd0\xbe\xd1\x80\xd0\xb8\xd1\x8f', blank=True, to='labworks.Category', null=True),
        ),
    ]
