# Generated by Django 2.1.3 on 2018-12-23 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_dailyemotions_another_week_yes'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyemotions',
            name='another_week_no',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Another Week No'),
        ),
    ]