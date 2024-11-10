from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse

from django.utils.encoding import smart_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token
from django.contrib import auth


# Create your views here.


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': "Некоректна адреса електронної пошти"},
                                status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Користувач з такою адресою електронної пошти вже існує'},
                                status=409)

        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': "Ім'я користувача має містити лише буквено-цифрові символи"},
                                status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Користувач з таким ім\'ям вже існує'},
                                status=409)

        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # Get user data
        # validate
        # create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Пароль повинен бути не менше 6 символів')
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={
                    'uidb64': uidb64, 'token': account_activation_token.make_token(user)})

                activate_url = 'http://' + domain + link
                email_body = 'Привіт ' + user.username + ' Ви успішно зареєструвались на нашому сайті. ' \
                    'Для активації облікового запису перейдіть за посиланням нижче. \n\n' + activate_url
                email_subject = 'Активуйте свій обліковий запис'

                email = EmailMessage(
                    email_subject,
                    email_body,
                    'plahotin033@gmail.com',
                    [email],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Аккаунт успішно створено')
                return render(request, 'authentication/register.html')

        messages.error(request, 'Користувач з таким ім\'ям вже існує')
        return render(request, 'authentication/register.html', context)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'Користувач вже активований')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Аккаунт активовано')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Привіт ' + user.username)
                    return redirect('expenses')
                messages.error(request, 'Аккаунт не активований перевірте свою пошту')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Неправильний логін або пароль')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Введіть логін і пароль')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'Ви вийшли з облікового запису')
        return redirect('login')
