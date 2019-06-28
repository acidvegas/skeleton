#!/usr/bin/env python
# IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)

import socket
import time
import threading

# Configuration
_connection = {'server':'irc.server.com', 'port':6697, 'proxy':None, 'ssl':True, 'ssl_verify':False, 'ipv6':False, 'vhost':None}
_cert       = {'file':None, 'key':None, 'password':None}
_ident      = {'nickname':'DevBot', 'username':'dev', 'realname':'acid.vegas/skeleton'}
_login      = {'nickserv':None, 'network':None, 'operator':None}
_settings   = {'channel':'#dev', 'key':None, 'modes':None, 'throttle':1}

# Formatting Control Characters / Color Codes
bold        = '\x02'
italic      = '\x1D'
underline   = '\x1F'
reverse     = '\x16'
reset       = '\x0f'
white       = '00'
black       = '01'
blue        = '02'
green       = '03'
red         = '04'
brown       = '05'
purple      = '06'
orange      = '07'
yellow      = '08'
light_green = '09'
cyan        = '10'
light_cyan  = '11'
light_blue  = '12'
pink        = '13'
grey        = '14'
light_grey  = '15'

def color(msg, foreground, background=None):
	if background:
		return f'\x03{foreground},{background}{msg}{reset}'
	else:
		return f'\x03{foreground}{msg}{reset}'

def debug(msg):
	print(f'{get_time()} | [~] - {msg}')

def error(msg, reason=None):
	if reason:
		print(f'{get_time()} | [!] - {msg} ({reason})')
	else:
		print(f'{get_time()} | [!] - {msg}')

def error_exit(msg):
	raise SystemExit(f'{get_time()} | [!] - {msg}')

def get_time():
	return time.strftime('%I:%M:%S')

class IRC(object):
	def __init__(self):
		self._queue = list()
		self._sock = None

	def _run(self):
		Loop._loops()
		self._connect()

	def _connect(self):
		try:
			self._create_socket()
			self._sock.connect((_connection['server'], _connection['port']))
			self._register()
		except socket.error as ex:
			error('Failed to connect to IRC server.', ex)
			Event._disconnect()
		else:
			self._listen()

	def _create_socket(self):
		family = socket.AF_INET6 if _connection['ipv6'] else socket.AF_INET
		if _connection['proxy']:
			proxy_server, proxy_port = _connection['proxy'].split(':')
			self._sock = socks.socksocket(family, socket.SOCK_STREAM)
			self._sock.setblocking(0)
			self._sock.settimeout(15)
			self._sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_server, int(proxy_port))
		else:
			self._sock = socket.socket(family, socket.SOCK_STREAM)
		if _connection['vhost']:
			self._sock.bind((_connection['vhost'], 0))
		if _connection['ssl']:
			ctx = ssl.SSLContext()
			if _cert['file']:
				ctx.load_cert_chain(_cert['file'], _cert['key'], _cert['password'])
			if _connection['ssl_verify']:
				ctx.verify_mode = ssl.CERT_REQUIRED
				ctx.load_default_certs()
			else:
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
			self._sock = ctx.wrap_socket(self._sock)

	def _listen(self):
		while True:
			try:
				data = self._sock.recv(1024).decode('utf-8')
				for line in (line for line in data.split('\r\n') if len(line.split()) >= 2):
					debug(line)
					Event._handle(line)
			except (UnicodeDecodeError,UnicodeEncodeError):
				pass
			except Exception as ex:
				error('Unexpected error occured.', ex)
				break
		Event._disconnect()

	def _register(self):
		if _login['network']:
			Bot._queue.append('PASS ' + _login['network'])
		Bot._queue.append('USER {0} 0 * :{1}'.format(_ident['username'], _ident['realname']))
		Bot._queue.append('NICK ' + _ident['nickname'])

