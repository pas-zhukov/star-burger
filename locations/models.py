from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.TextField(unique=True, verbose_name='Адрес')
    lon = models.FloatField(verbose_name='Долгота')
    lat = models.FloatField(verbose_name='Широта')
    updated = models.DateTimeField(default=timezone.now, verbose_name='Дата изменения')
