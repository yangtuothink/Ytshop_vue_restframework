from random import choice

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, status, mixins, permissions, authentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from YtShop.settings import APIKEY
from users.models import VerifyCode
from users.serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from utils.yunpianwang import YunPian

User = get_user_model()


# 自定义用户验证
class CustomBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            # 前端的用户传递过来的密码和数据库的保存密码是不一致的, 因此需要使用 check_password 的方式进行比对
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 发送短信验证码
class SmsCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SmsSerializer

    # 生成四位数字的验证码
    def generate_code(self):

        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    # 重写 create 方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 验证后即可取出数据
        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)

        code = self.generate_code()

        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 确认无误后需要保存数据库中
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


# 用户视图
class UserViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    # 用户中心的个人详情数据不能再基于统一设置的 UserRegSerializer 了
    # 用户注册和 用户详情分为了两个序列化组件
    # self.action 必须要继承了 ViewSetMixin 才有此功能
    # get_serializer_class 的源码位置在 GenericAPIView 中
    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer
        return UserDetailSerializer

    # permission_classes = (permissions.IsAuthenticated, )  # 因为根据类型的不同权限的认证也不同, 不能再统一设置了
    # get_permissions 的源码在 APIview 中
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        return []

    # 重写 create 函数来完成注册后自动登录功能
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        """
        此处重写的源码分析以及 相关的逻辑
        详情点击此博客 
        https://www.cnblogs.com/shijieli/p/10726194.html
        """
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        # token 的添加只能用此方法, 此方法通过源码阅读查找到位置为
        re_dict["token"] = jwt_encode_handler(payload)
        # 自定义一个字段加入进去
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 因为要涉及到 个人中心的操作需要传递过去 用户的 id, 重写 get_object 来实现
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
