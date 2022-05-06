import json
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from tools.logging_dec import logging_check
from .models import UserProfile
import hashlib
import random
from django.core.cache import cache
from tools.sms import YunTongXin
# Create your views here.

#FBV
@logging_check
def users_views(request,username):
    if request.method != 'POST':
        result = {'code':10103,'error':"请使用其他方式！"}
        return JsonResponse(result)

    user = request.myuser

    avatar = request.FILES['avatar']
    user.avatar = avatar
    user.save()
    return JsonResponse({'code':200})

#CBVm
#更灵活，可继承
#对未定义的http请求，返回405
class UserViews(View):
    @method_decorator(logging_check)
    def get(self,request,username=None):
        if username:
            user = request.myuser
            result = {'code':200,'username':username,
                'data':{
                    'info':user.info,
                    'sign':user.sign,
                    'nickname':user.nickname,
                    'avatar':str(user.avatar),
                }}
            return JsonResponse(result)

        else:

            pass


        return JsonResponse({'code':200 ,'msg':'test'})

    def post(self,request):
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        email = json_obj['email']
        phone = json_obj['phone']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        sms_num = json_obj['sms_num']


        if password_1 != password_2:
            result = {'code':10100,'error':'两次密码不一样！'}
            return JsonResponse(result)

        #比对验证码
        old_code = cache.get('sms_%s'%(phone))
        if not old_code:
            result = {'code':10110,'error':'验证码已过期！'}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {'code': 10111, 'error': '验证码错误！'}
            return JsonResponse(result)

        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            result = {'code': 10101, 'error': '该用户名已经被使用！'}
            return JsonResponse(result)

        p_m = hashlib.md5()
        p_m.update(password_1.encode()),
        UserProfile.objects.create(username=username,nickname=username,password=p_m.hexdigest(),email=email,phone=phone)
        result = {'code':200,'username':username,'data':{}}
        return JsonResponse(result)

    @method_decorator(logging_check)
    def put(self,request,username=None):
        json_str = request.body
        json_obj = json.loads(json_str)

        user = request.myuser

        user.sign = json_obj['sign']
        user.info = json_obj['info']
        user.nickname = json_obj['nickname']

        user.save()
        return JsonResponse({'code':200})

def sms_view(request):

    if request.method != 'POST':
        result = {'code':10108,'error':'Please use POST!'}
        return  JsonResponse(result)

    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']

    #生成随机码
    code = random.randint(1000,9999)
    print('phone',phone,'code',code)
    #存储随机码  django_redis
    cache_key = 'sms_%s'%(phone)
    #检查是否有发过的，且未过期
    old_code = cache.get(cache_key)
    if old_code:
        return JsonResponse({'code':10111,'error':'验证码已发送，请稍后再试！'})

    cache.set(cache_key,code,60)
    #发送随机码 -》 短信
    send_sms(phone,code)
    return JsonResponse({'code': 200})

def send_sms(phone,code):
    config = {
        "accountSid": "8aaf0708806a592701806a79cda00004",
        "accountToken": "9e23195157a142139085b6c66a175a2c",
        "appId": "8aaf0708806a592701806a79cf6c000b",
        "templateId": "1"
    }

    zky = YunTongXin(**config)
    zky.run(phone, code)