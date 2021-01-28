#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from rest_framework import mixins, viewsets, filters, status

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification
from .serializers import NotificationSerializer
from .consumers import NotificationsConsumer


class NotificationUnreadView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """未读通知列表"""
    serializer_class = NotificationSerializer

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()


def notification_handler(actor=None, recipient=None, verb=None, action_object=None, **kwargs):
    """
    通知处理器
    :param actor:           request.user对象
    :param recipient:       User Instance 接收者实例，可以是一个或者多个接收者
    :param verb:            str 通知类别
    :param action_object:   Instance 动作对象的实例
    :param kwargs:          key, id_value等
    :return:                None
    """
    key = kwargs.pop('key', 'notification')
    id_value = kwargs.pop('id_value', None)
    slug = kwargs.pop('slug', None)

    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    # request.user == recipient或recipient为空不通知
    elif actor == recipient or not recipient:
        return
    else:
        recipients = [recipient]

    for recipient in recipients:
        newnotify = Notification.objects.create(
            actor=actor,
            recipient=recipient,
            slug=slug,
            verb=verb,
            action_object=action_object
        )
        newnotify.save()

        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'key': key,
            'actor_name': actor.username,
            'id_value': id_value,
            'msg': newnotify.__str__(),
        }
        async_to_sync(channel_layer.send)("notifications", payload)

