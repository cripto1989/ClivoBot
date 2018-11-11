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
