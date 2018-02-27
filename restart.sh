#!/bin/sh
ps -ef | grep english_server.py | grep -v grep | awk -F' ' '{print $2}' | xargs kill -9
sleep 2s
nohup python -u english_server.py -c conf/server.cfg &
echo english_server start OK!