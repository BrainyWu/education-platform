# -*- coding: utf-8 -*-
__author__ = 'wuhai'

from rest_framework import serializers
from django.db.models import Q

from .models import CourseOrg, OrgCity, Teacher


class CourseOrgSerializer(serializers.ModelSerializer):
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
