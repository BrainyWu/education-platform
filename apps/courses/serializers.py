# -*- coding: utf-8 -*-
__author__ = 'wuhai'
import json

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Course, CourseResource, Lesson, Video
from organization.serializers import CourseOrgSerializer
from lib.typetools import JsonEncoder

User = get_user_model()


# 自定义ModelSerializer，便于拓展
class CustomModelSerializer(serializers.ModelSerializer):

    @property
    def null_serializer(self):
        # 构建空序列化对象，不返回write_only=True的字段
        fields = self.get_fields()
        return {field: 'null' for field, f_type in fields.items() if not f_type.write_only}


class CourseResourceSerializer(CustomModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = CourseResource
        fields = "__all__"

    def validate(self, attrs):
        # 将当前登录用户传给model.user
        attrs['user'] = self.context['request'].user
        return attrs


class VideoSerializer(CustomModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"


class LessonSerializer(CustomModelSerializer):
    videos = serializers.SerializerMethodField(read_only=True)
    video = VideoSerializer(write_only=True, default=[], many=True)

    class Meta:
        model = Lesson
        fields = "__all__"
        # depth = 1

    def get_videos(self, obj):
        return obj.get_videos()

    def create(self, validated_data):
        videos = validated_data.pop('video')
        lesson = Lesson.objects.create(**validated_data)
        for video in videos:
            Video.objects.create(lesson=lesson, **video)
        return lesson


class CourseSerializer(CustomModelSerializer):
    name = serializers.CharField(max_length=50, allow_null=True, validators=[
                                 UniqueValidator(queryset=Course.objects.all(), message="课程名已存在")])
    user = serializers.CharField(read_only=True)
    # 学习课程的学生名
    learn_users = serializers.SerializerMethodField(read_only=True)
    # 课程章节名
    lessons = serializers.SerializerMethodField(read_only=True)
    click_nums = serializers.IntegerField(read_only=True)
    lesson = LessonSerializer(write_only=True, default=[], many=True)

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons(self, obj):
        return obj.get_lessons()

    def get_learn_users(self, obj):
        return obj.get_learn_users()

    def validate(self, attrs):
        attrs['user'] = self.context['request'].user
        return attrs

    def create(self, validated_data):
        lessons = validated_data.pop('lesson')
        course = Course.objects.create(**validated_data)
        for lesson in lessons:
            Lesson.objects.create(course=course, **lesson)
        return course
