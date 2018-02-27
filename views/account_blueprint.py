#-*- coding: utf-8 -*-

from sanic.response import json
from sanic import Blueprint

from sys_manager import account
from sys_manager import login

from util.authen import PermissionCheck

bp = Blueprint('login')

ret = {
    "err_code": 0,
    "err_msg": "",
}

@bp.route('/user/add', methods=['POST'])
async def user_add(request):
    param = request.json
    ret["err_code"], ret["err_msg"] = await account.add_account(param=param)
    return json(ret)

@bp.route('/user/del', methods=['POST'])
@PermissionCheck("cookies")
async def user_del(request):
    param = request.json
    ret["err_code"], ret["err_msg"] = await account.del_account(param=param)
    return json(ret)

@bp.route('/login', methods=['POST'])
async def user_login(request):
    param = request.json
    err_code, token_key = await login.login(param=param)
    ret["err_code"] = err_code
    ret["err_msg"] = token_key
    resp = json(ret)
    resp.cookies['session_id'] = token_key
    return resp

@bp.route('/logout', methods=['POST'])
async def user_logout(request):
    token_key = request.cookies.get('session_id')
    ret["err_code"], ret["err_msg"] = await login.logout(token_key=token_key)
    return json(ret)

@bp.route('/get_user', methods=['POST'])
async def user_get(request):
    token_key = request.cookies.get('session_id')
    ret["err_code"], ret["user"] = await login.get_username(token_key=token_key)
    return json(ret)

bp.static('account/login', './template/account/login.html')