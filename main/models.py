from django.db import models
from django.contrib.postgres.fields import JSONField


class History(TimeStampModel):
    session = models.CharField(max_length=140, verbose_name="SessionID")
    data = JSONField()

    def __str__(self):
        pass
