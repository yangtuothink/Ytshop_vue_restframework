from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

# Create your views here.

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
