# command line arguments to start a pyro nameserver

# start nameserver and bind to localhost (default) on random port number. Nameserver is not
# visible from outside network
#pyro4-ns

# start nameserver and bind to ip address specified on available random port number
#pyro4-ns -n 192.168.0.104
#pyro4-ns --host="192.168.0.104"

# start nameserver and bind to ip address specified and use hmac key specified
#pyro4-ns -n 192.168.0.104 -k PEPC5uUcY565SJyepJIo 
pyro4-ns --host="192.168.0.104" --key "PEPC5uUcY565SJyepJIo"

