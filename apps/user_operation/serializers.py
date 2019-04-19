# _*_ coding:utf-8 _*_
from rest_framework.validators import UniqueTogetherValidator

from goods.serializers import GoodsSerializer

__author__ = "yangtuo"
__date__ = "2019/4/18 20:31"

from rest_framework import serializers

from .models import UserFav, UserLeavingMessage, UserAddress


# 收藏详情
class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ("goods", "id")


# 用户收藏
class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFav
        # 联合唯一可以在 model 中创建的时候进行操作, 通过 ModelSerializer 自然会帮你完成验证
        # 也可以在这里完成, 注意是在 Meta 中进行设置, 因为这是多字段的处理
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏过了"
            )
        ]
        fields = ("user", "goods", "id")  # 删除的需要因此加上 id, 这样方便删除操作


# 用户留言
class LeavingMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 留言的时间不能自己指定, 应该是系统自动根据当前的时间, 因此设置为只读
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ("user", "message_type", "subject", "message", "file", "id", "add_time")


# 收货地址
class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserAddress
        fields = ("id", "user", "province", "city", "district", "address", "signer_name", "add_time", "signer_mobile")
