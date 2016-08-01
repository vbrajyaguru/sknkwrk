# server.py
## this is the code that runs on the nodes and provides methods for clients to get sensor
## data and execute commands
 
from __future__ import print_function
import Pyro4
import socket
import ConfigParser
import io


class NodeServer(object):
	def __init__(self):
		self.name = socket.gethostname()
		self.conf = "server.conf"
		self.ip_addr = "127.0.0.1"
		self.hmac_key = ""
		self.hmac_key_ns = ""
		self.methods = ["get_fan_speed", "get_temps", "get_machine_type"]
		self.fanspeed = ["8400RPM", "8400RPM", "8160RPM", "7680RPM","7440RPM","7560RPM"]
		self.temps = ["24degrees C", "32degrees C"]
		self.machinetype = "Dell PowerEdge R730"
		self.attached_clients = []

	def list_clients(self):
		print("PRIVATE-FUNC: server {0} client list: {1}".format(self.name, self.attached_clients))

	@Pyro4.expose	
	def list_methods(self):
		print("server {0} received request to list supported methods.".format(self.name))
		return self.methods
		
	@Pyro4.expose
	def join(self, client):
		print("server {0} adding new client {1}".format(self.name, client))
		self.attached_clients.append(client)
		self.list_clients()	

	@Pyro4.expose
	def leave(self, client):
		print("server {0} removing client {1}".format(self.name, client))
		self.attached_clients.remove(client)
		self.list_clients()	
	
	@Pyro4.expose
	def get_fan_speed(self):
		print("server {0} received request for fan speed.".format(self.name))
		return self.fanspeed
	
	@Pyro4.expose
	def get_temps(self):
		print("server {0} received request for temp.".format(self.name))
		return self.temps
	
	@Pyro4.expose
	def get_machine_type(self):
		print("server {0} received request for machinetype.".format(self.name))
		return self.machinetype
	  
def main():
	server = NodeServer()

	try:
		# Load the configuration file
		with open(server.conf, "r") as file:
			server_config = file.read()
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(server_config))
		print("Server {0} loaded configuration file {1}".format(server.name, server.conf))


		# Read options from configuration file
		# Read ip address
		try:
			if(config.get("connection", "ip_addr") != ""):
				server.ip_addr = config.get("connection", "ip_addr")
				print("Server {0} using ip_addr \"{1}\"".format(server.name, server.ip_addr))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("Server {0} config option ip_addr not found, using default value \"{1}\"".format(server.name, server.ip_addr))  
		
		
		# Read server hmac key
		try:
			if(config.get("connection", "hmac_key") != ""):
				server.hmac_key = config.get("connection", "hmac_key")
				print("Server {0} using hmac_key \"{1}\"".format(server.name, server.hmac_key))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("Server {0} config option hmac_key not found, using default value \"{1}\"".format(server.name, server.hmac_key))


		# Read nameserver hmac key
		try:
			if(config.get("connection", "hmac_key_ns") != ""):
				server.hmac_key_ns = config.get("connection", "hmac_key_ns")
				print("Server {0} using hmac_key_ns \"{1}\"".format(server.name, server.hmac_key_ns))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("Server {0} config option hmac_key_ns not found, using default value \"{1}\"".format(server.name, server.hmac_key_ns))

	except IOError:
		print("Server {0} configuration file \"{1}\" not found, will use default options".format(server.name, server.conf))


	Pyro4.config.HOST = server.ip_addr
	with Pyro4.Daemon() as daemon:
		daemon._pyroHmacKey = server.hmac_key
		server_uri = daemon.register(server)
		with Pyro4.locateNS(hmac_key=server.hmac_key_ns) as ns:
			ns.register("server."+server.name, server_uri)
		print("Server {0} is running.".format(server.name))
		daemon.requestLoop()

if __name__ == "__main__":
   main()

