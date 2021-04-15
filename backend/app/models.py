from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, UserManager as AbstractUserManager


class UserManager(AbstractUserManager):
    pass


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    last_login = models.DateTimeField(default=timezone.now)

    username = models.CharField(max_length=200, unique=True)
    instagram_url = models.URLField(max_length=200, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()


# таблицы зависит от User
class GeneratedPost(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    image_filename = models.CharField(max_length=300, blank=True, null=True)
    content = models.CharField(max_length=5000)


# модель зависит от User
class Post(models.Model):
    content = models.CharField(max_length=5000)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
