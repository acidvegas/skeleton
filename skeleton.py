#!/usr/bin/env python
# Asyncronoua IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# skeleton.py

import asyncio
import logging
import logging.handlers
import os
import random
import time

##################################################

class config:
	class connection:
		server     = 'irc.supernets.org'
		port       = 6697
		ipv6       = False
		ssl        = True
		ssl_verify = False
		vhost      = None
		channel    = '#dev'
		key        = None
		modes      = None

	class cert:
		file     = None
		password = None

	class ident:
		nickname = 'skeleton'
		username = 'skeleton'
		realname = 'acid.vegas/skeleton'

	class login:
		network  = None
		nickserv = None
		operator = None

	class settings:
		admin = 'nick!user@host' # Must be in nick!user@host format (Wildcards accepted)
		log   = False

	class throttle:
		command   = 3
		message   = 0.5
		reconnect = 15
		rejoin    = 5
		timeout   = 15

##################################################

def ssl_ctx():
	import ssl
	ctx = ssl.create_default_context()
	if not config.connection.ssl_verify:
		ctx.check_hostname = False
		ctx.verify_mode = ssl.CERT_NONE
	if config.cert.file:
	    ctx.load_cert_chain(config.cert.file, password=config.cert.password)
	return ctx

##################################################

class Command:
	def join_channel(chan, key=None):
		Command.raw(f'JOIN {chan} {key}') if key else Command.raw('JOIN ' + chan)

	def mode(target, mode):
		Command.raw(f'MODE {target} {mode}')

	def nick(new_nick):
		Command.raw('NICK ' + new_nick)

	def raw(data):
		Bot.writer.write(data[:510].encode('utf-8') + b'\r\n')

	def sendmsg(target, msg):
		Command.raw(f'PRIVMSG {target} :{msg}')

##################################################

class Event:
	def connect():
		if config.connection.modes:
			Command.raw(f'MODE {config.ident.nickname} +{config.connection.modes}')
		if config.login.nickserv:
			Command.sendmsg('NickServ', f'IDENTIFY {config.ident.nickname} {config.login.nickserv}')
		if config.login.operator:
			Command.raw(f'OPER {config.ident.username} {config.login.operator}')
		Command.join_channel(config.connection.channel, config.connection.key)

	async def disconnect():
		Bot.writer.close()
		await bot.writer.wait_closed()
		asyncio.sleep(config.throttle.reconnect)

	def nick_in_use():
		new_nick = 'a' + str(random.randint(1000,9999))
		Command.nick(new_nick)

	async def handler():
		while not Bot.reader.at_eof():
			try:
				data = await Bot.reader.readline()
				data = data.decode('utf-8').strip()
				logging.info(data)
				args = data.split()
				if data.startswith('ERROR :Closing Link:'):
					raise Exception('Connection has closed.')
				elif data.startswith('ERROR :Reconnecting too fast, throttled.'):
					raise Exception('Connection has closed. (throttled)')
				elif args[0] == 'PING':
					Command.raw('PONG ' + args[1][1:])
				elif args[1] == '001': #RPL_WELCOME
					Event.connect()
				elif args[1] == '433': #ERR_NICKNAMEINUSE
					Event.nick_in_use()
				elif args[1] == 'KICK':
					pass # handle kick
			except (UnicodeDecodeError, UnicodeEncodeError):
				pass
			except:
				logging.exception('Unknown error has occured!')

##################################################

class IrcBot:
	def __init__(self):
		self.options = {
			'host'       : config.connection.server,
			'port'       : config.connection.port,
			'limit'      : 1024,
			'ssl'        : ssl_ctx() if config.connection.ssl else None,
			'family'     : socket.AF_INET6 if config.connection.ipv6 else socket.AF_INET,
			'local_addr' : (config.connection.vhost, 0) if config.connection.vhost else None
		}
		self.reader, self.writer = (None, None)

	async def connect(self):
		try:
			self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**self.options), timeout=config.throttle.timeout)
			if config.login.network:
				Command.raw('PASS ' + config.login.network)
			Command.raw(f'USER {config.ident.username} 0 * :{config.ident.realname}')
			Command.raw('NICK ' + config.ident.nickname)
		except:
			logging.exception('Failed to connect to IRC server!')
		else:
			await Event.handler()

##################################################

if __name__ == '__main__':
	if not os.path.exists('logs'):
		os.makedirs('logs')
	sh = logging.StreamHandler()
	sh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(message)s', '%I:%M %p'))
	if config.settings.log:
		fh = logging.handlers.RotatingFileHandler('logs/debug.log', maxBytes=250000, backupCount=7, encoding='utf-8')
		fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(filename)s.%(funcName)s.%(lineno)d | %(message)s', '%Y-%m-%d %I:%M %p'))
		logging.basicConfig(level=logging.NOTSET, handlers=(sh,fh))
		del fh,sh
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

	Bot = IrcBot()
	asyncio.run(Bot.connect())