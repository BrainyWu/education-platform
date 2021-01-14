#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import mixins, viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification
from .serializers import NotificationSerializer


class NotificationUnreadView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """未读通知列表"""
    serializer_class = NotificationSerializer

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    """
    通知处理器
    :param actor:           request.user对象
    :param recipient:       User Instance 接收者实例，可以是一个或者多个接收者
    :param verb:            str 通知类别
    :param action_object:   Instance 动作对象的实例
    :param kwargs:          key, id_value等
    :return:                None
    """
    if actor.username != recipient.username and recipient.username == action_object.user.username:
        # 只通知接收者，即recipient == 动作对象的作者
        key = kwargs.get('key', 'notification')
        id_value = kwargs.get('id_value', None)
        # 记录通知内容
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )

        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'key': key,
            'actor_name': actor.username,
            'id_value': id_value
        }
        async_to_sync(channel_layer.group_send)('notifications', payload)
