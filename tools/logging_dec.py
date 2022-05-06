from django.http import JsonResponse
from django.conf import settings
import jwt

from user.models import UserProfile


def logging_check(func):

    def wrap(request,*args, **kwargs):

        #获取token request.META.get('HTTP_AUTHORIZATION')
        token = str(request.META.get('HTTP_AUTHORIZATION'))
        if not token:
            result = {'code':403,'error':"请重新登录！"}
            return JsonResponse(result)
        #校验token
        try:
            res = jwt.decode(token,settings.JWT_TOKEN_KEY,algorithms=["HS256"])
        except Exception as e:
            print("==>>>>>>>======>",e)
            result = {'code': 403, 'error': "请重新登录！"}
            return JsonResponse(result)


        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user
        return func(request,*args, **kwargs)
    return wrap