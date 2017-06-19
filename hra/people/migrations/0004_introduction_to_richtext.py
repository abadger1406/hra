# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-15 14:17
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields
from django.utils.html import linebreaks


def convert_textfield_into_richtext(apps, schema_editor):
    PersonIndexPage = apps.get_model('people', 'PersonIndexPage')
    PersonPage = apps.get_model('people', 'PersonPage')

    for page in PersonIndexPage.objects.all():
        page.introduction = linebreaks(page.introduction)
        page.save()

    for page in PersonPage.objects.all():
        page.introduction = linebreaks(page.introduction)
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_auto_20170511_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personindexpage',
            name='introduction',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='personpage',
            name='introduction',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.RunPython(convert_textfield_into_richtext, migrations.RunPython.noop),
    ]