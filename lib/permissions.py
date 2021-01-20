# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        # Instance must have an attribute named `user`.
        return obj.user == request.user


class IsOwnerOrReadOnlyForCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Instance must have an attribute named `course` or `lesson`.
        try:
            return obj.course.user == request.user
        except:
            return obj.lesson.course.user == request.user
