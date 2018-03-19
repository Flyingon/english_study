# -*- coding: utf-8 -*-
from sanic.response import json, html
from sanic import Blueprint
from words import synonym
from words import reading
from words import listen
from words.get_xiaozhan_data import get_xiaozhan_word
from util.authen import PermissionCheck

bp = Blueprint('words_blueprint')

ret = {
    "err_code": 0,
    "err_msg": "",
}

synonym_prefix = "words/synonym/"
reading_prefix = "words/reading/"
listen_prefix = "words/listen/"

bp.static(synonym_prefix + 'index', './template/words/synonym_words.html')


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


bp.static(reading_prefix + 'index', './template/words/reading_words_index.html')
bp.static(reading_prefix + 'detail', './template/words/reading_words_detail.html')


@bp.route(reading_prefix + 'titles', methods=['GET'])
async def reading_tiles(request):
    data = await reading.get_toefl_titles()
    return json(data)

@bp.route(reading_prefix + 'words', methods=['GET'])
async def reading_titles(request):
    params = request.raw_args
    reading_id = params['id']
    data = await reading.get_toefl_words(reading_id)
    return json(data)

@bp.route(reading_prefix + 'del', methods=['POST'])
@PermissionCheck('cookies')
async def reading_word_del(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await reading.del_word(params)
    return json(ret)

@bp.route(reading_prefix + 'add', methods=['POST'])
@PermissionCheck('cookies')
async def reading_word_add(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await reading.add_word(params)
    return json(ret)

@bp.route(reading_prefix + 'update', methods=['POST'])
@PermissionCheck('cookies')
async def reading_word_add(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await reading.update_word(params)
    return json(ret)


bp.static(listen_prefix + 'index', './template/words/listen_words_index.html')
bp.static(listen_prefix + 'detail', './template/words/listen_words_detail.html')

@bp.route(listen_prefix + 'titles', methods=['GET'])
async def listen_tiles(request):
    data = await listen.get_toefl_titles()
    return json(data)

@bp.route(listen_prefix + 'words', methods=['GET'])
async def listen_tiles(request):
    params = request.raw_args
    reading_id = params['id']
    data = await listen.get_toefl_words(reading_id)
    return json(data)

@bp.route(listen_prefix + 'del', methods=['POST'])
@PermissionCheck('cookies')
async def listen_word_del(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await listen.del_word(params)
    return json(ret)

@bp.route(listen_prefix + 'add', methods=['POST'])
@PermissionCheck('cookies')
async def listen_word_add(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await listen.add_word(params)
    return json(ret)

@bp.route(listen_prefix + 'update', methods=['POST'])
@PermissionCheck('cookies')
async def listen_word_add(request):
    params = request.json
    ret["err_code"], ret["err_msg"] = await listen.update_word(params)
    return json(ret)