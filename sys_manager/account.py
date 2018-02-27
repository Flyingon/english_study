#-*- coding: utf-8 -*-

__all__ = ["add_account"]

from datetime import datetime
from model.pg_client import sql_excute
from util.hash_maker import get_md5


authen_token_key = "AUTHEN_TOKEN_KEY:%"

async def add_account(param):
    """
    添加账号
    """
    for p_k in ("account", "password"):
        if not param.get(p_k):
            return -1, "param [{}] is necessary".format(p_k)
    username = param.get("username", param["account"])
    account = param["account"]
    password = get_md5(param["password"])
    email = param.get("email", "")
    active = param.get("active", 1)
    create_time = param.get("create_time", format(datetime.now(), "%Y-%m-%d %H:%M:%S"))
    rsp = await sql_excute(sql="SELECT account FROM users WHERE account = '{}';".format(account))
    if rsp:
        return -2, "User[{}] is already existed".format(param["account"])
    query_sql = "INSERT INTO users (username, account, password, email, active, create_time) VALUES ('{0}', '{1}', '{2}', '{3}', {4}, '{5}');".format(
        username, account, password, email, active, create_time)
    rsp = await sql_excute(sql=query_sql)
    if rsp != 0:
        return -1, rsp
    return 0, ""

async def del_account(param):
    """
    删除账号
    """
    for p_k in ("account",):
        if not param.get(p_k):
            return -1, "param [{}] is necessary".format(p_k)
    rsp = await sql_excute(sql="DELETE FROM users WHERE account='{}'".format(param["account"]))
    if rsp != 0:
        return -1, rsp
    return 0, ""

