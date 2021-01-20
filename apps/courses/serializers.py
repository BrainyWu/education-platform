# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Course, CourseResource, Lesson, Video
from organization.serializers import CourseOrgSerializer

User = get_user_model()


class CourseResourceSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = CourseResource
        fields = "__all__"

    def validate(self, attrs):
        # 将当前登录用户传给model.user
        attrs['user'] = self.context['request'].user
        return attrs


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True, many=True)

    class Meta:
        model = Lesson
        fields = "__all__"
        # depth = 1

    def create(self, validated_data):
        videos = validated_data.pop('video', [])
        lesson = Lesson.objects.create(**validated_data)
        for video in videos:
            Video.objects.create(lesson=lesson, **video)
        return lesson


class CourseSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    click_nums = serializers.IntegerField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True)
    lesson =LessonSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = "__all__"

    def validate(self, attrs):
        attrs['user'] = serializers.CurrentUserDefault()
        return attrs

    def create(self, validated_data):
        lessons = validated_data.pop('lesson', [])
        course = Course.objects.create(**validated_data)
        for lesson in lessons:
            Lesson.objects.create(course=course, **lesson)
        return course
