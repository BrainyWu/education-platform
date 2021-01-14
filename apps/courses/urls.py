# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from django.conf.urls import url, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'course', views.CourseViewSet, basename="courses")
router.register(r'resource', views.CourseResourceViewSet, basename="resource")
router.register(r'comment', views.CourseCommentViewSet, basename="comment")
router.register(r'lesson', views.LessonViewSet, basename="lesson")
router.register(r'video', views.VideoViewSet, basename="video")

urlpatterns = [
    url(r'^', include(router.urls)),
]