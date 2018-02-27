#-*- coding: utf-8 -*-
import logging

default_level = logging.DEBUG

FORMAT = '%(levelname)s %(asctime)s %(filename)s %(funcName)s : %(message)s'
logging.basicConfig(format=FORMAT, level=default_level)

eng_log = logging.getLogger('english_server')