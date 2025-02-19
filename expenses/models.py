from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class Expense(models.Model):
    amount = models.FloatField(verbose_name='Сума')
    date = models.DateField(default=now, verbose_name='Дата')
    description = models.TextField(verbose_name='Опис')
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Власник')
    category = models.CharField(max_length=255, verbose_name='Категорія')

    def __str__(self):
        return self.category

    class Meta:
        ordering: ['-date']
        verbose_name = 'Витрату'
        verbose_name_plural = 'Витрати'


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Назва категорії')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорію'
        verbose_name_plural = 'Категорії'
