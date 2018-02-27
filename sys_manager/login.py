#-*- coding: utf-8 -*-

import uuid
from datetime import datetime
from model.pg_client import sql_excute
from model.redis_client import redis_excute
from util.hash_maker import get_md5

authen_token_key = "AUTHEN_TOKEN_KEY:%s"

async def login(param):
    """
    登录, 写token
    """
    if not param:
        return -1, "Please input [account] and [password]"
    for p_k in ("account", "password"):
        if not param.get(p_k):
            return -1, "param [{}] is necessary".format(p_k)
    rsp = await sql_excute(sql=
          "SELECT active, password FROM users WHERE account = '{}';".format(param["account"]))
    if not rsp:
        return -4, "User[{}] is not existed".format(param["account"])
    active = rsp[0][0]
    if active != 1:
        return -3, "User[{}] is actived".format(param["account"])
    pwd1 = rsp[0][1]
    pwd2 = get_md5(param["password"])
    if pwd1 != pwd2:
        return -2, "Password[{}] is not right".format(param["password"])
    token_key = await set_token_key(param["account"])
    return 0, token_key

async def logout(token_key):
    """
    登出, 删token
    """
    account = await check_token_key(token_key)
    if not account:
        return -1, "未登录"
    await unset_token_key(token_key)
    return 0, ""

async def get_username(token_key):
    account = await check_token_key(token_key)
    if not account:
        return -1, "Need login"
    rsp = await sql_excute(sql=
          "SELECT username FROM users WHERE account = '{}';".format(account.decode('utf-8')))
    if not rsp:
        return -4, "User[{}] is not existed".format(account)
    user_name = rsp[0][0]
    return 0, user_name

async def set_token_key(user_account):
    """
    设置token, 写入redis
    """
    token_key = str(uuid.uuid1())
    redis_key = authen_token_key % token_key
    await redis_excute("set", redis_key, user_account)
    await redis_excute("expire", redis_key, 60*60)
    return token_key

async def unset_token_key(token_key):
    """
    删除token
    """
    redis_key = authen_token_key % token_key
    await redis_excute("del", redis_key)

async def check_token_key(token_key):
    """
    检查token是否存在
    """
    redis_key = authen_token_key % token_key
    account = await redis_excute("get", redis_key)
    if not account:
        return False
    return account


