"""YtShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

# from django.contrib import admin
import xadmin
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from goods.views import GoodsListViewset, CategoryViewset
from users.views import SmsCodeViewset, UserViewset
from YtShop.settings import MEDIA_ROOT
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset

# 使用 routers 的方式
router = DefaultRouter()

# 配置 goods 的 url
# 注册后就不需要每个都写一个 url 了.这样集合一个就可以了
router.register(r'goods', GoodsListViewset, base_name="goods")

# 配置 categorys 的 url
router.register(r'categorys', CategoryViewset, base_name="categorys")

# 配置手机验证码发送 的 url
router.register(r'codes', SmsCodeViewset, base_name="codes")

# 配置用户注册的 url
router.register(r'users', UserViewset, base_name="users")

# 配置用户收藏的 url
router.register(r'userfavs', UserFavViewset, base_name="userfavs")

# 留言
router.register(r'messages', LeavingMessageViewset, base_name="messages")

# 收货地址
router.register(r'address', AddressViewset, base_name="address")

# 利用 routers 之后就不需要这样手动指定了
# 此方法必须要求继承 GenericViewSet 或者 ModelViewSet
# 这样可以手动指定相关的方法
# goods_list = GoodsListViewset.as_view({
#     'get': 'list',
# })

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^xadmin/', xadmin.site.urls),

    # api 登录
    url(r'^api-auth/', include('rest_framework.urls')),

    # media 路径请求
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # api 接口文档
    url(r'docs/', include_docs_urls(title="羊驼生鲜")),  # 此处的 url 不要加 $

    # DRF 自带的 token 认证
    # url(r'^api-token-auth/', views.obtain_auth_token),

    # DRF JWT 认证
    url(r'^login/', obtain_jwt_token),

    # 所有注册 URL
    # url(r'goods/$', GoodsListViewset.as_view(), name="good-list"),  # 继承了 viewsets 之后, 重写了 as_view, 因此不需要这样做了
    # url(r'goods/$', goods_list, name="good-list"),  # 利用了 routers 之后也不需要这么做了
    url(r'^', include(router.urls)),  # 使用了routers 之后极大的简介, 不需要手动指定 请求方式的映射了
    # 而且此方法涵盖了所有的 api 接口, 如果想添加接口就在 DefaultRouter() 里面注册去即可
]
