# _*_ coding:utf-8 _*_
__author__ = "yangtuo"
__date__ = "2019/4/12 15:07"

import django_filters
from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    # 自定制的 过滤字段
    price_min = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')  # 设置模糊查询, i 在前表示忽略大小写
    # 模糊搜索没必要在这里进行操作, 可以利用 drf 自带的 搜索方式实现模糊查询

    class Meta:
        model = Goods
        fields = ["price_min", "price_max", "name"]
