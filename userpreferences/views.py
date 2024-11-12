from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages


def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({"name": k, "value": v})

    user_preferences = UserPreferences.objects.filter(user=request.user).first()
    currency = user_preferences.currency if user_preferences else None

    if request.method == 'GET':
        return render(request, "preferences/index.html",
                      {'currencies': currency_data,
                       'user_preferences': user_preferences,
                       'currency': currency})
    else:
        currency = request.POST['currency']
        if user_preferences:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreferences.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Валюта успішно оновлена.')
        return redirect('index')
