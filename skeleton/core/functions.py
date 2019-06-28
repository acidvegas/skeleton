#!/usr/bin/env python
# IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# functions.py

import re

import config

def is_admin(ident):
	return re.compile(config.settings.admin.replace('*','.*')).search(ident)
