#!/usr/bin/env python
# Asyncronous IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# bot.py

import asyncio
import logging

import config

from commands import Command
from events import Event

def ssl_ctx():
	import ssl
	ctx = ssl.create_default_context()
	if not config.connection.ssl_verify:
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
	if config.cert.file:
	    ctx.load_cert_chain(config.cert.file, password=config.cert.password)
	return ctx

class IrcBot:
	def __init__(self):
		self.options = {
			'host'       : config.connection.server,
			'port'       : config.connection.port,
			'limit'      : 1024,
			'ssl'        : ssl_ctx() if config.connection.ssl else None,
			'family'     : 10 if config.connection.ipv6 else 2,
			'local_addr' : (config.connection.vhost, 0) if config.connection.vhost else None
		}
		self.reader = None
		self.writer = None

	async def run(self):
		try:
			self.reader, self.writer = await asyncio.open_connection(**self.options, timeout=config.throttle.timeout)
		except Exception as ex:
			logging.exception('Failed to connect to IRC server!')
		else:
			try:
				await Command(Bot).register(config.ident.nickname, config.ident.username, config.ident.realname, config.login.network)
				while not self.reader.at_eof():
					data = await self.reader.readline()
					Event(Bot).handle(data.decode('utf-8').strip())
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
			except Exception as ex:
				logging.exception('Unknown error has occured!')
		finally:
			Event.disconnect()

Bot = IrcBot()