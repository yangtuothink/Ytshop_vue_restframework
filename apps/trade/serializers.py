# _*_ coding:utf-8 _*_


from goods.serializers import GoodsSerializer
from trade.models import ShoppingCart, OrderGoods, OrderInfo

__author__ = "yangtuo"
__date__ = "2019/4/21 12:44"

from rest_framework import serializers

from goods.models import Goods


# 购物车商品详情
class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums")


# 购物车
class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于一",
                                        "required": "请选择购买数量"
                                    })
    # Serializer 的外键处理需要用此字段, 如果是 ModelSerializer 也可以使用此字段, 但是无需指定 queryset 即可
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    def create(self, validated_data):
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        # 判断当前是否已有记录
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)
        # 需要返回保存数据
        return existed

    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


# 订单商品详情
class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)

    #     alipay_url = serializers.SerializerMethodField(read_only=True)
    #
    #     def get_alipay_url(self, obj):
    #         alipay = AliPay(
    #             appid="",
    #             app_notify_url="http://127.0.0.1:8000/alipay/return/",
    #             app_private_key_path=private_key_path,
    #             alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #             debug=True,  # 默认False,
    #             return_url="http://127.0.0.1:8000/alipay/return/"
    #         )
    #
    #         url = alipay.direct_pay(
    #             subject=obj.order_sn,
    #             out_trade_no=obj.order_sn,
    #             total_amount=obj.order_mount,
    #         )
    #         re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    #
    #         return re_url
    #
    class Meta:
        model = OrderInfo
        fields = "__all__"


# 订单
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 订单的某些信息是不能自己修改的
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)

    #     alipay_url = serializers.SerializerMethodField(read_only=True)
    #
    #     def get_alipay_url(self, obj):
    #         alipay = AliPay(
    #             appid="",
    #             app_notify_url="http://127.0.0.1:8000/alipay/return/",
    #             app_private_key_path=private_key_path,
    #             alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #             debug=True,  # 默认False,
    #             return_url="http://127.0.0.1:8000/alipay/return/"
    #         )
    #
    #         url = alipay.direct_pay(
    #             subject=obj.order_sn,
    #             out_trade_no=obj.order_sn,
    #             total_amount=obj.order_mount,
    #         )
    #         re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    #
    #         return re_url

    # 生成订单号函数
    def generate_order_sn(self):
        # 当前时间+userid+随机数
        from time import strftime
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10, 99))
        return order_sn

    # 对订单号进行生成
    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"
