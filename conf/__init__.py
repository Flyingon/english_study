#-*- coding: utf-8 -*-

import configparser
from util.log import eng_log
from model.pg_client import init_pg_db
from model.redis_client import init_redis
from model.session_client import init_session_interface

def get_config_file(level):
    config_file = "prod"
    if level == "prod":
        config_file = "./conf/server.cfg"
    return config_file

def parse_config(level):
    ret = dict()
    config_file = get_config_file(level)
    eng_log.info("config file: %s", config_file)
    config = configparser.ConfigParser()
    config.read(config_file)

    ret["postgre_host"] = config.get('postgre', 'host')
    ret["postgre_port"] = int(config.get('postgre', 'port'))
    ret["postgre_db"] = config.get('postgre', 'dbname')
    ret["postgre_user"] = config.get('postgre', 'user')
    ret["postgre_password"] = config.get('postgre', 'password')

    ret["redis_host"] = config.get('redis_conf', 'redis_host')
    ret["redis_port"] = int(config.get('redis_conf', 'redis_port'))
    ret["redis_password"] = config.get('redis_conf', 'redis_password')
    ret["redis_db_name"] = int(config.get('redis_conf', 'redis_db'))

    ret["process_num"] = int(config.get('server_conf', 'process_num'))
    ret["server_port"] = int(config.get('server_conf', 'server_port'))

    return ret

async def init_db(config):
    await init_pg_db(user=config["postgre_user"],
               password=config["postgre_password"],
               host=config["postgre_host"],
               port=config["postgre_port"],
               db_name=config["postgre_db"])

    await init_redis(host=config["redis_host"],
               port=config["redis_port"],
               password=config["redis_password"],
               db_name=config["redis_db_name"])

    print("DataBase config init finish")

def init_session(config):
    """
    初始化sanic_session, 暂时没有用
    :param config:
    :return:
    """
    init_session_interface(
        host=config["redis_host"],
        port=config["redis_port"],
        password=config["redis_password"],
        db_name=config["redis_db_name"]
    )
    print("Session_interface init finish")