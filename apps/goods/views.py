from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication

from .models import Goods, GoodsCategory
from .serializers import GoodsSerializer, CategorySerializer
from .filters import GoodsFilter


# 自定义重写 分页 组件
class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100
    # ordering = ['id']


# 商品列表
class GoodsListViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Goods.objects.all()  # 筛选  get_queryset 方法和此属性等效
    serializer_class = GoodsSerializer  # 序列化
    pagination_class = GoodsPagination  # 分页
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    """
    利用 django-filter 进行过滤
    利用 drf自带的 filters.SearchFilter 进行搜索
    利用 drf自带的 filters.OrderingFilter 进行排序
    """
    # filterset_fields = ('name', 'shop_price')  # 设置过滤字段, 此设置无法设置不存在的字段
    filterset_class = GoodsFilter  # 设置自定义的过滤类, 可以设置自己定制的字段了, 与 filterset_fields 相互覆盖
    search_fields = ('name', 'goods_brief', 'goods_desc')  # 设置 搜索字段
    """
    '^' 内容开头匹配
    '=' 精准匹配
    '@' 全文搜索（目前只支持Django的MySQL后端。）
    '$' 后跟正则表达式
    
    search_fields = ('=name', ) 
    """
    ordering_fields = ('sold_num', 'shop_price')  # 设置排序字段
    # authentication_classes = (TokenAuthentication,)  # 设置当前视图的认证方式


    # queryset 属性写了的话就不需要重写此方法
    # 但是如果想自定义过滤规则则需要重写 get_queryset 方法
    # def get_queryset(self):
    #     queryset = Goods.objects.all()  # 此处是隐式查找, 不用担心数据过大, 不循环就不会真正的查
    #     price_min = self.request.query_params.get("pirce_min", 0)  # 接收参数中的 pirce_min
    #     if price_min:
    #         queryset = queryset.filter(shop_price__gt=int(price_min))  # 查比 pirce_min 大的
    #     return queryset  # 整个逻辑码下来还是有点繁琐 因此 django-filter 对此进行了相应的封装

    # 如果继承了 ListAPIView 连 get 都不需要重写啦 <generics.ListAPIView>
    # 如果不重写就会认为不接收此类型请求
    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)

    # 继承了 mixins 不需要手动写啦  <mixins.ListModelMixin, generics.GenericAPIView>
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

    """
    继承结构 (功能↓) (封装↑)
            ModelViewSet/ReadOnlyModelViewSet
    generics.xxx                        GenericViewSet
    mixins.xxx                          GenericAPIView                              
                                        APIView  
                                        ViewSetMixin

                       
    基础的四个功能组件(每个都有自己独有功能)              
        APIView(View) 
            啥都没有, 全部手写去吧
        
        ViewSetMixin(object)
            提供了 as_view 的重写
            以及 initialize_request 里面很多的 action 
        
        mixins.xxx(object)
            提供以下的 5 个基础的增删改查方法, 
            CreateModelMixin - create()    post() 
            ListModelMixin - list()    get()
            RetrieveModelMixin - retrieve()   patch() 
            DestroyModelMixin - destroy()   delete()
            UpdateModelMixin - update()    put() 
            
        GenericAPIView(views.APIView) 
            提供了以下字段的封装, 不需要手写了
            queryset = None             数据库对象
            serializer_class = None     序列化对象
            lookup_field = 'pk'         默认查询字段, 默认是 id 
            lookup_url_kwarg = None     查询单一数据时URL中的参数关键字名称, 默认与look_field相同
            filter_backends = api_settings.DEFAULT_FILTER_BACKENDS      过滤
            pagination_class = api_settings.DEFAULT_PAGINATION_CLASS    分页器选择
    
    进阶的两个(对基础组件的一层封装) 
        GenericViewSet(ViewSetMixin, generics.GenericAPIView) 
            集合了 as_view 以及 可写参数
    
        generics.xxxx.....(mixins.xxxxx,GenericAPIView)
            各式的组合增删改查, 以及附加参数功能
            CreateAPIView(mixins.CreateModelMixin,GenericAPIView)
            ListAPIView(mixins.ListModelMixin,GenericAPIView)  
            RetrieveAPIView(mixins.RetrieveModelMixin,GenericAPIView)
            DestroyAPIView(mixins.DestroyModelMixin,GenericAPIView)
            UpdateAPIView(mixins.UpdateModelMixin,GenericAPIView)
            ListCreateAPIView(mixins.ListModelMixin,mixins.CreateModelMixin,GenericAPIView)
            RetrieveUpdateAPIView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,GenericAPIView)
            RetrieveDestroyAPIView(mixins.RetrieveModelMixin,mixins.DestroyModelMixin,GenericAPIView)
            RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,GenericAPIView)
        
    终极的两个(二级封装更加方便了)
        ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet)
            其他都有, 只能读取
        ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet)
            全部都有, 集合了所有的请求方式
    
    视图继承的选择
        一阶段 
            View 你这是在用 django
        二阶段
            APIView 在用 drf 了.但是是最基础的方式
        三阶段
            GenericAPIView 很多参数可以用了, 但是所有方法自己写
        四阶段
            GenericAPIView + mixins 能用参数了, 不用写各请求的逻辑了. 但是还要写个壳子
        五阶段
            GenericAPIView + generics.xxx 能用参数, 而且灵活组合自己的请求类型, 壳子也不用写了
        六阶段
            GenericViewSet + generics.xxx 能用参数, 灵活组请求类型, 重写了as_view, 获得高级路由功能
        七阶段
            ReadOnlyModelViewSet 前面有的我都有. 但是我只能读
        八阶段
            ModelViewSet 我全都有
    """


# 商品类型
class CategoryViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    retrieve:
        获取商品分类详情
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer
