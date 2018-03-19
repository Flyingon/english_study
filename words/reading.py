#-*- coding: utf-8 -*-

from datetime import datetime
from model.pg_client import sql_excute

async def get_toefl_titles():
    """
    查询托福阅读题目
    """
    ret = list()
    query_sql = "SELECT id, title_en, title_cn, source, pic FROM readingbasic ORDER BY id"
    query_ret = await sql_excute(sql=query_sql)
    for data in query_ret:
        ret.append({
            'id': data[0],
            'title_en': data[1],
            'title_cn': data[2],
            'source': data[3],
            'pic': data[4],
        })
    return ret

async def get_toefl_words(reading_id):
    """
    查询每篇文章的单词
    """
    ret = list()
    query_sql = "SELECT id, word_en, word_cn FROM readingword WHERE reading_id = {} ORDER BY create_time desc".format(reading_id)
    query_ret = await sql_excute(sql=query_sql)
    for data in query_ret:
        ret.append({
            'id': data[0],
            'word_en': data[1],
            'word_cn': data[2],
        })
    return ret

async def del_word(param):
    """
    删除单词
    """
    query_sql = "DELETE FROM readingword WHERE id ='{}'".format(param["word_id"])
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        return -1, rsp
    else:
        return 0, ""

async def add_word(param):
    """
    添加单词
    """
    create_time = format(datetime.now(), "%Y-%m-%d %H:%M:%S")
    query_sql = "INSERT INTO readingword (reading_id, word_en, word_cn, create_time) VALUES ('{0}', '{1}', '{2}', '{3}');".format(
        param["reading_id"], param["word"], param["meaning"], create_time)
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        if "duplicate key value violates unique constraint" in rsp:
            return -2, "单词已经存在 %s" %(rsp.split('\n')[1])
        return -1, rsp
    else:
        return 0, ""
    
async def update_word(param):
    """
    添加单词
    """
    query_sql = "UPDATE readingword set word_en='{0}',word_cn='{1}' WHERE id='{2}';".format(
            param["word"], param["meaning"], param["word_id"])
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        return -1, rsp
    else:
        return 0, ""