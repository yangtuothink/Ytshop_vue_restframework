from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from trade.models import ShoppingCart
from trade.serializers import ShopCartSerializer, ShopCartDetailSerializer
from utils.permissions import IsOwnerOrReadOnly


# 购物车
class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    list:
        获取购物车详情
    create：
        加入购物车
    delete：
        删除购物记录
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ShopCartSerializer
    # 我们修改的是要的是 goods 的id 而不是这条记录本身的 id
    lookup_field = "goods_id"

    # 分流 序列化组件
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)
