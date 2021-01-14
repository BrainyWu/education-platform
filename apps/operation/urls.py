# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'add_ask', views.AddUserAskViewSet, basename="addask")
router.register(r'add_fav', views.AddFavViewSet, basename="addfav")
router.register(r'banners', views.BannerViewSet, basename="banners")

urlpatterns = [
    url(r'^', include(router.urls)),
]
