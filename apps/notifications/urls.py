#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.conf.urls import url, include

from .views import *


urlpatterns = [
    url('', NotificationUnreadView.as_view({'get': 'list'}), name='unread'),
]
