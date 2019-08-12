from django.db import models


class RecacheSchedule(models.Model):
    url = models.TextField(unique=True)
    datetime = models.DateTimeField(db_index=True)
