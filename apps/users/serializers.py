# _*_ coding:utf-8 _*_
__author__ = "yangtuo"
__date__ = "2019/4/15 20:25"

import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
from datetime import timedelta
from rest_framework.validators import UniqueValidator

from .models import VerifyCode
from YtShop.settings import REGEX_MOBILE

User = get_user_model()


# 手机验证序列化组件
# 不使用 ModelSerializer, 并不需要所有的字段, 会有麻烦
class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    # 验证手机号码
    # validate_ + 字段名 的格式命名
    def validate_mobile(self, mobile):

        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        # 验证码发送频率
        # 当前时间减去一分钟( 倒退一分钟 ), 然后发送时间要大于这个时间, 表示还在一分钟内
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")
        return mobile


# 用户详情信息序列化类
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")


# 用户注册
class UserRegSerializer(serializers.ModelSerializer):
    """
    max_length      最大长度
    min_length      最小长度
    label           显示名字
    help_text       帮助提示信息
    error_messages  错误类型映射提示
        blank         空字段提示
        required      必填字段提示
        max_length    超长度提示
        min_length    过短提示
    write_only      只读, 序列化的时候忽略字段, 不再返回给前端页面, 用于去除关键信息(密码等)或者某些不必要字段(验证码)
    style           更改输入标签显示类型
    validators      可以指明一些默认的约束类
        UniqueValidator             约束唯一
        UniqueTogetherValidator     联合约束唯一
        UniqueForMonthValidator
        UniqueForDateValidator
        UniqueForYearValidator
        ....
    """
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    # validators 可以指明一些默认的约束类, 此处的 UniqueValidator 表示唯一约束限制不能重名
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    # style 可以设置为密文状态
    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    # 用户表中的 password 是需要加密后再保存的, 次数需要重写一次 create 方法
    # 当然也可以不这样做, 这里的操作利用 django 的信号来处理, 详情见 signals.py
    # def create(self, validated_data):
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)
    #     user.set_password(validated_data["password"])
    #     user.save()
    #     return user

    # 对验证码的验证处理
    # validate_ + 字段对个别字段进行单一处理
    def validate_code(self, code):

        # 如果使用 get 方式需要处理两个异常, 分别是查找到多个信息的情况以及查询到0信息的情况的异常
        # 但是使用 filter 方式查到多个就以列表方式返回, 如果查询不到数据就会返回空值, 各方面都很方便
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass

        # 前端传过来的所有的数据都在, initial_data 字典里面 ,
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]  # 时间倒叙排序后的的第一条就是最新的一条
            # 当前时间回退5分钟
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            # 最后一条短信记录的发出时间小于5分钟前, 表示是5分钟前发送的, 表示过期
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")
            # 根据记录的 验证码 比对判断
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
            # return code  # 没必要保存验证码记录, 仅仅是用作验证
        else:
            raise serializers.ValidationError("验证码错误")

    # 对所有的字段进行限制
    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]  # 重命名一下
        del attrs["code"]  # 删除无用字段
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
