package main

import (
	"bufio"
	"crypto/tls"
	"flag"
	"fmt"
	"log"
	"net"
	"strconv"
	"strings"
	"time"
)

var (
	server  string
	port    string
	useSSL  bool
	channel string
	key     string
)

func init() {
	flag.StringVar(&server, "server", "", "The IRC server address (e.g., 1.2.3.4)")
	flag.StringVar(&port, "port", "6667", "The port of the IRC server (e.g., 6667)")
	flag.BoolVar(&useSSL, "ssl", false, "Whether to use SSL or not")
	flag.StringVar(&channel, "channel", "", "The IRC channel to join (e.g., #channelName)")
	flag.StringVar(&key, "key", "", "The IRC channel key")
	flag.Parse()
}

const (
	nickname = "[dev]skelly"
	username = "golang"
	realname = "IRC Bot Skeleton in Golang"
)

func checkArgs() {
	if server == "" || channel == "" {
		log.Fatal("Both server and channel arguments are required.")
	} else if channel[0] != '#' {
		channel = "#" + channel // Using # on the commandline requires escaping, lets just make it optional
	}
	num, err := strconv.Atoi(port)
	if err != nil {
		log.Fatal("Invalid port number.")
	} else if num < 1 || num > 65535 {
		log.Fatal("Port number must be between 1 and 65535.")
	}
}

func main() {
	checkArgs()

	fullServer := fmt.Sprintf("%s:%s", server, port)

	var conn net.Conn
	var err error

	if useSSL {
		conn, err = tls.Dial("tcp", fullServer, &tls.Config{InsecureSkipVerify: true})
	} else {
		conn, err = net.Dial("tcp", fullServer)
	}
	if err != nil {
		log.Printf("Failed to connect: %v", err)
		time.Sleep(15 * time.Second)
	}

	messageChannel := make(chan string, 100) // for received IRC messages
	sendChannel := make(chan string, 100)    // for messages to send to the IRC server
	quit := make(chan struct{})

	timeoutDuration := 300 * time.Second
	timeoutTimer := time.NewTimer(timeoutDuration)

	go func() {
		reader := bufio.NewReader(conn)
		for {
			line, err := reader.ReadString('\n')
			if err != nil {
				log.Println("Error reading from server:", err)
				conn.Close()
				close(quit)
				return
			}
			select {
			case messageChannel <- line:
				timeoutTimer.Reset(timeoutDuration)
			case <-quit:
				return
			case <-timeoutTimer.C:
				log.Println("No data received for 300 seconds. Reconnecting...")
				conn.Close()
				close(quit)
				return
			}
		}
	}()

	go func() {
		for {
			select {
			case message := <-sendChannel:
				data := []byte(message)
				if len(data) > 510 {
					data = data[:510]
				}
				_, err := conn.Write(append(data, '\r', '\n'))
				if err != nil {
					log.Println("Error writing to server:", err)
					conn.Close()
					close(quit)
					return
				}
			case <-quit:
				return
			}
		}
	}()

	// Initial handshake
	sendChannel <- fmt.Sprintf("NICK %s", nickname)
	sendChannel <- fmt.Sprintf("USER %s 0 * :%s", username, realname)

	for {
		dataHandler(<-messageChannel, sendChannel)
	}
}

func eventPrivate(nick, ident, msg string) {
	fmt.Println("Private message from", nick, ":", msg)
}

func eventMessage(nick, ident, channel, msg string) {
	fmt.Println("Channel message from", nick, ":", msg)
	if ident == "acidvegas!~stillfree@most.dangerous.motherfuck" {
		args := strings.Split(msg, " ")
		switch args[0] {
		case "!masscan":
			fmt.Println("The value is a")
		case "!nmap":
			fmt.Println("The value is b")
		case "!httpx":
			fmt.Println("The value is c")
		case "!nuclei":
			fmt.Println("The value is c")
		default:
			fmt.Println("Unknown value")
		}
	}
}

func dataHandler(data string, sendChannel chan<- string) {
	fmt.Println(data)
	parts := strings.Split(data, " ")

	if parts[0] == "PING" {
		sendChannel <- fmt.Sprintf("PONG %s", parts[1])
	} else if parts[1] == "001" { // RPL_WELCOME
		time.Sleep(5 * time.Second) // JOIN channel delay after connection, required for many networks with flood protection / mitigation
		sendChannel <- fmt.Sprintf("JOIN %s %s", channel, key)
	} else if parts[1] == "KICK" {
		return
	} else if len(parts) > 3 && parts[1] == "PRIVMSG" {
		nick := strings.Split(parts[0], "!")[0][1:]
		ident := strings.Split(parts[0], ":")[1]
		target := parts[2]
		msg := strings.Join(parts[3:], " ")[1:]
		if target == nickname { // Private Messages
			eventPrivate(nick, ident, msg)
		} else if target == channel { // Channel Messages
			eventMessage(nick, ident, channel, msg)
		}
	}
}
