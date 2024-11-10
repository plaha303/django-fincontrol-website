import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreferences
from django.contrib import messages


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__startswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__startswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreferences.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source = request.POST.get('source')

        if not amount:
            messages.error(request, 'Сума є обов\'язковою')

        elif not description:
            messages.error(request, 'Опис є обов\'язковим')

        elif not date:
            messages.error(request, 'Дата є обов\'язковою')
        else:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Невірний формат дати')
            else:
                UserIncome.objects.create(
                    owner=request.user,
                    amount=amount,
                    date=date,
                    source=source,
                    description=description
                )

                messages.success(request, 'Прибуток успішно додано')
                return redirect('income')
        return render(request, 'income/add_income.html', context)


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }

    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)

    elif request.method == 'POST':
        amount = request.POST.get('amount').replace(',', '.')
        description = request.POST.get('description')
        date = request.POST.get('income_date')
        source = request.POST.get('source')

        if date:
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Неправильний формат дати.')
                return render(request, 'income/edit_income.html', context)
        else:
            messages.error(request, 'Дата є обов\'язковою')
            return render(request, 'income/edit_income.html', context)

        income.amount = amount
        income.description = description
        income.date = date
        income.source = source
        income.save()

        messages.success(request, 'Прибуток успішно оновлено')
        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Прибуток успішно видалено')
    return redirect('income')
