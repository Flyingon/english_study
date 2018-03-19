# -*- coding: utf-8 -*-

# __all__ = []

"""
用pony orm 定义和初始化建表
"""

import sys

sys.path.append('../.')

import os
import configparser
from pony.orm import *
from datetime import datetime

db = Database()


# class Users(db.Entity):
#     account = PrimaryKey(str, 64),
#     username = Optional(str, 64, nullable=True),
#     password = Required(str, 64),
#     email = Optional(str, 64, nullable=True),
#     active = Optional(int),
#     create_time = Optional(datetime)


class SynonymWords(db.Entity):
    meaning = Required(str)
    word = Required(str)
    type = Required(str)
    PrimaryKey(meaning, word, type)


class ReadingBasic(db.Entity):
    id = PrimaryKey(int, auto=True)
    title_en = Required(str)  # 文章英文名
    title_cn = Required(str)  # 文章中文名
    source = Optional(str)  # 文章来源，例如：top1-1
    pic = Optional(str)  # 背景图片

    doc = Set('ReadingDoc')
    word = Set('ReadingWord')
    question = Set('ReadingQuestion')
    word_xiaozhan = Set('ReadingWord_Xiaozhan')


class ReadingDoc(db.Entity):
    reading_id = Required(ReadingBasic)
    section = Required(int)  # 文章段落
    content_en = Required(str, 5000)  # 文章内容
    content_cn = Required(str, 5000)  # 中文翻译
    content_html = Required(str, 5000)   #小站html

class ReadingWord(db.Entity):
    reading_id = Required(ReadingBasic)
    word_en = Required(str)
    word_cn = Required(str)
    create_time = Optional(datetime)

class ReadingWord_Xiaozhan(db.Entity):
    reading_id = Required(ReadingBasic)
    word_en = Required(str)
    word_cn = Required(str)
    detail = Optional(str)


class ReadingQuestion(db.Entity):
    """
    题目表，暂时不启用，没必要爬取
    """
    id = PrimaryKey(int, auto=True)
    reading_id = Required(ReadingBasic)
    index = Required(int)
    content = Required(str)
    answer = Required(str)
    options = Required(str, 5000)
    resolve = Required(str, 5000)


class ListenBasic(db.Entity):
    id = PrimaryKey(int, auto=True)
    title_en = Required(str)  # 文章英文名
    title_cn = Required(str)  # 文章中文名
    source = Optional(str)  # 文章来源，例如：top1-1
    pic = Optional(str)  # 背景图片
    classify = Optional(str)  # 分类

    word = Set('ListenWord')

class ListenWord(db.Entity):
    listen_id = Required(ListenBasic)
    word_en = Required(str)
    word_cn = Required(str)
    create_time = Optional(datetime)

current_path = os.path.dirname(os.path.realpath(__file__))
conf_file = os.path.join(current_path, '../conf/server.cfg')
config = configparser.ConfigParser()
config.read(conf_file)

postgre_host = config.get('postgre', 'host')
postgre_port = int(config.get('postgre', 'port'))
postgre_db = config.get('postgre', 'dbname')
postgre_user = config.get('postgre', 'user')
postgre_password = config.get('postgre', 'password')


def bind_db(provider, host, port, user, password, db_name):
    if provider in ("mysql", "postgres"):
        db.bind(provider=provider, host=host, port=port, user=user, password=password, database=db_name)
    elif provider == 'oracle':
        db.bind(provider, '{user}/{passwd}@{host}:{port}/{db}'.format(
            user=user,
            passwd=password,
            host=host,
            port=port,
            db=db_name
        ))
    db.generate_mapping(create_tables=True)


bind_db('postgres', postgre_host, postgre_port, postgre_user, postgre_password, postgre_db)
