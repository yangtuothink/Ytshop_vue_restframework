# _*_ coding:utf-8 _*_
from YtShop.settings import APIKEY

__author__ = "yangtuo"
__date__ = "2019/4/15 20:25"
import requests
import json


# 云片网短信发送功能类
class YunPian(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        parmas = {
            "apikey": self.api_key,
            "mobile": mobile,
            "text": "您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }

        response = requests.post(self.single_send_url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict


if __name__ == "__main__":
    yun_pian = YunPian(APIKEY)
    yun_pian.send_sms("2019", "")  # 参数为 code 以及 mobile
