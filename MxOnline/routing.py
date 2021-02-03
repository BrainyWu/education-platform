# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from apps.notifications.consumers import NotificationsConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                url(r'^ws/notifications/$', NotificationsConsumer.as_asgi()),
            ])
        )
    )
})

