from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.utils import IntegrityError

from smtplib import SMTPRecipientsRefused

from .forms import UserAuthForm, UserRegisterForm
from .models import User, GeneratedPost
from .decorators import redirect_on_auth


def hello_page(request):
    return render(request, "index.html")


# вход на сайт
@redirect_on_auth
def login_page(request):
    if request.method == "POST":
        form_with_data = UserAuthForm(request.POST)
        if form_with_data.is_valid():
            user_login = form_with_data["username"].value()
            user_password = form_with_data["password"].value()

            user = authenticate(request, username=user_login, password=user_password)
            if user and user.is_active:
                login(request, user)
                messages.success(request, "Вход выполнен успешно")
                return HttpResponseRedirect("/account/profile")
        messages.error(request, "Логин или пароль введен неверно")

    user_form_object = UserAuthForm()
    return render(request, "account/login.html", context={"auth_form": user_form_object})


@redirect_on_auth
def register_page(request):
    if request.method == "POST":
        form_with_data = UserRegisterForm(request.POST)
        if form_with_data.is_valid():
            user_email = form_with_data["email"].value()
            user_login = form_with_data["username"].value()
            user_password = form_with_data["password"].value()
            user_password_2 = form_with_data["password_repeat"].value()

            if user_password != user_password_2:
                messages.error(request, "Пароли не совпадают")
                return HttpResponseRedirect("/account/register")

            if not settings.DEBUG:
                try:
                    send_mail(
                        'Спасибо за регистрацию',
                        'Благодарим вас за регистрацию на сервисе PostMaker.',
                        'PostMakerOfficial@yandex.ru',
                        [user_email],
                    )

                except SMTPRecipientsRefused:
                    messages.error(request, "Почта введена неверно")
                    return HttpResponseRedirect("/account/register")

            try:
                new_user = User.objects.create_user(email=user_email, username=user_login, password=user_password)
                new_user.save()
            except IntegrityError:
                messages.error(request, "Пользователь уже существует")
                return HttpResponseRedirect("/account/register")

            # все идет по плану
            user = authenticate(request, username=user_login, password=user_password)
            login(request, user)

            messages.success(request, "Регистрация прошла успешно")
            return HttpResponseRedirect("/account/profile")

        messages.error(request, "Какая то ошибка")
        return HttpResponseRedirect("/account/register")

    user_form_object = UserRegisterForm()

    return render(request, "account/register.html", context={"register_form": user_form_object})


@login_required
def profile_page(request):
    user = User.objects.get(pk=request.user.id)

    form_parameters = {
        "Эл. почта": {
            "value": user.email,
            "type": "static"
        },
        "Имя пользователя": {
            "value": user.username,
            "type": "static"
        },
        "Ссылка на аккаунт instagram": {
            "value": user.instagram_url or "",
            "type": "dynamic"
        },
        "Роль на сайте": {
            "value": "Администратор" if user.is_admin else "Пользователь",
            "type": "static"
        }
    }

    return render(request, "account/profile.html", context={"parameters": form_parameters})


def generate_text():
    return "hello world"


@csrf_exempt
@login_required
def model_generate_post(request):
    if request.method == "POST":
        print(request.body)
        return JsonResponse({"message": "hello world from django"})

    return render(request, "model/generate_post.html")


def model_history(request):
    pass
