from django.contrib import admin
from .models import Expense, Category


class ExpenseAdmin(admin.ModelAdmin):
    verbose_name_plural = 'Витрати'


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
