# Generated by Django 2.1.3 on 2018-11-10 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20181110_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datauser',
            name='emotion_neg',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Frustado'), (2, 'Triste'), (3, 'Irritado')], default=1, null=True),
        ),
    ]
