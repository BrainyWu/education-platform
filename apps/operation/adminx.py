# -*- coding: utf-8 -*-
__author__ = 'wuhai'

import xadmin

from .models import UserAsk, UserCourse, UserMessage, CourseComment, UserFavorite, Banner


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'created_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'created_time']


class UserAskAdmin(object):
    list_display = ['name', 'mobile', 'course_name', 'created_time']
    search_fields = ['name', 'mobile', 'course_name']
    list_filter = ['name', 'mobile', 'course_name', 'created_time']
    model_icon = 'fa fa-question-circle'


class UserCourseAdmin(object):
    list_display = ['user', 'course', 'created_time']
    search_fields = ['user', 'course']
    list_filter = ['user', 'course', 'created_time']
    model_icon = 'fa fa-address-book'


class UserMessageAdmin(object):
    list_display = ['user', 'message', 'has_read', 'created_time']
    search_fields = ['user', 'message', 'has_read']
    list_filter = ['user', 'message', 'has_read', 'created_time']
    model_icon = 'fa fa-envelope-o'


class CourseCommentAdmin(object):
    list_display = ['user', 'course', 'comments', 'created_time']
    search_fields = ['user', 'course', 'comments']
    list_filter = ['user', 'course', 'comments', 'created_time']
    model_icon = 'fa fa-comment'


class UserFavoriteAdmin(object):
    list_display = ['user', 'fav_id', 'fav_type', 'created_time']
    search_fields = ['user', 'fav_id', 'fav_type']
    list_filter = ['user', 'fav_id', 'fav_type', 'created_time']
    model_icon = 'fa fa-heart'


xadmin.site.register(UserAsk, UserAskAdmin)
xadmin.site.register(UserCourse, UserCourseAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(CourseComment, CourseCommentAdmin)
xadmin.site.register(UserFavorite, UserFavoriteAdmin)
xadmin.site.register(Banner, BannerAdmin)
