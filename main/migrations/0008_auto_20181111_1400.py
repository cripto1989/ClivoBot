# Generated by Django 2.1.3 on 2018-11-11 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_dailyemotions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datauser',
            name='emotion_neg',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Frustado'), (2, 'Triste'), (3, 'Irritado')], null=True),
        ),
        migrations.AlterField(
            model_name='datauser',
            name='user_gender',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Masculino'), (2, 'Femenino')], null=True),
        ),
    ]
