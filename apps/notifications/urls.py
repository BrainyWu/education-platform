#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.conf.urls import url, include

from apps.notifications import views


urlpatterns = [
    url('', views.NotificationUnreadView.as_view(), name='unread'),
]
