# _*_ encoding:utf-8 _*_
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(("male", "男"), ("female", "女")), default="male")
    address = models.CharField(max_length=100, default="")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="image/%Y/%m", max_length=100)

    class Meta:
        db_table = 'user_info'
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    # def save(self, *args, **kwargs):
    #     self.set_password(self.password)
    #     super(UserProfile, self).save(*args, **kwargs)
