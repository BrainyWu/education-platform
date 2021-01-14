# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import mixins, viewsets, filters, status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.decorators import action

from .models import Course, CourseResource, Lesson, Video
from .serializers import CourseSerializer, LessonSerializer, CourseResourceSerializer, VideoSerializer
from operation.models import UserFavorite, CourseComment, UserCourse
from operation.serializers import CourseCommentSerializer
from lib.utils import BasePagination, get_object
from lib.response import Response


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    throttle_classes = (UserRateThrottle, AnonRateThrottle)
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("degree", "category")
    search_fields = ("name", "desc", "detail")
    ordering_fields = ("students", "click_nums", "add_time", "fav_nums")
    lookup_field = 'id'

    def get_custom_serializer(self, queryset=None, many=True):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return self.get_serializer(queryset, many=many)

    def get_queryset(self):
        return Course.objects.all()

    def list(self, request, *args, **kwargs):
        courses = self.filter_queryset(self.get_queryset())

        courses_serializer = self.get_custom_serializer(courses)
        len_courses = len(courses)

        return Response({
            'all_courses': courses_serializer.data,
            'total': len_courses,
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # 是否收藏课程
        has_fav_course = False
        # 是否收藏机构
        has_fav_org = False
        course = self.get_object()

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            # 确定course.course_org不为None
            if course.course_org and UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("name", "course__degree", "course__category")
    lookup_field = 'id'

    def get_queryset(self):
        return CourseResource.objects.all()

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            resources = CourseResource.objects.filter(course__pk=int(course_id))
        else:
            resources = CourseResource.objects.all()
        resources_serializer = CourseResourceSerializer(resources, many=True)
        return Response({
            'course_resources': resources_serializer.data,
        }, status=status.HTTP_200_OK)


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("add_time",)

    def get_queryset(self):
        return Lesson.objects.all()

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            course = Course.objects.get(id=int(course_id))
            lessons = Lesson.objects.filter(course=int(course_id))

            course_serializer = CourseSerializer(course)
            lessons_serializer = LessonSerializer(lessons, many=True)

            return Response({
                'course': course_serializer.data,
                'lessons': lessons_serializer.data,
            }, status=status.HTTP_200_OK)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ("name", "name")
    search_fields = ("name",)
    ordering_fields = ("add_time",)

    def get_queryset(self):
        return Video.objects.all()

    def list(self, request, *args, **kwargs):
        lesson_id = request.query_params.get('lesson_id', None)

        if lesson_id:
            videos = Video.objects.filter(lesson=int(lesson_id))
            video_serializer = self.get_serializer(videos, many=True)

            return Response({
                'videos': video_serializer.data,
            }, status=status.HTTP_200_OK)
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
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return CourseComment.objects.all()

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id', None)

        if course_id:
            course_comment = CourseComment.objects.filter(course=int(course_id)).order_by("add_time")
            course_comment_serializer = self.get_serializer(course_comment, many=True)

            return Response({
                'course_comments': course_comment_serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return super(CourseCommentViewSet, self).list(request, *args, **kwargs)
