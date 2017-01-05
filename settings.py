#!/usr/bin/env python
import logging
from config import basedir
log_file = basedir + '/logs/sys_watcher.log'
logging.basicConfig(filename=log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s' ' [in %(pathname)s:%(lineno)d]',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


STORE_SQLITE = 'sqlite'
STORE_REDIS = 'redis'
STORE_MYSQL = 'mysql'
STORE_ES = 'elasticsearch'
