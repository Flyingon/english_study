# -*- coding: utf-8 -*-

import aioredis

pool = None

async def init_redis(host, port, password, db_name):
    """
    base on aioredis
    """
    global pool
    if not password:
        password = None
    pool = await aioredis.create_pool((host, port), password=password, db=db_name)

async def redis_excute(*args):
    with await pool as con:
        ret = await con.execute(*args)
        return ret
