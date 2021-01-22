# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from rest_framework import serializers
from django.db.models import Q

from .models import CourseOrg, OrgCity, Teacher


class CourseOrgSerializer(serializers.ModelSerializer):
    # 统计机构老师数量
    teacher_nums = serializers.SerializerMethodField(read_only=True)

    def get_teacher_nums(self, obj):
        return obj.get_teacher_nums()

    class Meta:
        model = CourseOrg
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgCity
        fields = "__all__"
