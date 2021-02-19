# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'o', views.OrgViewSet, basename="org")
router.register(r'city', views.CityViewSet, basename="city")
router.register(r'teacher', views.TeacherViewSet, basename="teacher")

urlpatterns = [
    url(r'^', include(router.urls)),
]
