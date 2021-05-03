#!/usr/bin/env python
# Asyncronous IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/asyncirc)
# events.py

import asyncio
import logging

import config

class Event:
	def __init__(self, bot):
		self.Bot = bot

	def connect(self):
		if config.settings.modes:
			Commands.raw(f'MODE {config.ident.nickname} +{config.settings.modes}')
		if config.login.nickserv:
			Commands.sendmsg('NickServ', f'IDENTIFY {config.ident.nickname} {config.login.nickserv}')
		if config.login.operator:
			Commands.raw(f'OPER {config.ident.username} {config.login.operator}')
		Commands.join_channel(config.connection.channel, config.connection.key)

	async def disconnect(self):
		self.writer.close()
		await self.writer.wait_closed()
		asyncio.sleep(config.throttle.reconnect)

	def join_channel(self):
		pass

	def kick(self):
		pass

	def invite(self):
		pass

	def message(self):
		pass

	def nick_in_use(self):
		new_nick = 'a' + str(random.randint(1000,9999))
		Command.nick(new_nick)

	def part_channel(self):
		pass

	def private_message(self):
		pass

	def quit(self):
		pass

	async def handler(self, data):
		logging.info(data)
		args = data.split()
		if args[0] == 'PING':
			self.raw('PONG ' + args[1][1:])
		elif args[1] == '001': #RPL_WELCOME
			self.connect()
		elif args[1] == '433': #ERR_NICKNAMEINUSE
			self.nick_in_use()
