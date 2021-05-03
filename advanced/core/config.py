#!/usr/bin/env python
# Asyncronous IRC Bot Skeleton - Developed by acidvegas in Python (https://acid.vegas/skeleton)
# config.py

class connection:
	server        = 'irc.server.com'
	port          = 6667
	ipv6          = False
	ssl           = False
	ssl_verify    = False
	vhost         = None
	channel       = '#dev'
	key           = None
	modes         = None

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