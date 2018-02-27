#-*- coding: utf-8 -*-
from sanic.response import json, html
from sanic import Blueprint
from words import synonym
from words.get_xiaozhan_data import get_xiaozhan_word
from util.authen import PermissionCheck

bp = Blueprint('words_blueprint')

ret = {
    "err_code": 0,
    "err_msg": "",
}

synonym_prefix = "words/synonym/"

@bp.route(synonym_prefix + 'all', methods=['GET'])
async def words_all(request):
    data = await synonym.query_format_words(word_type=None)
    return json(data)

@bp.route(synonym_prefix + 'adj', methods=['GET'])
async def words_adj(request):
    data = await synonym.query_format_words("adj")
    return json(data)

@bp.route(synonym_prefix + 'noun', methods=['GET'])
async def words_noun(request):
    data = await synonym.query_format_words("noun")
    return json(data)

@bp.route(synonym_prefix + 'verb', methods=['GET'])
async def words_verb(request):
    data = await synonym.query_format_words("verb")
    return json(data)

@bp.route(synonym_prefix + 'adv', methods=['GET'])
async def words_adv(request):
    data = await synonym.query_format_words("adverb")
    return json(data)

@bp.route(synonym_prefix + 'add', methods=['POST'])
@PermissionCheck('cookies')
async def words_add(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await synonym.add_words(params)
    return json(ret)

@bp.route(synonym_prefix + 'del', methods=['POST'])
@PermissionCheck('cookies')
async def words_del(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await synonym.del_words(params)
    return json(ret)

@bp.route(synonym_prefix + 'mod', methods=['POST'])
@PermissionCheck('cookies')
async def words_update(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await synonym.update_words(params)
    return json(ret)

@bp.route('words/detail', methods=['GET'])
async def word_xiaozhan(request):
    params = request.raw_args
    word = params["word"]
    return html(get_xiaozhan_word(word))

bp.static(synonym_prefix + 'index', './template/words/synonym_words.html')