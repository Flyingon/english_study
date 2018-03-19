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

def reading_basic_get():

    l1 = [4,8,12,16,20,24,28,32,36,40,44,48,53]
    review_dict = {}
    for page_id in l1:
        url = 'https://top.zhan.com/toefl/read/alltpo%s.html' %page_id
        rsp = requests.get(url)
        soup = BeautifulSoup(rsp.text, 'lxml')
        item_content_list = soup.find_all(class_='item_content')
        readings = []
        for item_content in item_content_list:
            # print(item_content)
            data = {}
            data['pic'] = item_content.find(class_='cover_img').attrs.get("src")
            data['title_cn'] = item_content.find(class_='item_text_cn').contents[0]
            data['title_en'] = item_content.find(class_='item_text_en').contents[0]
            data['source'] = re.findall('reading\/(.*)\.jpg', data['pic'])[0]
            readings.append(data)

            review_url = re.findall('href="(.*practicereview.*?)" target', str(item_content))[0]
            review_dict[data['source']] = review_url
        readings.sort(key=lambda k:k['source'])
        for r in readings:
            with db_session:
                ReadingBasic(**r)
        time.sleep(1)
    print(review_dict)

@db_session
def reading_doc_get():
    from data_gather.xiaozhan import xiaozhan_reading_review
    url_prefix = 'https://top.zhan.com'
    cihui_dict = {}
    for s,v in xiaozhan_reading_review.items():
        url = url_prefix + v
        rsp = requests.get(url)
        # print(rsp.text)
        soup = BeautifulSoup(rsp.text, 'lxml')
        words_url = soup.find(class_='study').attrs.get("href")
        article = soup.find(class_='article')
        doc_content = html2text.html2text(article.prettify())
        # print(doc_content)
        # print(repr(doc_content))
        doc_contents = doc_content.split('  \n  \n')

        basic = ReadingBasic.get(source=s)
        for i, d in enumerate(doc_contents[:-1]):
            section = i + 1
            if ') ' in d:
                d = d.split(') ')[1]
            print(section, d)
            rd = ReadingDoc.get(reading_id=basic, section=section)
            rd.content_en = d
        commit()

    #     entire_doc = []
    #     br_flag = 0
    #     data = {
    #         'section': 1,
    #         'content_html': '',
    #         'content_en': '',
    #         'content_cn': '',
    #             }
    #     for i in article.children:
    #         if not isinstance(i, Tag):
    #             continue
    #         elif i.name == "br":
    #             br_flag += 1
    #             if br_flag == 2:
    #                 if all((data['content_html'], data['content_en'], data['content_cn'])):
    #                     entire_doc.append(copy.deepcopy(data))
    #                 data['section'] += 1
    #                 data['content_html'] = ''
    #                 data['content_en'] = ''
    #                 data['content_cn'] = ''
    #                 br_flag = 0
    #         elif not i.attrs.get('data-translation'):
    #                 continue
    #         else:
    #             data['content_html'] += str(i)
    #
    #             data['content_cn'] += i.attrs.get('data-translation')
    #             for c in i.contents[0].contents:
    #                 if isinstance(c, NavigableString):
    #                     temp = c
    #             if '\n' in temp:
    #                 temp = str(temp).replace('\r\n', '')
    #                 temp = str(temp).replace('\n', '')
    #             data['content_en'] += temp
    #     for d in entire_doc:
    #         d['reading_id'] = basic
    #         ReadingDoc(**d)
    #     cihui_dict[s] = words_url
    #     commit()
    #     print(s)
    # print(cihui_dict)

@db_session
def reading_cihui_get():
    from data_gather.xiaozhan import xiaozhan_reading_cihui
    url = 'https://top.zhan.com/vocab/vocabulary/get-voca-list.html'
    param = {
        'list_type': 0,
        'get_type': 1,
        'test_type': 1,
        'corpus_id': 3,
        'sortRule': 'word, asc',
        'frequency': 0,
        'core': 0,
        'page': 1,
    }

    for s,v in xiaozhan_reading_cihui.items():
        basic = ReadingBasic.get(source=s)
        param['corpus_id'] = int(re.findall('reading-(.*).html', v)[0])
        param_encode = urlencode(param)
        rsp = requests.get(url, params=param_encode)
        data = rsp.json()
        count = int(data['count'])
        total_page = math.ceil(count/15)
        words = []
        for r in data['rows']:
            words.append({
                'word_en': r['word'],
                'word_cn': r['bref'],
                'detail': json.dumps(r, ensure_ascii=False)
            })
        for i in range(2, total_page+1):
            param['page'] = i
            param_encode = urlencode(param)
            rsp = requests.get(url, params=param_encode)
            data = rsp.json()
            for r in data['rows']:
                words.append({
                    'word_en': r['word'].strip(),
                    'word_cn': r['bref'].strip(),
                    'detail': json.dumps(r, ensure_ascii=False)
                })
        for d in words:
            d['reading_id'] = basic
            if not d['word_en']:
                continue
            ReadingWord(**d)
        commit()
        print(s)

@db_session
def reading_question_get():
    from data_gather.xiaozhan import xiaozhan_reading_review
    url_prefix = 'https://top.zhan.com'
    for s, v in xiaozhan_reading_review.items():
        basic = ReadingBasic.get(source=s)
        url1 = url_prefix + v
        questions = []
        for index in range(0,14):
            url = url1.replace('.html', '-0-%s.html' %index)
            print(url)
            rsp = requests.get(url)
            soup = BeautifulSoup(rsp.text, 'lxml')
            question = soup.find(class_='question_desc')
            if not question:
                continue
            question_option = question.find(class_='question_option')
            answer_content = question.find(class_='answer_content')
            resolve_content = question.find(class_='resolve_content')
            # print(question_option)
            # print(answer_content)
            # print(resolve_content)
            question_text = ""
            for i in question_option.find(class_='q_tit').find(class_='text').contents:
                if isinstance(i, Tag):
                    question_text += i.contents[0].strip()
                else:
                    question_text += str(i).strip()
            question_options = []
            if index == 13:
                for i in question_option.find_all(class_='ops dragsec '):
                    question_options.append(i.contents[0].strip())
            elif index == 12:
                question_options.append(question_option.p.contents[0].strip())
            else:
                for i in question_option.find_all(class_='ops sec'):
                    question_options.append(i.label.contents[0].strip())
            answer = answer_content.find(class_='correctAnswer').span.contents[0].strip()
            resolve = resolve_content.find(class_='desc').contents[0].strip()

            questions.append({
                'index': index,
                'content': question_text,
                'options': json.dumps(question_options, ensure_ascii=False),
                'answer': answer,
                'resolve': resolve
            })
        # print(questions)
        for q in questions:
            q['reading_id'] = basic
            ReadingQuestion(**q)
        commit()
        print(s)


if __name__ == '__main__':
    reading_doc_get()