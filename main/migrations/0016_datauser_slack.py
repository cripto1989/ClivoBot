# Generated by Django 2.1.3 on 2018-11-17 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20181111_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='datauser',
            name='slack',
            field=models.CharField(default='', max_length=140, verbose_name='Slack ID'),
            preserve_default=False,
        ),
    ]