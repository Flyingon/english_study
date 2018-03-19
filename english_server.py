#-*- coding: utf-8 -*-
import asyncio
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic import response

from views import words_blueprint
from views import account_blueprint
from conf import init_db, parse_config, init_session


app = Sanic(__name__)

config = parse_config("prod")

@app.listener('before_server_start')
async def init_env(app, loop):
    await init_db(config)
    init_session(config)

@app.listener('after_server_start')
async def notify_server_started(app, loop):
    print('English Server successfully started!')

@app.exception(NotFound)
def ignore_404s(request, exception):
    return response.redirect('/static/404/html/index.html')

def main():
    app.static('', './template/index.html')
    app.static('static', './static')
    app.static('template', './template')
    app.static('favicon.ico', './static/assets/img/favicon.ico')
    app.blueprint(words_blueprint.bp)
    app.blueprint(account_blueprint.bp)

    app.run(host='0.0.0.0', port=config["server_port"], debug=False, workers=config["process_num"])

if __name__ == "__main__":
    main()