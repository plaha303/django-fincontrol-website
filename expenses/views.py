import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreferences


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__startswith=search_str, owner=request.user) | Expense.objects.filter(
            date__startswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user_preferences = UserPreferences.objects.filter(user=request.user).first()
    currency = user_preferences.currency if user_preferences else None
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if not amount:
            messages.error(request, 'Сума є обов\'язковою')

        elif not description:
            messages.error(request, 'Опис є обов\'язковим')

        elif not date:
            messages.error(request, 'Дата є обов\'язковою')
        else:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Невірний формат дати')
            else:
                Expense.objects.create(owner=request.user,
                                       amount=amount,
                                       date=date,
                                       category=category,
                                       description=description)

                messages.success(request, 'Витрати успішно додано')
                return redirect('expenses')
        return render(request, 'expenses/add_expense.html', context)


@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount').replace(',', '.')
        description = request.POST.get('description')
        date = request.POST.get('expense_date')
        category = request.POST.get('category')

        if date:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неправильний формат дати.')
                return render(request, 'expenses/edit-expense.html', context)
        else:
            messages.error(request, 'Дата є обов\'язковою')
            return render(request, 'expenses/edit-expense.html', context)

        expense.amount = amount
        expense.description = description
        expense.date = date
        expense.category = category
        expense.save()

        messages.success(request, 'Витрати успішно оновлено')
        return redirect('expenses')


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Витрати успішно видалено')
    return redirect('expenses')


def expense_category_summary(request):
    today_date = datetime.date.today()
    six_months_ago = today_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago,
                                      date__lte=today_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')
