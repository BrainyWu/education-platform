# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from django.conf.urls import url, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register(r'course', CourseViewSet, basename="courses")
router.register(r'resource', CourseResourceViewSet, basename="resource")
router.register(r'(?P<course_id>\d+)/comment', CourseCommentViewSet, basename="comment")
router.register(r'(?P<course_id>\d+)/lessons', LessonViewSet, basename="lesson")
router.register(r'(?P<course_id>\d+)/lessons/(?P<lesson_id>\d+)/videos', VideoViewSet, basename="video")

urlpatterns = [
    url(r'(?P<course_id>\d+)/videos', VideoViewSet.as_view({'get': 'list'}), name='c_videos'),
    url(r'^', include(router.urls))
]