class Command:
	def _action(target, msg):
		Bot._queue.append(chan, f'\x01ACTION {msg}\x01')

	def _ctcp(target, data):
		Bot._queue.append(target, f'\001{data}\001')

	def _invite(nick, chan):
		Bot._queue.append(f'INVITE {nick} {chan}')

	def _join(chan, key=None):
		Bot._queue.append(f'JOIN {chan} {key}') if key else Bot._queue.append('JOIN ' + chan)

	def _mode(target, mode):
		Bot._queue.append(f'MODE {target} {mode}')

	def _nick(nick):
		Bot._queue.append('NICK ' + nick)

	def _notice(target, msg):
		Bot._queue.append(f'NOTICE {target} :{msg}')

	def _part(chan, msg=None):
		Bot._queue.append(f'PART {chan} {msg}') if msg else Bot._queue.append('PART ' + chan)

	def _quit(msg=None):
		Bot._queue.append('QUIT :' + msg) if msg else Bot._queue.append('QUIT')

	def _raw(data):
		Bot._sock.send(bytes(data[:510] + '\r\n', 'utf-8'))

	def _sendmsg(target, msg):
		Bot._queue.append(f'PRIVMSG {target} :{msg}')

	def _topic(chan, text):
		Bot._queue.append(f'TOPIC {chan} :{text}')

class Event:
	def _connect():
		if _settings['modes']:
			Command._mode(_ident['nickname'], '+' + _settings['modes'])
		if _login['nickserv']:
			Command._sendmsg('NickServ', 'IDENTIFY {0} {1}'.format(_ident['nickname'], _login['nickserv']))
		if _login['operator']:
			Bot._queue.append('OPER {0} {1}'.format(_ident['username'], _login['operator']))
		Command._join(_setting['channel'], _settings['key'])

	def _ctcp(nick, chan, msg):
		pass

	def _disconnect():
		Bot._sock.close()
		Bot._queue = list()
		time.sleep(15)
		Bot._connect()

	def _invite(nick, chan):
		pass

	def _join(nick, chan):
		pass

	def _kick(nick, chan, kicked):
		if kicked == _ident['nickname'] and chan == _settings['channel']:
			time.sleep(3)
			Command.join(chan, _Settings['key'])

	def _message(nick, chan, msg):
		if msg == '!test':
			Bot._queue.append(chan, 'It Works!')

	def _nick_in_use():
		error_exit('The bot is already running or nick is in use!')

	def _part(nick, chan):
		pass

	def _private(nick, msg):
		pass

	def _quit(nick):
		pass

	def _handle(data):
		args = data.split()
		if data.startswith('ERROR :Closing Link:'):
			raise Exception('Connection has closed.')
		elif data.startswith('ERROR :Reconnecting too fast, throttled.'):
			raise Exception('Connection has closed. (throttled)')
		elif args[0] == 'PING':
			Command._raw('PONG ' + args[1][1:])
		elif args[1] == '001':
			Event._connect()
		elif args[1] == '433':
			Event._nick_in_use()
		elif args[1] == 'INVITE':
			nick = args[0].split('!')[0][1:]
			chan = args[3][1:]
			Event._invite(nick, chan)
		elif args[1] == 'JOIN':
			nick = args[0].split('!')[0][1:]
			chan = args[2][1:]
			Event._join(nick, chan)
		elif args[1] == 'KICK':
			nick   = args[0].split('!')[0][1:]
			chan   = args[2]
			kicked = args[3]
			Event._kick(nick, chan, kicked)
		elif args[1] == 'PART':
			nick = args[0].split('!')[0][1:]
			chan = args[2]
			Event._part(nick, chan)
		elif args[1] == 'PRIVMSG':
			#ident = args[0][1:]
			nick   = args[0].split('!')[0][1:]
			chan   = args[2]
			msg    = ' '.join(args[3:])[1:]
			if msg.startswith('\001'):
				Event._ctcp(nick, chan, msg)
			elif chan == _ident['nickname']:
				Event._private(nick, msg)
			else:
				Event._message(nick, chan, msg)
		elif args[1] == 'QUIT':
			nick = args[0].split('!')[0][1:]
			Event._quit(nick)

class Loop:
	def _loops():
		threading.Thread(target=Loop._queue).start()

	def _queue():
		while True:
			try:
				if Bot._queue:
					Command._raw(Bot._queue.pop(0))
			except Exception as ex:
				error('Error occured in the queue handler!', ex)
			finally:
				time.sleep(_settings['throttle'])

# Main
if _connection['proxy']:
	try:
		import socks
	except ImportError:
		error_exit('Missing PySocks module! (https://pypi.python.org/pypi/PySocks)')
if _connection['ssl']:
	import ssl
else:
	del _cert, _connection['verify']
Bot = IRC()
Bot._run()