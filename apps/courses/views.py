# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.key_constructor.constructors import DefaultListKeyConstructor, DefaultObjectKeyConstructor
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import mixins, viewsets, filters, status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.decorators import action

from .models import Course, CourseResource, Lesson, Video
from .serializers import CourseSerializer, LessonSerializer, CourseResourceSerializer, VideoSerializer
from notifications.views import notification_handler
from operation.models import UserFavorite, CourseComment
from operation.serializers import CourseCommentSerializer
from lib.permissions import IsOwnerOrReadOnly, IsOwnerOrReadOnlyForCourse
from lib.utils import BasePagination, get_object
from lib.response import Response
from notifications.views import notification_handler


User = get_user_model()


class CourseViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    list:
        课程列表
    retrieve:
        课程详情，以及关联课程列表
    create:
        添加课程
    destroy：
        删除课程
    """
    serializer_class = CourseSerializer
    pagination_class = BasePagination
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("degree", "category")
    search_fields = ("name", "desc", "detail")
    ordering_fields = ("students", "created_time", "fav_nums")
    lookup_field = 'id'

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            # 只允许删除和和更新自己的课程
            return [IsOwnerOrReadOnly()]

    def get_custom_serializer(self, queryset=None, many=True):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return self.get_serializer(queryset, many=many)

    def get_queryset(self):
        # return Course.objects.raw("SELECT d.*, GROUP_CONCAT((SELECT u.username FROM user_info u "
        #                           "WHERE u.id=uc.user_id LIMIT 10)) learn_users FROM ("
        #                           "SELECT c.*, GROUP_CONCAT(cl.`name`) lessons FROM course c "
        #                           "LEFT JOIN course_lesson cl ON c.id=cl.course_id GROUP BY cl.course_id) d "
        #                           "LEFT JOIN user_course uc ON d.id=uc.course_id GROUP BY uc.course_id")
        return Course.objects.all().select_related('org', 'user', 'teacher')

    def perform_create(self, serializer):
        obj = serializer.save()
        # 课程创建成功,通知其他用户
        others_user = User.objects.all().exclude(pk=self.request.user.id)
        notification_handler(actor=self.request.user, recipient=others_user, verb='B', action_object=obj)

    # @cache_response(cache='cache1', key_func=DefaultListKeyConstructor())
    def list(self, request, *args, **kwargs):
        courses = self.filter_queryset(self.get_queryset())
        serializer = self.get_custom_serializer(courses)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @cache_response(cache='cache1', key_func=DefaultObjectKeyConstructor())
    def retrieve(self, request, *args, **kwargs):
        # 是否收藏课程
        has_fav_course = False
        # 是否收藏机构
        has_fav_org = False
        course = self.get_object()

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            # 确定course.org不为None
            if course.org and UserFavorite.objects.filter(user=request.user, fav_id=course.org.id, fav_type=2):
                has_fav_org = True

        course.click_nums += 1
        course.save()

        # 查询tag关联除自身之外的课程
        rel_coures = Course.objects.filter(tag=course.tag).exclude(id=course.id)
        rel_coures_serializer = self.get_custom_serializer(rel_coures)
        course_serializer = self.get_serializer(course)

        return Response({
            'course': course_serializer.data,
            'related_coures': rel_coures_serializer.data,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org
        }, status=status.HTTP_200_OK)


class CourseResourceViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    list:
        all课程资源列表
        course_id: 某个课程资源列表
    retrieve:
        课程资源详情
    create:
        添加课程资源
    destroy：
        删除课程资源
    """
    serializer_class = CourseResourceSerializer
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("name", "course__degree", "course__category")
    lookup_field = 'id'

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        return CourseResource.objects.all().select_related('course', 'user')

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            resources = CourseResource.objects.filter(course__pk=int(course_id))
        else:
            resources = CourseResource.objects.all()
        resources_serializer = CourseResourceSerializer(resources, many=True)
        return Response(resources_serializer.data, status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    list:
        all课程章节列表
        course_id: 某个课程章节列表
    retrieve:
        章节详情
    create:
        添加章节
    destroy：
        删除章节
    """
    serializer_class = LessonSerializer
    pagination_class = BasePagination
    filter_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("created_time",)

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnlyForCourse()]

    def get_queryset(self):
        return Lesson.objects.all().select_related('course')

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            lessons = Lesson.objects.filter(course=int(course_id))
            lessons_serializer = LessonSerializer(lessons, many=True)
            return Response(lessons_serializer.data, status=status.HTTP_200_OK)
        else:
            return super(LessonViewSet, self).list(request, *args, **kwargs)


class VideoViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    list:
        all章节视频列表
        lesson_id: 某个章节的视频列表
    retrieve:
        视频详情
    create:
        添加章节视频
    destroy：
        删除章节视频
    """
    serializer_class = VideoSerializer
    pagination_class = BasePagination
    filter_fields = ("name", )
    search_fields = ("name",)
    ordering_fields = ("created_time",)

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnlyForCourse()]

    def get_queryset(self):
        return Video.objects.all().select_related('lesson')

    def list(self, request, *args, **kwargs):
        lesson_id = request.query_params.get('lesson_id', None)

        if lesson_id:
            videos = Video.objects.filter(lesson=int(lesson_id))
            video_serializer = self.get_serializer(videos, many=True)

            return Response(video_serializer.data, status=status.HTTP_200_OK)
        else:
            return super(VideoViewSet, self).list(request, *args, **kwargs)


class CourseCommentViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    """
    list:
        all评论列表
        course_id: 某个课程的评论列表
    retrieve:
        评论详情
    create:
        添加评论
    destroy：
        删除评论
    """
    serializer_class = CourseCommentSerializer
    pagination_class = BasePagination

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save()
        # 有课程评论则推送消息通知课程作者
        obj = get_object(Course, int(serializer.data['course']))
        notification_handler(self.request.user, obj.user, 'C', obj)

    def get_queryset(self):
        return CourseComment.objects.all().select_related('course')

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            course_comment = CourseComment.objects.filter(course=int(course_id)).order_by("created_time")
            course_comment_serializer = self.get_serializer(course_comment, many=True)

            return Response(course_comment_serializer.data, status=status.HTTP_200_OK)
        else:
            return super(CourseCommentViewSet, self).list(request, *args, **kwargs)
