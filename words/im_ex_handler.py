#-*- coding: utf-8 -*-
import pandas as pd
import psycopg2
from pony.orm import db_session, sql_debug, select
from model.data_model_bak import db, SynonymWords

config_file = "../conf/server.cfg"
import configparser

config = configparser.ConfigParser()
config.read(config_file)

postgre_host = config.get('postgre', 'host')
postgre_port = int(config.get('postgre', 'port'))
postgre_db = config.get('postgre', 'dbname')
postgre_user = config.get('postgre', 'user')
postgre_password = config.get('postgre', 'password')

# sql_debug(True)
# postgre = psycopg2.connect(host=postgre_host, port=postgre_port, dbname=postgre_db, user=postgre_user, password=postgre_password)
db.bind(provider="postgres", user=postgre_user, password=postgre_password, host=postgre_host, port=postgre_port,
        database=postgre_db)
db.generate_mapping(create_tables=True)

if __name__ == '__main__':
    with db_session:
        sws = select(s for s in SynonymWords)[:]
        for sw in sws:
            print(sw.meaning, sw.word, sw.type)
