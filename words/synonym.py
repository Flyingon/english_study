#-*- coding: utf-8 -*-

from datetime import datetime
from model.pg_client import sql_excute

async def query_format_words(word_type):
    """
    格式化单词查询结果，包含表头和内容
    :param word_type: 单词词性
    :return: ret = {"th_list": [],"data": []}
    """
    ret = {
        "th_list": ["单词释义"],
        "data": []
    }
    longest_words_count = 0
    if not word_type:
        resp = await get_all_words()
    else:
        resp = await get_words_by_type(word_type)
    for k,v in resp.items():
        length = len(v)
        ret["data"].append([k] + v)
        if longest_words_count < length:
            longest_words_count = length
    ret["data"].sort(key=lambda k:k[-1], reverse=True)
    ret["data"] = [d[:-1] for d in ret["data"]]
    for i in range(1, longest_words_count + 1):
        ret["th_list"].append("单词%s" %i)
    return ret

async def get_all_words():
    """
    查询所有单词
    """
    ret = {}
    ctime_dict = {}
    query_sql = "SELECT meaning, word, type, create_time FROM synonymwords"
    query_ret = await sql_excute(sql=query_sql)
    for data in query_ret:
        if data[0] in ret:
            ret[data[0]].append("%s(%s)" %(data[1], data[2]))
            ctime_dict[data[0]].append(data[3])
        else:
            ret[data[0]] = ["%s(%s)" %(data[1], data[2])]
            ctime_dict[data[0]] = [data[3]]
    for k,v in ret.items():
        ret[k].append(max(ctime_dict[k]))
    return ret

async def get_words_by_type(word_type):
    """
    根据词性查询单词
    """
    ret = {}
    ctime_dict = {}
    query_sql = "SELECT meaning, word, type, create_time FROM synonymwords where type='{}'".format(word_type)
    query_ret = await sql_excute(sql=query_sql)
    for data in query_ret:
        if data[0] in ret:
            ret[data[0]].append(data[1])
            ctime_dict[data[0]].append(data[3])
        else:
            ret[data[0]] = [data[1]]
            ctime_dict[data[0]] = [data[3]]
    for k,v in ret.items():
        ret[k].append(max(ctime_dict[k]))
    return ret

async def add_words(param):
    """
    添加单词
    """
    create_time = format(datetime.now(), "%Y-%m-%d %H:%M:%S")
    query_sql = ""
    for word in param["word_list"]:
        query_sql += "INSERT INTO synonymwords (meaning, word, type, create_time) VALUES ('{0}', '{1}', '{2}', '{3}');".format(
            param["meaning"], word, param["word_type"], create_time)
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        if "duplicate key value violates unique constraint" in rsp:
            return -2, "单词已经存在 %s" %(rsp.split('\n')[1])
        return -1, rsp
    else:
        return 0, ""

async def del_words(param):
    """
    删除单词
    """
    if param.get("word_list"):
        query_sql = ""
        for word in param["word_list"]:
            query_sql += "DELETE FROM synonymwords WHERE meaning = '{0}' AND word = '{1}' AND type = '{2}';".format(
                param["meaning"], word, param["word_type"])
    else:
        query_sql = "DELETE FROM synonymwords WHERE where meaning='{}'".format(param["meaning"])
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        return -1, rsp
    else:
        return 0, ""

async def update_words(param):
    """
    修改单词，保持同一词性下面[单词释义]唯一
    """
    query_sql = "SELECT meaning, word, type FROM synonymwords WHERE meaning = '{0}' AND type='{1}'".format(param["meaning"], param["word_type"])
    query_ret = await sql_excute(sql=query_sql)
    old_words = set()
    for data in query_ret:
        old_words.add(data[1])
    create_time = format(datetime.now(), "%Y-%m-%d %H:%M:%S")
    query_sql = ""
    for word in param["word_list"]:
        if word not in old_words:
            query_sql += "INSERT INTO synonymwords (meaning, word, type, create_time) VALUES ('{0}', '{1}', '{2}', '{3}');".format(
                param["meaning"], word, param["word_type"], create_time)
        else:
            old_words.remove(word)
    for word in old_words:
        query_sql += "DELETE FROM synonymwords WHERE meaning = '{0}' AND word = '{1}' AND type = '{2}';".format(
            param["meaning"], word, param["word_type"])
    if query_sql:
        rsp = await sql_excute(sql=query_sql)
        if rsp != 0:
            return -1, rsp
        else:
            return 0, ""
    else:
        return -2, "无需修改"