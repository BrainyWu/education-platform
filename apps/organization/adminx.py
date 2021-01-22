# -*- coding: utf-8 -*-
__author__ = 'wuhai'
import xadmin

from .models import OrgCity, CourseOrg, Teacher


class OrgCityAdmin(object):
    list_display = ['name', 'desc', 'created_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'created_time']
    model_icon = 'fa fa-university'


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']
    relfield_style = 'fk-ajax'
    style_fields = {"desc": "ueditor"}
    model_icon = 'fa fa-university'


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']
    model_icon = 'fa fa-user-md'


xadmin.site.register(OrgCity, OrgCityAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)
