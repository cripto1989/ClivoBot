from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext as _
from model_utils import Choices
from django.contrib.postgres.fields import JSONField

# Create your models here.


class DataUser(TimeStampedModel):
    session_id = models.CharField(max_length=400)
    user_name = models.CharField(max_length=50)
    jobcoach_name = models.CharField(max_length=50)
    user_email = models.EmailField()
    GENDER = Choices((1, 'male', _('Masculino')), (2, 'female', _('Femenino')))
    gender = models.PositiveSmallIntegerField(choices=GENDER, default=GENDER.male)
    EMOTION = Choices((1, 'emotion_frustrated', _('Frustado')), (2, 'emotion_sad', _('Triste')),(1, 'emotion_irritated', _('Irritado')))
    emotion = models.PositiveSmallIntegerField(choices=EMOTION, default=EMOTION.emotion_frustrated)

    def __str__(self):
        return "{}".format(self.session_id)


class History(TimeStampedModel):
    session = models.CharField(max_length=140, verbose_name="SessionID")
    data = JSONField()

    def __str__(self):
        pass
