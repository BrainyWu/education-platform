# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register(r'user', UserView, basename="user")
router.register(r'usercourse', UserFavOrgView, basename="user_course")
router.register(r'userfav/org', UserFavOrgView, basename="userfav_org")
router.register(r'userfav/teacher', UserFavTeacherView, basename="userfav_teacher")
router.register(r'userfav/course', UserFavOrgView, basename="userfav_course")
router.register(r'usermessages', UserFavOrgView, basename="user_messages")


urlpatterns = [
    url(r'^', include(router.urls)),
    # 修改密码
    url(r'^userpwd/$', ModifyPwdView.as_view({'put': 'update'}), name="update_pwd"),
    # 重置密码
    url(r'^resetpwd/$', ResetPwdView.as_view({'put': 'update'}), name="reset_pwd"),
    # 修改邮箱
    url(r'^useremail/$', ModifyEmailView.as_view({'put': 'update'}), name="update_email"),
    # 发送邮箱验证码
    url(r'^emailcode/$', send_email_code, name="send_email_code"),
]
