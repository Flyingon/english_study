#-*- coding: utf-8 -*-
import re
from functools import wraps
from sanic.response import json
from model.redis_client import redis_excute
from model.pg_client import sql_excute
from util.log import eng_log

authen_token_key = "AUTHEN_TOKEN_KEY:%s"

class PermissionCheck(object):
    """
    api请求权限验证
    """
    def __init__(self, check_type):
        self.check_type = check_type

    def __call__(self, func):
        @wraps(func)
        async def auth_func(*args, **kwargs):
            request_obj = args[0]
            try:
                session_id = self._get_session(request_obj)
                eng_log.debug("Session_id: %s", session_id)
            except Exception as e:
                return await self.handle_response(err_msg='获取session失败, error: {}'.format(str(e)))
            if not session_id:
                return await self.handle_response(err_msg='需要登录')
            ret = await self._get_token_key(session_id)
            if not ret:
                return await self.handle_response(err_msg='已过期，重新登录')
            account = await self._get_user(account=ret)
            if not account:
                return await self.handle_response(err_msg='账号不存在')
            permissions = await self._get_permission_set(account)
            if not any(filter(lambda item: re.match(item, request_obj.path), permissions)):
                return await self.handle_response(err_msg='没有权限')
            return await func(*args, **kwargs)
        return auth_func

    def _get_session(self, request_obj):
        if self.check_type == 'cookies':
            return request_obj.cookies.get('session_id')
        else:
            return None

    async def handle_response(self, err_msg, err_code=-1):
        return json({
            "err_code": err_code,
            "err_msg": err_msg,
        })

    @classmethod
    async def _get_token_key(cls, token_key):
        """
        从redis读取session_id
        """
        redis_key = authen_token_key % token_key
        return await redis_excute("get", redis_key)

    @classmethod
    async def _get_user(cls, account):
        rsp = await sql_excute(sql=
              "SELECT account FROM users WHERE account = '{}';".format(account))
        if not rsp:
            return None
        else:
            return rsp[0][0]

    @classmethod
    async def _get_permission_set(cls, account):
        return [".*"]