# _*_ coding:utf-8 _*_
__author__ = "yangtuo"
__date__ = "2019/4/15 20:25"

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)  # post_save 信号类型, sender 能触发信号的模型
def create_user(sender, instance=None, created=False, **kwargs):    # created 是否新建( update 就不会被识别 )
    # instance 表示保存对象, 在这里是被保存的 user 对象
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()
        # Token.objects.create(user=instance)
        # user 对象的保存一般是要伴随着 token 的, 这里已经使用 JWT 方式了, 因此就不需要这种 token 了.


"""

created  是否是新建
"""
