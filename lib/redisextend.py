# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from django_redis import get_redis_connection
from rest_framework import mixins, viewsets, serializers


class CustomRedisClient:
    def __init__(self, conn=None):
        self.conn = conn
        self.cursor = conn.connection_pool.connection_kwargs['db']

    def scan_names(self, cursor=None, match=None):
        """获取redis db同一级目录下所有name, 便于批量操作"""
        if cursor is None:
            cursor = self.cursor
        pieces = [cursor]
        pieces.extend([b'MATCH', match])
        return self.conn.execute_command("SCAN", *pieces)[1]


# 自定义ModelSerializer，便于拓展
class CustomModelSerializer(serializers.ModelSerializer):

    @property
    def null_serializer(self):
        # 构建缓存空序列化对象，不返回write_only=True的字段
        fields = self.get_fields()
        return {field: 'null' for field, f_type in fields.items() if not f_type.write_only}


class CustomModelViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """redis cache model viewset"""
    conn = get_redis_connection()

    @property
    def custom_conn(self):
        # 自定义redis连接，拓展redis数据库函数
        return CustomRedisClient(self.conn)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.filter(**filter_kwargs).first()
        if obj:
            self.check_object_permissions(self.request, obj)
        return obj

    def cache_retrieve(self, cache_key=None, expire=60):
        cache_obj = self.conn.hgetall(cache_key)

        if not cache_obj:
            # 缓存不存在则数据库中查找，数据库中有则返回，没有则设置一个空对象并设置过期时间防止穿透
            instance = self.get_object()
            if instance:
                serializer = self.get_serializer(instance)
                self.conn.hset(name=cache_key, mapping=serializer.data)
                return serializer.data
            else:
                # 组装一个空对象字典返回并设置60s过期, 与THROTTLE_RATES保持一致
                cache_obj = getattr(self.serializer_class(), 'null_serializer')  # 确保serializer存在null_serializer属性
                self.conn.hmset(cache_key, mapping=cache_obj)
                self.conn.expire(cache_key, expire)
        return cache_obj


if __name__ == '__main__':
    pass
