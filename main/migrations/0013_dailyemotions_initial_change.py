# Generated by Django 2.1.3 on 2018-11-11 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_dailyemotions_data_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyemotions',
            name='initial_change',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='initial Change'),
        ),
    ]
