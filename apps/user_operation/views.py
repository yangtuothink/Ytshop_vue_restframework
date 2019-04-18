from rest_framework import viewsets
from rest_framework import mixins

from .serializers import UserFavSerializer
from .models import UserFav


# 用户收藏功能
class UserFavViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
