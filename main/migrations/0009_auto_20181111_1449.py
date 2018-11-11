# Generated by Django 2.1.3 on 2018-11-11 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20181111_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyemotions',
            name='flow',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Hola'), (2, '1hr'), (3, '2hrs')], null=True),
        ),
        migrations.AlterField(
            model_name='dailyemotions',
            name='emotion_neg',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Feliz'), (2, 'Emocionado'), (3, 'Frustado'), (4, 'Triste'), (5, 'Irritado')], null=True),
        ),
        migrations.AlterField(
            model_name='dailyemotions',
            name='emotion_pos',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Feliz'), (2, 'Emocionado'), (3, 'Frustado'), (4, 'Triste'), (5, 'Irritado')], null=True),
        ),
    ]