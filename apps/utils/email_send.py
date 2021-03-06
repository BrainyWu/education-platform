# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from random import Random

from django.core.mail import send_mail
from django_redis import get_redis_connection


def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_email(email, send_type):
    if send_type == 3:
        code = random_str(4)
    else:
        code = random_str(16)
    # 使用redis保存验证码，并设置过期：5分钟
    conn = get_redis_connection('default')
    conn.setex(':'.join(['verify_code', send_type, email]), 60 * 5, code)
    # 发送邮件
    email_title = ""
    email_body = ""

    # if send_type == 1:
    #     email_title = "xxx在线网注册激活链接"
    #     email_body = "请点击下面的链接激活你的账号: http://127.0.0.1:8000/active/{0}".format(code)
    #
    #     send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    #     if send_status:
    #         pass
    # elif send_type == 2:
    #     email_title = "xxx在线网注册密码重置链接"
    #     email_body = "请点击下面的链接重置密码: http://127.0.0.1:8000/reset/{0}".format(code)
    #
    #     send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    #     if send_status:
    #         pass
    # elif send_type == 3:
    #     email_title = "xxx在线网邮箱修改验证码"
    #     email_body = "你的邮箱验证码为: {0}".format(code)
    #
    #     send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    #     if send_status:
    #         pass
