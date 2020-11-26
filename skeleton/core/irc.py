#!/usr/bin/env python
# IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# irc.py

import socket
import time

import config
import constants
import database
import debug
import functions

# Load optional modules
if config.connection.ssl:
	import ssl
if config.connection.proxy:
	try:
		import sock
	except ImportError:
		debug.error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)') # Required for proxy support.

def color(msg, foreground, background=None):
	if background:
		return f'\x03{foreground},{background}{msg}{constants.reset}'
	else:
		return f'\x03{foreground}{msg}{constants.reset}'

class IRC(object):
	def __init__(self):
		self.last   = 0
		self.slow   = False
		self.sock   = None
		self.status = True

	def connect(self):
		try:
			self.create_socket()
			self.sock.connect((config.connection.server, config.connection.port))
			self.register()
		except socket.error as ex:
			debug.error('Failed to connect to IRC server.', ex)
			Events.disconnect()
		else:
			self.listen()

	def create_socket(self):
		family = socket.AF_INET6 if config.connection.ipv6 else socket.AF_INET
		if config.connection.proxy:
			proxy_server, proxy_port = config.connection.proxy.split(':')
			self.sock = socks.socksocket(family, socket.SOCK_STREAM)
			self.sock.setblocking(0)
			self.sock.settimeout(15)
			self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self.sock = socket.socket(family, socket.SOCK_STREAM)
		if config.connection.vhost:
			self.sock.bind((config.connection.vhost, 0))
		if config.connection.ssl:
			ctx = ssl.SSLContext()
			if config.cert.file:
				ctx.load_cert_chain(config.cert.file, config.cert.key, config.cert.password)
			if config.connection.ssl_verify:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self.sock = ctx.wrap_socket(self.sock)

	def listen(self):
		while True:
			try:
				data = self.sock.recv(2048).decode('utf-8')
				for line in (line for line in data.split('\r\n') if line):
					debug.irc(line)
					if len(line.split()) >= 2:
						Events.handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				debug.error('Unexpected error occured.', ex)
				break
		Events.disconnect()

	def register(self):
		if config.login.network:
			Commands.raw('PASS ' + config.login.network)
		Commands.raw(f'USER {config.ident.username} 0 * :{config.ident.realname}')
		Commands.nick(config.ident.nickname)



class Commands:
	def action(chan, msg):
		Commands.sendmsg(chan, f'\x01ACTION {msg}\x01')

	def ctcp(target, data):
		Commands.sendmsg(target, f'\001{data}\001')

	def error(target, data, reason=None):
		if reason:
			Commands.sendmsg(target, '[{0}] {1} {2}'.format(color('!', constants.red), data, color('({0})'.format(reason), constants.grey)))
		else:
			Commands.sendmsg(target, '[{0}] {1}'.format(color('!', constants.red), data))

	def identify(nick, password):
		Commands.sendmsg('nickserv', f'identify {nick} {password}')

	def invite(nick, chan):
		Commands.raw(f'INVITE {nick} {chan}')

	def join_channel(chan, key=None):
		Commands.raw(f'JOIN {chan} {key}') if key else Commands.raw('JOIN ' + chan)

	def mode(target, mode):
		Commands.raw(f'MODE {target} {mode}')

	def nick(nick):
		Commands.raw('NICK ' + nick)

	def notice(target, msg):
		Commands.raw(f'NOTICE {target} :{msg}')

	def oper(user, password):
		Commands.raw(f'OPER {user} {password}')

	def part(chan, msg=None):
		Commands.raw(f'PART {chan} {msg}') if msg else Commands.raw('PART ' + chan)

	def quit(msg=None):
		Commands.raw('QUIT :' + msg) if msg else Commands.raw('QUIT')

	def raw(msg):
		Bot.sock.send(bytes(msg + '\r\n', 'utf-8'))

	def sendmsg(target, msg):
		Commands.raw(f'PRIVMSG {target} :{msg}')

	def topic(chan, text):
		Commands.raw(f'TOPIC {chan} :{text}')



