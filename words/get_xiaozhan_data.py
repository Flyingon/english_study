#-*- coding: utf-8 -*-
import requests

def get_xiaozhan_word(word):
    word_url = "http://top.zhan.com/cihui/toefl-{}.html"
    r = requests.get(word_url.format(word))
    return r.text


if __name__ == '__main__':
    print(get_xiaozhan_word("utilitarian"))