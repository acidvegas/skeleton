#!/usr/bin/env python
# Asyncronous IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# skeleton.py

import asyncio
import logging
import logging.handlers
import os
import sys

sys.dont_write_bytecode = True
os.chdir(os.path.dirname(__file__) or '.')
sys.path += ('core','modules')

import config

if not os.path.exists('logs'):
	os.makedirs('logs')
sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(message)s', '%I:%M %p'))
if config.settings.log:
	fh = logging.handlers.RotatingFileHandler('logs/debug.log', maxBytes=250000, backupCount=7, encoding='utf-8')
	fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(filename)s.%(funcName)s.%(lineno)d | %(message)s', '%Y-%m-%d %I:%M %p'))
	logging.basicConfig(level=logging.NOTSET, handlers=(sh,fh))
	del fh
else:
	logging.basicConfig(level=logging.NOTSET, handlers=(sh,))
del sh

print('#'*56)
print('#{:^54}#'.format(''))
print('#{:^54}#'.format('Asyncronous IRC Bot Skeleton'))
print('#{:^54}#'.format('Developed by acidvegas in Python'))
print('#{:^54}#'.format('https://acid.vegas/skeleton'))
print('#{:^54}#'.format(''))
print('#'*56)

from bot import Bot

asyncio.run(Bot.run())