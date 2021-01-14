# -*- coding: utf-8 -*-
__author__ = 'wuhai'
import re

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import UserFavorite, UserAsk, UserCourse, UserMessage, CourseComment, Banner
from courses.serializers import CourseSerializer
from lib.utils import get_object

User = get_user_model()


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = "__all__"


class UserMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    user_mobile = serializers.CharField(source='user.mobile')
    user_image = serializers.ImageField(source='user.image')

    class Meta:
        model = UserMessage
        fields = ('username', 'user_mobile', 'user_image', 'message', 'has_read', 'add_time')


class UserFavoriteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    user_mobile = serializers.CharField(source='user.mobile')
    user_image = serializers.ImageField(source='user.image')

    class Meta:
        model = UserFavorite
        fields = ('username', 'user_mobile', 'user_image', 'fav_id', 'fav_type', 'add_time')


class UserCourseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    user_mobile = serializers.CharField(source='user.mobile')
    user_image = serializers.ImageField(source='user.image')
    course = CourseSerializer(read_only=True, many=True)

    class Meta:
        model = UserCourse
        fields = ('username', 'user_mobile', 'user_image', 'course', 'add_time')


class CourseCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = CourseComment
        fields = "__all__"


class UserAskSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(allow_blank=True, max_length=11, min_length=11, error_messages={
        'max_length': '手机号码格式不正确',
        'min_length': '手机号码格式不正确',
    })

    def validate_mobile(self, mobile):
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")
        return mobile

    class Meta:
        model = UserAsk
        fields = "__all__"
