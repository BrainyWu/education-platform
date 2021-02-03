#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = 'wuhai'

from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from rest_framework import mixins, viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification
from .serializers import NotificationSerializer
from lib.utils import get_object


class NotificationUnreadView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """未读通知列表"""
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.all()
        # return self.request.user.notifications.unread()


@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated,))
def mark_all_as_read(request, *args, **kwargs):
    """将所有通知标为已读"""
    request.user.notifications.mark_all_as_read()
    redirect_url = request.data.get('next') or request.query_params.get('next')

    messages.add_message(request, messages.SUCCESS, f'用户{request.user.username}的所有通知标为已读')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('notification:unread')


@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated,))
def mark_as_read(request, uuid, *args, **kwargs):
    """根据slug标为已读"""
    redirect_url = request.data.get('next') or request.query_params.get('next')

    notification = get_object(Notification, object_id=uuid)
    notification.mark_as_read()

    messages.add_message(request, messages.SUCCESS, f'通知{notification}标为已读')
    if redirect_url:
        return redirect(redirect_url)
    return redirect('notifications:unread')


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
    async_to_sync(channel_layer.group_send)("notifications", payload)

