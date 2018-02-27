# -*- coding: utf-8 -*-

import requests
import json

from api_test.config import *

class WordsAPITest(object):

    prefix_host = host
    url = ''
    data = ''
    headers = ''

    def post(self):
        json_data = json.dumps(self.data, ensure_ascii=False).encode("utf-8")
        print('[REQUEST][URL]', self.url, '[DATA]', json_data)
        rsp = requests.post(self.url, data=json_data, headers=self.headers, timeout=200)
        print('[RESPONSE]', rsp.text, rsp.headers)

    def get(self):
        json_data = json.dumps(self.data, ensure_ascii=False)
        print('[REQUEST][URL]', self.url, '[DATA]', json_data)
        rsp = requests.get(self.url, data=json_data, headers=self.headers)
        print('[RESPONSE]', rsp.text, rsp.headers)

    def add_word(self):
        self.url = self.prefix_host + '/words/synonym/add'
        self.headers = {
            "Cookie": session_id
        }
        self.data = {
            "meaning": "专横的",
            "word_type": "adj",
            "word_list": ["premptory", "despotic"]
        }
        self.post()

    def del_word(self):
        self.url = self.prefix_host + '/words/synonym/del'
        self.headers = {
            "Cookie": session_id
        }
        self.data = {
            "meaning": "专横的",
            "word_type": "adj",
            "word_list": ["premptory", "despotic"]
        }
        self.post()


if __name__ == '__main__':
    session_id = "session_id=22a6509e-0b49-11e8-af04-b8e8563ec9f2"
    api_test = WordsAPITest()
    api_test.add_word()
    # api_test.del_word()


