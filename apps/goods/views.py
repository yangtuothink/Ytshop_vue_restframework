from .serializers import GoodsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Goods
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination


# 自定义重写 分页 组件
class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


class GoodsListView(generics.ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination

    # 如果继承了 ListAPIView 连 get 都不需要重写啦 generics.ListAPIView
    # 如果不重写就会认为不接收此类型请求
    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    # 继承了 mixins 不需要手动写啦  mixins.ListModelMixin, generics.GenericAPIView
    # def get(self, request, format=None):
    #     goods = Goods.objects.all()[:10]
    #     goods_serializer = GoodsSerializer(goods, many=True)
    #     return Response(goods_serializer.data)

    # 写一下看看而已, 商品的上传通过 后台即可, 用户不能这样操作, 关闭此接口
    # def post(self, request, ):
    #     goods_serializer = GoodsSerializer(data=request.data)
    #     if goods_serializer.is_valid():
    #         goods_serializer.save()
    #         return Response(goods_serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(goods_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