class Events:
	def connect():
		if config.settings.modes:
			Commands.mode(config.ident.nickname, '+' + config.settings.modes)
		if config.login.nickserv:
			Commands.identify(config.ident.nickname, config.login.nickserv)
		if config.login.operator:
			Commands.oper(config.ident.username, config.login.operator)
		Commands.join_channel(config.connection.channel, config.connection.key)

	def ctcp(nick, chan, msg):
		pass

	def disconnect():
		Bot.sock.close()
		time.sleep(config.throttle.reconnect)
		Bot.connect()

	def invite(nick, chan):
		if nick == config.ident.nickname and chan == config.connection.channe:
			Commands.join_channel(config.connection.channel, config.connection.key)

	def join_channel(nick, chan):
		pass

	def kick(nick, chan, kicked):
		if kicked == config.ident.nickname and chan == config.connection.channel:
			time.sleep(config.throttle.rejoin)
			Commands.join_channel(chan, config.connection.key)

	def message(nick, ident, chan, msg):
		try:
			if chan == config.connection.channel and Bot.status:
				if msg.startswith(config.settings.cmd_char):
					if not database.Ignore.check(ident):
						if time.time() - Bot.last < config.throttle.command and not functions.is_admin(ident):
							if not Bot.slow:
								Commands.sendmsg(chan, color('Slow down nerd!', constants.red))
								Bot.slow = True
						elif Bot.status or functions.is_admin(ident):
							Bot.slow = False
							args     = msg.split()
							if msg == 'test':
								while True:
									Commands.raw('WHO')
									time.sleep(0.5)
							'''
							if len(args) == 1:
								if cmd == 'test':
									Commands.sendmsg(chan, 'It works!')
							elif len(args) >= 2:
								if cmd == 'echo':
									Commands.sendmsg(chan, args)
							'''
						Bot.last = time.time()
		except Exception as ex:
			Commands.error(chan, 'Command threw an exception.', ex)

	def nick_in_use():
		debug.error('The bot is already running or nick is in use.')

	def part(nick, chan):
		pass

	def private(nick, ident, msg):
		if functions.is_admin(ident):
			args = msg.split()
			if msg == '.ignore':
				ignores = database.Ignore.read()
				if ignores:
					Commands.sendmsg(nick, '[{0}]'.format(color('Ignore List', constants.purple)))
					for user in ignores:
						Commands.sendmsg(nick, color(user, constants.yellow))
					Commands.sendmsg(nick, '{0} {1}'.format(color('Total:', constants.light_blue), color(len(ignores), constants.grey)))
				else:
					Commands.error(nick, 'Ignore list is empty!')
			elif msg == '.off':
				Bot.status = False
				Commands.sendmsg(nick, color('OFF', constants.red))
			elif msg == '.on':
				Bot.status = True
				Commands.sendmsg(nick, color('ON', constants.green))
			elif len(args) == 3:
				if args[0] == '.ignore':
					if args[1] == 'add':
						user_ident = args[2]
						if user_ident not in database.Ignore.hosts():
							database.Ignore.add(nickname, user_ident)
							Commands.sendmsg(nick, 'Ident {0} to the ignore list.'.format(color('added', constants.green)))
						else:
							Commands.error(nick, 'Ident is already on the ignore list.')
					elif args[1] == 'del':
						user_ident = args[2]
						if user_ident in database.Ignore.hosts():
							database.Ignore.remove(user_ident)
							Commands.sendmsg(nick, 'Ident {0} from the ignore list.'.format(color('removed', constants.red)))
						else:
							Commands.error(nick, 'Ident does not exist in the ignore list.')

	def quit(nick):
		pass

	def handle(data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif args[0] == 'PING':
			Commands.raw('PONG ' + args[1][1:])
		elif args[1] == constants.RPL_WELCOME:
			Events.connect()
		elif args[1] == constants.ERR_NICKNAMEINUSE:
			Events.nick_in_use()
		elif args[1] == constants.INVITE and len(args) == 4:
			nick = args[0].split('!')[0][1:]
			chan = args[3][1:]
			Events.invite(nick, chan)
		elif args[1] == constants.JOIN and len(args) == 3:
			nick = args[0].split('!')[0][1:]
			chan = args[2][1:]
			Commands.raw('WHOIS SNIFF')
			Events.join_channel(nick, chan)
		elif args[1] == constants.KICK and len(args) >= 4:
			nick   = args[0].split('!')[0][1:]
			chan   = args[2]
			kicked = args[3]
			Events.kick(nick, chan, kicked)
		elif args[1] == constants.PART and len(args) >= 3:
			nick = args[0].split('!')[0][1:]
			chan = args[2]
			Events.part(nick, chan)
		elif args[1] == constants.PRIVMSG and len(args) >= 4:
			nick  = args[0].split('!')[0][1:]
			ident = args[0].split('!')[1]
			chan  = args[2]
			msg   = data.split(f'{args[0]} PRIVMSG {chan} :')[1]
			if msg.startswith('\001'):
				Events.ctcp(nick, chan, msg)
			elif chan == config.ident.nickname:
				Events.private(nick, ident, msg)
			else:
				Events.message(nick, ident, chan, msg)
		elif args[1] == constants.QUIT:
			nick = args[0].split('!')[0][1:]
			Events.quit(nick)

Bot = IRC()
