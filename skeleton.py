#!/usr/bin/env python
# Skeleton IRC bot - developed by acidvegas in python (https://git.acid.vegas/skeleton)
import argparse
import asyncio
import logging
import logging.handlers
import ssl

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

def color(msg: str, foreground: str, background: str='') -> str:
    '''
    Color a string with the specified foreground and background colors.
    
    :param msg: The string to color.
    :param foreground: The foreground color to use.
    :param background: The background color to use.
    '''
    return f'\x03{foreground},{background}{msg}{reset}' if background else f'\x03{foreground}{msg}{reset}'

def ssl_ctx() -> ssl.SSLContext:
    '''Create a SSL context for the connection.'''
    ctx = ssl.create_default_context()
    ctx.verify_mode = ssl.CERT_NONE # Comment out this line to verify hosts
    #ctx.load_cert_chain('/path/to/cert', password='loldongs')
    return ctx

class Bot():
    def __init__(self):
        self.nickname = 'skeleton'
        self.username = 'skelly'
        self.realname = 'Developement Bot'
        self.reader   = None
        self.writer   = None

    async def action(self, chan: str, msg: str):
        '''
        Send an ACTION to the IRC server.

        :param chan: The channel to send the ACTION to.
        :param msg: The message to send to the channel.
        '''
        await self.sendmsg(chan, f'\x01ACTION {msg}\x01')

    async def raw(self, data: str):
        '''
        Send raw data to the IRC server.
		
        :param data: The raw data to send to the IRC server. (512 bytes max including crlf)
        '''
        self.writer.write(data[:510].encode('utf-8') + b'\r\n')

    async def sendmsg(self, target: str, msg: str):
        '''
        Send a PRIVMSG to the IRC server.
        
        :param target: The target to send the PRIVMSG to. (channel or user)
        :param msg: The message to send to the target.
        '''
        await self.raw(f'PRIVMSG {target} :{msg}')

    async def connect(self):
        '''Connect to the IRC server.'''
        while True:
            try:
                options = {
                    'host'       : args.server,
                    'port'       : args.port if args.port else 6697 if args.ssl else 6667,
                    'limit'      : 1024, # Buffer size in bytes (don't change this unless you know what you're doing)
                    'ssl'        : ssl_ctx() if args.ssl else None,
                    'family'     : 10 if args.v6 else 2, # 10 = AF_INET6 (IPv6), 2 = AF_INET (IPv4)
                    'local_addr' : args.vhost if args.vhost else None # Can we just leave this as args.vhost?
                }
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(**options), 15) # 15 second timeout
                if args.password:
                    await self.raw('PASS ' + args.password) # Rarely used, but IRCds may require this
                await self.raw(f'USER {self.username} 0 * :{self.realname}') # These lines must be sent upon connection
                await self.raw('NICK ' + self.nickname)                      # They are to identify the bot to the server
                while not self.reader.at_eof():
                    data = await asyncio.wait_for(self.reader.readuntil(b'\r\n'), 300) # 5 minute ping timeout
                    await self.handle(data.decode('utf-8').strip()) # Handle the data received from the IRC server
            except Exception as ex:
                logging.error(f'failed to connect to {args.server} ({str(ex)})')
            finally:
                await asyncio.sleep(30) # Wait 30 seconds before reconnecting

    async def handle(self, data: str):
        '''
        Handle the data received from the IRC server.
        
        :param data: The data received from the IRC server.
        '''
        logging.info(data)
        try:
            parts = data.split()
            if data.startswith('ERROR :Closing Link:'):
                raise Exception('BANNED')
            if parts[0] == 'PING':
                await self.raw('PONG ' + parts[1]) # Respond to the server's PING request with a PONG to prevent ping timeout
            elif parts[1] == '001': # RPL_WELCOME
                await self.raw(f'MODE {self.nickname} +B') # Set user mode +B (Bot)
                await self.sendmsg('NickServ', 'IDENTIFY {self.nickname} simps0nsfan420') # Identify to NickServ
                await self.raw('OPER MrSysadmin fartsimps0n1337') # Oper up
                await asyncio.sleep(10) # Wait 10 seconds before joining the channel (required by some IRCds to wait before JOIN)
                if parts.key:
                    await self.raw(f'JOIN {args.channel} {args.key}') # Join the channel with the key
                else:
                    await self.raw(f'JOIN {args.channel}')
            elif parts[1] == '433': # ERR_NICKNAMEINUSE
                self.nickname += '_' # If the nickname is already in use, append an underscore to the end of it
                await self.raw('NICK ' + self.nickname) # Send the new nickname to the server
            elif parts[1] == 'KICK':
                chan   = parts[2]
                kicked = parts[3]
                if kicked == self.nickname:
                    await asyncio.sleep(3)
                    await self.raw(f'JOIN {chan}')
            elif parts[1] == 'PRIVMSG':
                ident  = parts[0][1:]
                nick   = parts[0].split('!')[0][1:]
                target = parts[2]
                msg    = ' '.join(parts[3:])[1:]
                if target == self.nickname:
                    pass # Handle private messages here
                if target.startswith('#'): # Channel message
                    if msg.startswith('!'):
                        if msg == '!hello':
                            await self.sendmsg(target, f'Hello {nick}! Do you like ' + color('colors?', green))
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass # Some IRCds allow invalid UTF-8 characters, this is a very important exception to catch
        except Exception as ex:
            logging.exception(f'Unknown error has occured! ({ex})')


def setup_logger(log_filename: str, to_file: bool = False):
    '''
    Set up logging to console & optionally to file.

    :param log_filename: The filename of the log file
    '''
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(message)s', '%I:%M %p'))
    if to_file:
        fh = logging.handlers.RotatingFileHandler(log_filename+'.log', maxBytes=250000, backupCount=3, encoding='utf-8') # Max size of 250KB, 3 backups
        fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)9s | %(filename)s.%(funcName)s.%(lineno)d | %(message)s', '%Y-%m-%d %I:%M %p')) # We can be more verbose in the log file
        logging.basicConfig(level=logging.NOTSET, handlers=(sh,fh))
    else:
        logging.basicConfig(level=logging.NOTSET, handlers=(sh,))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Connect to an IRC server.") # The arguments without -- are required arguments.
    parser.add_argument("server", help="The IRC server address.")
    parser.add_argument("channel", help="The IRC channel to join.")
    parser.add_argument("--password", help="The password for the IRC server.")
    parser.add_argument("--port", type=int, help="The port number for the IRC server.") # Port is optional, will default to 6667/6697 depending on SSL.
    parser.add_argument("--ssl", action="store_true", help="Use SSL for the connection.")
    parser.add_argument("--v4", action="store_true", help="Use IPv4 for the connection.")
    parser.add_argument("--v6", action="store_true", help="Use IPv6 for the connection.")
    parser.add_argument("--key",  default="", help="The key (password) for the IRC channel, if required.")
    parser.add_argument("--vhost", help="The VHOST to use for connection.")
    args = parser.parse_args()

    print(f"Connecting to {args.server}:{args.port} (SSL: {args.ssl}) and joining {args.channel} (Key: {args.key or 'None'})")

    setup_logger('skeleton', to_file=True) # Optionally, you can log to a file, change to_file to False to disable this.

    bot = Bot() # We define this here as an object so we can call it from an outside function if we need to.

    asyncio.run(bot.connect())