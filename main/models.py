from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext as _
from model_utils import Choices
from django.contrib.postgres.fields import JSONField

# Create your models here.


class DataUser(TimeStampedModel):
    session_id = models.CharField(max_length=400, blank=True, null=True)
    user_name = models.CharField(max_length=50, blank=True, null=True)
    jobcoach_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    GENDER = Choices((1, 'male', _('Masculino')), (2, 'female', _('Femenino')))
    user_gender = models.PositiveSmallIntegerField(choices=GENDER, default=GENDER.male, blank=True, null=True)
    EMOTION = Choices((1, 'emotion_frustrated', _('Frustado')),
                      (2, 'emotion_sad', _('Triste')), (3, 'emotion_irritated', _('Irritado')))
    emotion_neg = models.PositiveSmallIntegerField(choices=EMOTION, default=EMOTION.emotion_frustrated,
                                               blank=True, null=True)

    def __str__(self):
        return "{}".format(self.session_id)


class History(TimeStampedModel):
    session = models.CharField(max_length=140, verbose_name="SessionID")
    data = JSONField()

    def __str__(self):
        pass


class DailyEmotions(TimeStampedModel):
    EMOTION = Choices((1, 'emotion_happy', _('Feliz')), (2, 'emotion_excited', _('Emocionado')),
                      (3, 'emotion_frustrated', _('Frustado')), (4, 'emotion_sad', _('Triste')),
                      (5, 'emotion_irritated', _('Irritado')))
    emotion_pos = models.PositiveSmallIntegerField(choices=EMOTION, default=EMOTION.emotion_happy,
                                                   blank=True, null=True)
    emotion_neg = models.PositiveSmallIntegerField(choices=EMOTION, default=EMOTION.emotion_frustrated,
                                                   blank=True, null=True)
    first_obstacle = models.TextField(max_length=500, blank=True, null=True, verbose_name="First Obstacle")
    alerts_total = models.CharField(max_length=10, blank=True, null=True, verbose_name="Alerts Total")
    alerts_critical = models.CharField(max_length=10, blank=True, null=True, verbose_name="Alerts Criticals")
    alerts_non_critical = models.CharField(max_length=10, blank=True, null=True, verbose_name="Alerts Non-Critial")
    work_dislike = models.TextField(max_length=500, blank=True, null=True, verbose_name="Work Dislike")
    session_id = models.ForeignKey(DataUser, on_delete=models.CASCADE)

    def __str__(self):
        pass
