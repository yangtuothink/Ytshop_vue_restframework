# _*_ coding:utf-8 _*_
__author__ = "yangtuo"
__date__ = "2019/4/12 15:07"

import django_filters
from django.db.models import Q

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    商品的过滤类
    """
    # 自定制的 过滤字段
    pricemin = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    pricemax = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')  # 设置模糊查询, i 在前表示忽略大小写
    # 模糊搜索没必要在这里进行操作, 可以利用 drf 自带的 搜索方式实现模糊查询

    top_category = django_filters.NumberFilter(method='top_category_filter')  # method 可以指定函数

    # 筛选出来所有的一级分类
    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ["pricemin", "pricemax"]
