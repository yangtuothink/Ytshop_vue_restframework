# _*_ coding:utf-8 _*_
__author__ = "yangtuo"
__date__ = "2019/4/9 21:26"
from django.views.generic.base import View
from goods.models import Goods


# from django.views.generic import ListView


class GoodsListView(View):
    def get(self, request):
        """
        通过django的view实现商品列表页
        :param request:
        :return:
        """

        json_list = []
        goods = Goods.objects.all()[:10]

        # 特么最基础的方式, 每个字段手写 创造字典
        # for good in goods:
        #     json_dict = {}
        #     json_dict["name"] = good.name
        #     json_dict["category"] = good.category.name
        #     json_dict["market_price"] = good.market_price
        #     json_dict["add_time"] = good.add_time
        #     json_list.append(json_dict)

        # 此方法可以将 所有的 字段直接转换成 dict 比上面简单一点
        # 但是此方法转换字段的时候 某些字段是无法转换的. 因此会报错
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        # django 的最终解决方案是 serializers
        import json
        from django.core import serializers
        json_data = serializers.serialize('json', goods)  # 会生成一个字符串
        json_data = json.loads(json_data)
        from django.http import HttpResponse, JsonResponse
        # JsonResponse 自带了 dumps 所以直接传入字典即可
        return JsonResponse(json_data, safe=False)
