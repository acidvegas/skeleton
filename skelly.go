package main

import (
	"bufio"
	"crypto/tls"
	"flag"
	"fmt"
	"log"
	"net"
	"strings"
	"time"
)

// IRC color & control codes
const (
	bold       = "\x02"
	italic     = "\x1D"
	underline  = "\x1F"
	reverse    = "\x16"
	reset      = "\x0f"
	white      = "00"
	black      = "01"
	blue       = "02"
	green      = "03"
	red        = "04"
	brown      = "05"
	purple     = "06"
	orange     = "07"
	yellow     = "08"
	lightGreen = "09"
	cyan       = "10"
	lightCyan  = "11"
	lightBlue  = "12"
	pink       = "13"
	grey       = "14"
	lightGrey  = "15"
)

var (
	// Connection settings
	server   string
	port     int
	channel  string
	key      string
	password string
	ipv4     bool
	ipv6     bool
	vhost    string

	// SSL settings
	useSSL    bool
	sslVerify bool
	sslCert   string
	sslPass   string

	// Bot settings
	nick     string
	user     string
	real     string
	nickserv string
	operserv string
	mode     string
	flood    int
)

func init() {
	flag.StringVar(&server, "server", "", "The IRC server address.")
	flag.IntVar(&port, "port", 6667, "The port number for the IRC server.")
	flag.StringVar(&channel, "channel", "", "The IRC channel to join.")
	flag.StringVar(&key, "key", "", "The key (password) for the IRC channel, if required.")
	flag.StringVar(&password, "password", "", "The password for the IRC server.")
	flag.BoolVar(&ipv4, "v4", false, "Use IPv4 for the connection.")
	flag.BoolVar(&ipv6, "v6", false, "Use IPv6 for the connection.")
	flag.StringVar(&vhost, "vhost", "", "The VHOST to use for connection.")
	flag.BoolVar(&useSSL, "ssl", false, "Use SSL for the connection.")
	flag.BoolVar(&sslVerify, "ssl-verify", false, "Verify SSL certificates.")
	flag.StringVar(&sslCert, "ssl-cert", "", "The SSL certificate to use for the connection.")
	flag.StringVar(&sslPass, "ssl-pass", "", "The SSL certificate password.")
	flag.StringVar(&nick, "nick", "skelly", "The nickname to use for the bot.")
	flag.StringVar(&user, "user", "skelly", "The username to use for the bot.")
	flag.StringVar(&real, "real", "Development Bot", "The realname to use for the bot.")
	flag.StringVar(&mode, "mode", "+B", "The mode to set on the bot's nickname.")
	flag.StringVar(&nickserv, "nickserv", "", "The password for the bot's nickname to be identified with NickServ.")
	flag.StringVar(&operserv, "operserv", "", "The password for the bot's nickname to be identified with OperServ.")
	flag.IntVar(&flood, "flood", 3, "Delay between command usage.")
	flag.Parse()
}

func logfmt(option string, message string) string {
	switch option {
	case "DEBUG":
		return fmt.Sprintf("\033[95m%s\033[0m [\033[95mDEBUG\033[0m] %s", getnow(), message)
	case "ERROR":
		return fmt.Sprintf("\033[95m%s\033[0m [\033[31mERROR\033[0m] %s", getnow(), message)
	case "SEND":
		return fmt.Sprintf("\033[95m%s\033[0m [\033[92mSEND\033[0m] %s", getnow(), message)
	case "RECV":
		return fmt.Sprintf("\033[95m%s\033[0m [\033[96mRECV\033[0m] %s", getnow(), message)
	}
	return fmt.Sprintf("\033[95m%s\033[0m [\033[95mDEBUG\033[0m] %s", getnow(), message) // This should never happen
}

func color(msg string, foreground string, background string) string {
	if background != "" {
		return fmt.Sprintf("\x03%s,%s%s%s", foreground, background, msg, reset)
	}
	return fmt.Sprintf("\x03%s%s%s", foreground, msg, reset)
}

type Bot struct {
	nickname string
	username string
	realname string
	conn     net.Conn
	reader   *bufio.Reader
	writer   *bufio.Writer
	last     time.Time
	slow     bool
}

func Skeleton() *Bot {
	return &Bot{
		nickname: "skeleton",
		username: "skelly",
		realname: "Development Bot",
	}
}

