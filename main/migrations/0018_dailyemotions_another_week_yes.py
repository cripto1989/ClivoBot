# Generated by Django 2.1.3 on 2018-12-23 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_dailyemotions_slack'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyemotions',
            name='another_week_yes',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Another Week Yes'),
        ),
    ]