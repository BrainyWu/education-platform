# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from datetime import datetime

from django.db.models.signals import post_delete, post_save
from django.core.cache import cache

from .models import Course, Lesson, Video, CourseResource


def change_updated_at(sender=None, instance=None, *args, **kwargs):
    # 信号量key的生成规则必须与keyconstructors UpdatedAtKeyBit一致，object更新时间维护才有效
    key = ':'.join([
        "ObjectUpdatedAt",
        instance.__module__,
        instance.get_queryset().model.__name__,
        instance.kwargs[instance.lookup_field],
    ])
    cache.set(key, datetime.utcnow())


def delete_updated_at(sender=None, instance=None, *args, **kwargs):
    key = ':'.join([
        "ObjectUpdatedAt",
        instance.__module__,
        instance.get_queryset().model.__name__,
        instance.kwargs[instance.lookup_field],
    ])
    cache.delete(key)


post_save.connect(receiver=change_updated_at, sender=Course)
post_delete.connect(receiver=delete_updated_at, sender=Course)

post_save.connect(receiver=change_updated_at, sender=Lesson)
post_delete.connect(receiver=delete_updated_at, sender=Lesson)

post_save.connect(receiver=change_updated_at, sender=Video)
post_delete.connect(receiver=delete_updated_at, sender=Video)
