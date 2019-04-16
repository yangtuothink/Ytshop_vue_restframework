from random import choice

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, status, mixins
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from YtShop.settings import APIKEY
from users.models import VerifyCode
from users.serializers import SmsSerializer
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
class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
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



