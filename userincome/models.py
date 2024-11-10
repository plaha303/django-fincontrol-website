from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class UserIncome(models.Model):
    amount = models.FloatField(verbose_name='Сума')
    date = models.DateField(default=now, verbose_name='Дата')
    description = models.TextField(verbose_name='Опис')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Власник')
    source = models.CharField(max_length=255, verbose_name='Джерело надходження')

    def __str__(self):
        return self.source

    class Meta:
        ordering: ['-date']
        verbose_name = 'Надходження'
        verbose_name_plural = 'Надходження'


class Source(models.Model):
    name = models.CharField(max_length=255, verbose_name='Джерело надходження')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Джерело надходження'
        verbose_name_plural = 'Джерела надходження'
