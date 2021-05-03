#!/usr/bin/env python
# Asyncronous IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# commands.py

class Command:
	def __init__(self, bot):
		self.Bot = bot

	def action(self, target, msg):
		self.sendmsg(target, f'\x01ACTION {msg}\x01')

	def join_channel(self, chan, key=None):
		self.raw(f'JOIN {chan} {key}') if key else raw('JOIN ' + chan)

	def mode(self, target, mode):
		self.raw(f'MODE {target} {mode}')

	def nick(self, new_nick):
		self.raw('NICK ' + new_nick)

	def notice(self, target, msg):
		self.raw(f'NOTICE {target} :{msg}')

	def part_channel(self, chan, msg=None):
		self.raw(f'PART {chan} {msg}') if msg else raw('PART ' + chan)

	def quit(self, msg=None):
		self.raw('QUIT :' + msg) if msg else raw('QUIT')

	def raw(self, data):
		self.Bot.writer.write(data[:510].encode('utf-8') + b'\r\n')

	def register(self, nickname, username, realname, password=None):
		if password:
			self.raw('PASS ' + password)
		self.raw('NICK ' + nickname)
		self.raw(f'USER {username} 0 * :{realname}')

	def sendmsg(self, target, msg):
		self.raw(f'PRIVMSG {target} :{msg}')

	def topic(self, chan, data):
		self.raw(f'TOPIC {chan} :{text}')