func (bot *Bot) Connect() error {
	address := fmt.Sprintf("%s:%d", server, port)

	var networkType string
	switch {
	case ipv4:
		networkType = "tcp4"
	case ipv6:
		networkType = "tcp6"
	default:
		networkType = "tcp"
	}

	var dialer net.Dialer

	if vhost != "" {
		localAddr, err := net.ResolveTCPAddr(networkType, vhost+":0")
		if err != nil {
			return fmt.Errorf("failed to resolve local address: %w", err)
		}
		dialer.LocalAddr = localAddr
	}

	var err error
	if useSSL {
		tlsConfig := &tls.Config{
			InsecureSkipVerify: !sslVerify,
		}

		if sslCert != "" {
			var cert tls.Certificate
			cert, err = tls.LoadX509KeyPair(sslCert, sslPass)
			if err != nil {
				return fmt.Errorf("failed to load SSL certificate: %w", err)
			}
			tlsConfig.Certificates = []tls.Certificate{cert}
		}

		bot.conn, err = tls.DialWithDialer(&dialer, networkType, address, tlsConfig)
	} else {
		bot.conn, err = dialer.Dial(networkType, address)
	}

	if err != nil {
		return fmt.Errorf("failed to dial: %w", err)
	}

	bot.reader = bufio.NewReader(bot.conn)
	bot.writer = bufio.NewWriter(bot.conn)

	if password != "" {
		bot.raw("PASS " + password)
	}
	bot.raw(fmt.Sprintf("USER %s 0 * :%s", user, real))
	bot.raw("NICK " + nick)

	return nil
}

func (bot *Bot) raw(data string) {
	if bot.writer != nil {
		bot.writer.WriteString(data + "\r\n")
		bot.writer.Flush()
		if strings.Split(data, " ")[0] == "PONG" {
			fmt.Println(logfmt("SEND", "\033[93m"+data+"\033[0m"))
		} else {
			fmt.Println(logfmt("SEND", data))
		}
	}
}

func (bot *Bot) sendMsg(target string, msg string) {
	bot.raw(fmt.Sprintf("PRIVMSG %s :%s", target, msg))
}

func (bot *Bot) handle(data string) {
	parts := strings.Fields(data)

	if len(parts) < 2 {
		return
	}

	if parts[0] != "PING" {
		parts[1] = "\033[38;5;141m" + parts[1] + "\033[0m"
	}
	coloredData := strings.Join(parts, " ")
	fmt.Println(logfmt("RECV", coloredData))

	parts = strings.Fields(data)
	if parts[0] == "PING" {
		bot.raw("PONG " + parts[1])
		return
	} else {
		command := parts[1]
		switch command {
		case "001": // RPL_WELCOME
			bot.raw("MODE " + nick + " " + mode)

			if nickserv != "" {
				bot.raw("PRIVMSG NickServ :IDENTIFY " + nickserv)
			}

			if operserv != "" {
				bot.raw("OPER " + nick + " " + operserv)
			}

			go func() {
				time.Sleep(15 * time.Second)
				if key != "" {
					bot.raw("JOIN " + channel + " " + key)
				} else {
					bot.raw("JOIN " + channel)
				}
			}()
		case "PRIVMSG":
			bot.eventPrivMsg(data)
		}
	}
}

func getnow() string {
	return time.Now().Format("03:04:05")
}

func (bot *Bot) eventPrivMsg(data string) {
	parts := strings.Split(data, " ")
	ident := strings.TrimPrefix(parts[0], ":")
	nick := strings.Split(ident, "!")[0]
	target := parts[2]
	msg := strings.Join(parts[3:], " ")[1:]

	if target == bot.nickname {
		// Private message handling
	} else if strings.HasPrefix(target, "#") {
		if target == channel {
			if msg == "!test" {
				bot.sendMsg(channel, nick+": Test successful!")
			}
		}
	}
}
func main() {
	for {
		fmt.Printf("\033[90m%s\033[0m [\033[95mDEBUG\033[0m] Connecting to %s:%d and joining %s\n", getnow(), server, port, channel)

		bot := Skeleton()
		err := bot.Connect()

		if err != nil {
			log.Printf("\033[90m%s\033[0m [\033[31mERROR\033[0m]\033[93m Failed to connect to server! Retrying in 15 seconds... \033[90m(%v)\033[0m", getnow(), err)
		} else {
			for {
				line, _, err := bot.reader.ReadLine()
				if err != nil {
					log.Printf("\033[90m%s\033[0m [\033[31mERROR\033[0m]\033[93m Lost connection to server! Retrying in 15 seconds... \033[90m(%v)\033[0m", getnow(), err)
					break
				}
				bot.handle(string(line))
			}
		}

		if bot.conn != nil {
			bot.conn.Close()
		}

		time.Sleep(15 * time.Second)
	}
}
