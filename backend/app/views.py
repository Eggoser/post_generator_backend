from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.utils import IntegrityError

from smtplib import SMTPRecipientsRefused
import json
import base64
import uuid
import io
import os
import subprocess
from PIL import Image

from .forms import UserAuthForm, UserRegisterForm
from .models import User, GeneratedPost
from .decorators import redirect_on_auth


def call_gpt(text, tags, length=70, with_tags=False):
    try:
        compiler = os.path.join(settings.BASE_DIR / "app" / 'gpt/virtual/bin/python3')
        ex_file = os.path.join(settings.BASE_DIR / "app" / 'gpt/gpt.py')

        if with_tags:
            output = subprocess.check_output([compiler, ex_file, text, str(length), tags])
        else:
            output = subprocess.check_output([compiler, ex_file, text, str(length)])
    except:
        return "Error :("
    return output


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

    if request.method == "POST":
        insta_url = request.POST.get("@Instagram")
        user.instagram_url = insta_url
        user.save()

    form_parameters = {
        "Эл. почта": {
            "value": user.email,
            "type": "static",
            "placeholder": ""
        },
        "Имя пользователя": {
            "value": user.username,
            "type": "static",
            "placeholder": ""
        },
        "@Instagram": {
            "value": user.instagram_url or "",
            "type": "dynamic",
            "placeholder": "@voftik"
        },
        "Роль на сайте": {
            "value": "Администратор" if user.is_admin else "Пользователь",
            "type": "static",
            "placeholder": ""
        }
    }

    return render(request, "account/profile.html", context={"parameters": form_parameters})


@csrf_exempt
@login_required
def model_generate_post(request):
    if request.method == "POST":
        json_data = json.loads(request.body)

        tags = json_data["tags"]

        image_raw = io.BytesIO(base64.b64decode(json_data["image"]))
        img = Image.open(image_raw)
        img = img.convert("RGB")

        new_filename = uuid.uuid4().hex + ".jpg"
        file_path = os.path.join(settings.MEDIA_ROOT, new_filename)
        img.save(file_path, format="JPEG")

        generated_text = call_gpt(text="", tags="|".join(tags))

        cur_user = User.objects.get(pk=request.user.id)
        generated_post = GeneratedPost(tags=" | ".join(tags),
                                       content=generated_text,
                                       image_filename=new_filename,
                                       user_id=cur_user)
        generated_post.save()

        return JsonResponse({"message": generated_text})

    return render(request, "model/generate_post.html")


def model_history(request):
    user = User.objects.get(pk=request.user.id)
    user_local_history = GeneratedPost.objects.filter(user_id=user)

    return render(request, "model/history.html", context={"history": user_local_history})
