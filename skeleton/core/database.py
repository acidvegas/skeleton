#!/usr/bin/env python
# IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# database.py

import os
import re
import sqlite3

# Globals
db  = sqlite3.connect(os.path.join('data', 'bot.db'), check_same_thread=False)
sql = db.cursor()

def check():
	tables = sql.execute('SELECT name FROM sqlite_master WHERE type=\'table\'').fetchall()
	if not len(tables):
		sql.execute('CREATE TABLE IGNORE (IDENT TEXT NOT NULL);')
		db.commit()

class Ignore:
	def add(ident):
		sql.execute('INSERT INTO IGNORE (IDENT) VALUES (?)', (ident,))
		db.commit()

	def check(ident):
		for ignored_ident in Ignore.read():
			if re.compile(ignored_ident.replace('*','.*')).search(ident):
				return True
		return False

	def read():
		return list(item[0] for item in sql.execute('SELECT IDENT FROM IGNORE ORDER BY IDENT ASC').fetchall())

	def remove(ident):
		sql.execute('DELETE FROM IGNORE WHERE IDENT=?', (ident,))
		db.commit()
