# -*- coding: utf-8 -*-
"""
sanic_session:
https://pythonhosted.org/sanic_session/using_the_interfaces.html
当前session自己实现，暂时没有用到这个模块，需要用的话用middleware包装：
from model import session_client

@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session_client.session_interface.open(request)

@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session_client.session_interface.save(request, response)

"""
import asyncio_redis
from sanic_session import RedisSessionInterface

redis = None
session_interface = None

class Redis:
    """
    A simple wrapper class that allows you to share a connection
    pool across your application.
    """
    _pool = None

    def __init__(self, host, port, password, db_name):
        self.host = host
        self.port = port
        self.password = password if not password else None
        self.db_name = db_name

    async def get_redis_pool(self):
        if not self._pool:
            self._pool = await asyncio_redis.Pool.create(
                host=self.host, port=self.port, password=self.password,
                db=self.db_name, poolsize=10
            )

        return self._pool

def init_session_interface(host, port, password, db_name):
    global redis, session_interface
    redis = Redis(host, port, password, db_name)
    session_interface = RedisSessionInterface(redis.get_redis_pool)
