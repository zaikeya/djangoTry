import base64
import datetime
import hashlib
import json

import requests  #发http/https请求

class YunTongXin():

    base_url = 'https://app.cloopen.com:8883'

    def __init__(self,accountSid,accountToken,appId,templateId):
        self.accountSid = accountSid
        self.accountToken = accountToken
        self.appId = appId
        self.templateId = templateId

    def get_request_url(self,sig):
        # /2013-12-26/Accounts/{accountSid}/SMS/{funcdes}?sig={SigParameter}
        self.url = self.base_url + "/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s"%(self.accountSid,sig)
        return self.url

    def get_timestamp(self):
        #时间戳
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_sig(self,timestamp):
        #生成业务url中的url
        s = self.accountSid + self.accountToken + timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()

    def get_request_header(self,timestamp):
        #生成请求头
        s = self.accountSid + ':' + timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {
            'Accept':'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization':auth
        }


    def get_request_body(self,phone,code):

        return {
            "to":phone,
            "appId":self.appId,
            "templateId":self.templateId,
            "datas":[code,"3"]
        }


    def request_api(self,url,header,body):
        res = requests.post(url,headers=header,data=body)
        return res.text



    def run(self,phone,code):
        #获取时间戳
        timestamp = self.get_timestamp()
        #生成签名
        sig = self.get_sig(timestamp)
        #生成业务url
        url = self.get_request_url(sig)
        header = self.get_request_header(timestamp)
        body = self.get_request_body(phone,code)
        data = self.request_api(url,header,json.dumps(body))
        return data


# if __name__ == '__main__':
#
#       config = {
#           "accountSid" : "8aaf0708806a592701806a79cda00004",
#         "accountToken" : "9e23195157a142139085b6c66a175a2c",
#           "appId":"8aaf0708806a592701806a79cf6c000b",
#           "templateId":"1"
#       }
#
#       zky = YunTongXin(**config)
#       res = zky.run('17799703815',"990322")
#       print(res)
