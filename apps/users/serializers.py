# -*- coding: utf-8 -*-
__author__ = 'wuhai'
from datetime import datetime, timedelta
import re

from django.db.models import Q
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

from captcha.fields import CaptchaField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class VerifySerializer(serializers.Serializer):
    # 指定验证类型
    send_type = serializers.IntegerField(required=True, write_only=True, label="类型",
                                         help_text="1(注册)，2(忘记密码)，3(修改邮箱)")
    code = serializers.CharField(required=True, write_only=True, label="验证码", help_text="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 })

    def validate_code(self, code):
        conn = get_redis_connection('default')
        db_code = conn.get(':'.join(['verify_code', self.initial_data["send_type"], self.initial_data["email"]]))
        if not db_code:
            raise serializers.ValidationError("请检查邮箱，类型是否正确, 验证码是否过期")
        if code != db_code.decode('utf8'):
            raise serializers.ValidationError("验证码错误")


class EmailModifySerializer(VerifySerializer):
    """邮箱修改"""
    email = serializers.EmailField(max_length=50, required=True, help_text="原邮箱")
    new_email = serializers.EmailField(max_length=50, required=True, write_only=True, help_text="新邮箱")

    def validate(self, attrs):
        if attrs['email'] == attrs['new_email']:
            raise serializers.ValidationError("新邮箱不能与之前的一致.")
        attrs['email'] = attrs['new_email']
        return attrs

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        return instance


class UserRegSerializer(VerifySerializer, serializers.ModelSerializer):
    """用户注册"""
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(),
                                                                 message="username already exists.")])
    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )
    email = serializers.EmailField(label="邮箱", help_text="邮箱", required=True, allow_blank=False,
                                   validators=[
                                       UniqueValidator(queryset=User.objects.all(), message="email already exists.")])

    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        # 用户名密码加密并激活
        user.set_password(validated_data["password"])
        user.is_active = True
        user.save()
        return user

    def validate(self, attrs):
        # 保存前删除code，send_type
        del attrs["code"], attrs['send_type']
        return attrs

    class Meta:
        model = User
        fields = ("send_type", "code", "username", "mobile", "email", "password")


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'gender', 'image', 'birthday', 'address', 'mobile']


class ResetPwdSerializer(VerifySerializer):
    """密码重置"""
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False)
    email = serializers.EmailField(label="邮箱", help_text="邮箱", required=True, allow_blank=False)

    password1 = serializers.CharField(
        style={'input_type': 'password'}, help_text="新密码", label="新密码", write_only=True,
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'}, help_text="确认密码", label="确认密码", write_only=True,
    )

    class Meta:
        fields = '__all__'

    def validate(self, attrs):
        if not User.objects.filter(username=attrs['username'], email=attrs['email']):
            raise serializers.ValidationError("用户不存在.")
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("密码不一致.")
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password1"])
        instance.save()
        return instance


class ModifyPwdSerializer(serializers.Serializer):
    """密码修改"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    password1 = serializers.CharField(style={'input_type': 'password'}, label="新密码", help_text="新密码", required=True,
                                      min_length=5, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, label="确认密码", help_text="确认密码", required=True,
                                      min_length=5, write_only=True)

    class Meta:
        fields = '__all__'

    def validate(self, attrs):
        if attrs['user'].check_password(attrs['password1']):
            raise serializers.ValidationError("不能与原密码一致.")
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError("新密码前后不一致.")
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password1"])
        instance.save()
        return instance
