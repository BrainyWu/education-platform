# -*- coding: utf-8 -*-
import json
import logging
from collections import OrderedDict

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework_extensions.key_constructor.constructors import DefaultListKeyConstructor, \
    DefaultObjectKeyConstructor
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
logger = logging.getLogger()


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

    @action(methods=['GET'], detail=True, url_path='rel', url_name='relate_coures')  # detail表示是否单一资源
    def get_relate_coures(self, request, *args, **kwargs):
        course = self.get_object()
        # 查询tag关联除自身之外的课程
        rel_coures = Course.objects.filter(tag=course.tag).exclude(id=course.id)
        serializer = self.get_custom_serializer(rel_coures)
        return Response({'rel_courses': serializer.data}, status=status.HTTP_200_OK)

    def get_object(self):
        obj = Course.objects.filter(id=self.kwargs.get('id')).first()
        if obj:
            self.check_object_permissions(self.request, obj)  # 单一资源检查删改权限
        return obj

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
        course_serializer = self.get_serializer(course)
        return Response({
            'course': course_serializer.data,
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
    lookup_field = 'id'

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnlyForCourse()]

    def get_queryset(self):
        return Lesson.objects.filter(course=self.kwargs.get('course_id')).select_related('course')

    def get_object(self):
        obj = Lesson.objects.filter(id=self.kwargs.get('id')).first()
        if obj:
            self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        lesson_id = self.kwargs.get('id')
        if lesson_id is None:
            return Response(code=-1, msg="lesson_id is required params.", status=status.HTTP_400_BAD_REQUEST)
        conn = get_redis_connection('cache1')
        cache_key = ':'.join(('lessons', lesson_id))
        cache_obj = conn.hgetall(cache_key)
        # 缓存存在则直接返回
        if cache_obj:
            return Response(cache_obj)
        # 缓存不存在则数据库中查找，数据库中有则返回，没有则设置一个空对象并设置过期时间防止穿透
        else:
            instance = self.get_object()
            if instance:
                serializer = self.get_serializer(instance)
                conn.hset(name=cache_key, mapping=serializer.data)
                return Response(serializer.data)
            else:
                # 组装一个空对象字典返回并设置60s过期
                cache_obj = getattr(self.serializer_class(), 'null_serializer')
                conn.hmset(cache_key, mapping=cache_obj)
                conn.expire(cache_key, 60)
                return Response(cache_obj)

    def list(self, request, *args, **kwargs):
        # 限制只获取某一个课程的章节
        course_id = self.kwargs.get('course_id')

        lessons = Lesson.objects.filter(course=int(course_id))
        lessons_serializer = LessonSerializer(lessons, many=True)
        return Response(lessons_serializer.data, status=status.HTTP_200_OK)


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
    filter_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("created_time",)
    lookup_field = 'id'

    def get_permissions(self):
        if self.action not in ["update", "destroy"]:
            return [IsAuthenticatedOrReadOnly()]
        else:
            return [IsOwnerOrReadOnlyForCourse()]

    def get_queryset(self):
        return Video.objects.all().select_related('lesson')

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        lesson_id = self.request.query_params.get('lesson_id')

        videos = Video.objects.get_course_videos(course_id)
        if lesson_id:
            # 获取指定章节视频
            videos = videos.get_lesson_videos(lesson_id)
        video_serializer = self.get_serializer(videos, many=True)
        return Response(video_serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        obj = Video.objects.filter(id=self.kwargs.get('id')).first()
        if obj:
            self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        video_id = self.kwargs.get('id')

        if video_id is None:
            return Response(code=-1, msg="video_id is required params.", status=status.HTTP_400_BAD_REQUEST)
        conn = get_redis_connection('cache1')
        cache_key = ':'.join(('videos', video_id))
        cache_obj = conn.hgetall(cache_key)
        if cache_obj:
            return Response(cache_obj)
        else:
            instance = self.get_object()
            if instance:
                serializer = self.get_serializer(instance)
                conn.hset(name=cache_key, mapping=serializer.data)
                return Response(serializer.data)
            else:
                cache_obj = getattr(self.serializer_class(), 'null_serializer')
                conn.hmset(cache_key, mapping=cache_obj)
                conn.expire(cache_key, 60)
                return Response(cache_obj)


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
        return CourseComment.objects.filter(course=self.kwargs.get('course_id')).select_related('course')

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')

        course_comment = CourseComment.objects.filter(course=int(course_id)).order_by("created_time")
        course_comment_serializer = self.get_serializer(course_comment, many=True)
        return Response(course_comment_serializer.data, status=status.HTTP_200_OK)
