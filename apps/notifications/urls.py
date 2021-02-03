#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.conf.urls import url, include

from .views import *

app_name = 'notifications'

urlpatterns = [
    url('unread/', NotificationUnreadView.as_view({'get': 'list'}), name='unread'),
    url('mark-all-read/', mark_all_as_read, name='mark_all_read'),
    url('mark-as-read/<uuid>/', mark_as_read, name='mark_as_read'),
]
