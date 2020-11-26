#!/usr/bin/env python
# IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# config.py

class connection:
	server     = 'irc.supernets.org'
	port       = 6667
	proxy      = None
	ipv6       = False
	ssl        = False
	ssl_verify = False
	vhost      = None
	channel    = '#500'
	key        = None

class cert:
	key      = None
	file     = None
	password = None

class ident:
	nickname = 'WORMSEC'
	username = 'wormsec'
	realname = '48 0 US 3.7.2.1'

class login:
	network  = 'ELSILRACLIHP'
	nickserv = None
	operator = None

class throttle:
	command   = 3
	reconnect = 10
	rejoin    = 3

class settings:
	admin    = 'nick!user@host.name' # Must be in nick!user@host format (Can use wildcards here)
	cmd_char = '!'
	log      = False
	modes    = None
