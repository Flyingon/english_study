# -*- coding: utf-8 -*-

import requests
import json

from api_test.config import *

class LoginAPITest(object):
    prefix_host = host
    url = ''
    data = ''
    headers = ''

    def post(self):
        json_data = json.dumps(self.data, ensure_ascii=False)
        print('[REQUEST][URL]', self.url, '[DATA]', json_data)
        rsp = requests.post(self.url, data=json_data, headers=self.headers, timeout=200)
        print('[RESPONSE]', rsp.content.decode('utf-8'), rsp.headers)

    def get(self):
        json_data = json.dumps(self.data, ensure_ascii=False)
        print('[REQUEST][URL]', self.url, '[DATA]', json_data)
        rsp = requests.get(self.url, data=json_data, headers=self.headers)
        print('[RESPONSE]', rsp.content, rsp.headers)

    def add_user(self):
        self.url = self.prefix_host + '/user/add'
        self.data = {
            "account": "yzy",
            "password": "yzy105178"
        }
        self.post()

    def del_user(self):
        self.url = self.prefix_host + '/user/del'
        self.headers = {
            "Cookie":"session_id=22a6509e-0b49-11e8-af04-b8e8563ec9f2"
        }
        self.data = {
            "account": "yzy",
        }
        self.post()

    def login(self):
        self.url = self.prefix_host + '/login'
        self.data = {
            "account": "yzy",
            "password": "123"
        }
        self.post()

    def logout(self):
        self.headers = {
            "Cookie":"session_id=58e1f11c-0b13-11e8-a60c-b8e8563ec9f2"
        }
        self.url = self.prefix_host + '/logout'
        self.data = {
        }
        self.post()

    def getuser(self):
        self.headers = {
            "Cookie":"session_id=22a6509e-0b49-11e8-af04-b8e8563ec9f2"
        }
        self.url = self.prefix_host + '/get_user'
        self.data = {
        }
        self.post()


if __name__ == '__main__':
    api_test = LoginAPITest()
    api_test.add_user()
    # api_test.del_user()
    # api_test.login()
    # api_test.logout()
    # api_test.getuser()

