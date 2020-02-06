from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    phone_no = models.CharField(max_length=10)
    device_id = models.CharField(max_length=5000)
    willin_to_help = models.IntegerField(default=1)     # 1-Willing to help, 0-Not Willing to help
    is_staff = models.BooleanField(default=False)       # Field necessary for a django user
    is_active = models.BooleanField(default=True)       # Field necessary for a django user
    is_superuser = models.BooleanField(default=False)   # Field necessary for a django user
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'date_of_birth', 'phone_no', 'device_id']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Chat(models.Model):
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_id")
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_id")
    body = models.TextField()
    date_time_creation = models.DateTimeField(auto_now_add=True)

