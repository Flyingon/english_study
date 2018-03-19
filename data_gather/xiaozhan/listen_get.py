# -*- coding: utf-8 -*-

import re
import copy
import math
import time
import requests
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag, NavigableString
import html2text

from model.data_model import *

def listen_basic_get():

    l1 = [4,8,12,16,20,24,28,32,36,40,44,48,53]
    review_dict = {}
    for page_id in l1:
        url = 'http://top.zhan.com/toefl/listen/alltpo%s.html' %page_id
        rsp = requests.get(url)
        soup = BeautifulSoup(rsp.text, 'lxml')
        item_content_list = soup.find_all(class_='item_content')
        listens = []
        for item_content in item_content_list:
            # print(item_content)
            data = {}
            data['pic'] = item_content.find(class_='cover_img').attrs.get("src")
            data['classify'] = item_content.find(class_='item_img_tips').find(class_='left').contents[0]
            data['title_cn'] = item_content.find(class_='item_text_cn').contents[0]
            data['title_en'] = item_content.find(class_='item_text_en').contents[0]
            data['source'] = re.findall('listen\/(.*)\.jpg', data['pic'])[0]
            listens.append(data)

            review_url = re.findall('href="(.*review.*?)" target', str(item_content))[0]
            review_dict[data['source']] = review_url
        listens.sort(key=lambda k:k['source'])
        # print(listens)
        for r in listens:
            with db_session:
                ListenBasic(**r)
        time.sleep(1)
        print(page_id)
    print(review_dict)


if __name__ == '__main__':
    listen_basic_get()