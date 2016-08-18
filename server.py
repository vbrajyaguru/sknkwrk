# server.py
## this is the code that runs on the nodes and provides methods for clients to get sensor
## data and execute commands
 
from __future__ import print_function
import Pyro4
import socket
import ConfigParser
import io
import os

class NodeServer(object):
	def __init__(self):
		self.name = socket.gethostname()
		self.conf = "server.conf"
		self.ip_addr = "127.0.0.1"
		self.hmac_key = ""
		self.hmac_key_ns = ""
		self.methods = ["get_fan_speed", "get_temps", "get_machine_type"]
		self.machinetype = ""
		self.attached_clients = []

	def list_clients(self):
		print("server {0} client list: {1}".format(self.name, self.attached_clients))

	@Pyro4.expose	
	def list_methods(self, client):
		print("server {0} received request to list supported methods from client {1}.".format(self.name, client))
		print("server {0} responding to {1} with: {2}".format(self.name, client, self.methods))
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
	def get_fan_speed(self, client):
		print("server {0} received request for fan speed from client {1}.".format(self.name, client))
		fanspeed = []
		fans = os.popen("ipmitool -c sdr type Fan | awk -F , /'RPM'/'{print $2}'")
		for f in fans.readlines():
			fanspeed.append(int(f.strip()))
		print("server {0} responding to {1} with: {2}".format(self.name, client,  fanspeed))
		return fanspeed

	@Pyro4.expose
	def get_temps(self, client):
		print("server {0} received request for temp from client {1}.".format(self.name, client))
		temps = []
		inlet = os.popen("ipmitool -c sdr type Temperature | awk -F , /'Inlet'/'{print $2}'").read()
		exhaust = os.popen("ipmitool -c sdr type Temperature | awk -F , /'Exhaust'/'{print $2}'").read()
		temps.append(int(inlet.strip()))
		temps.append(int(exhaust.strip()))
		print("server {0} responding to {1} with: {2}".format(self.name, client, temps))
		return temps
	
	@Pyro4.expose
	def get_machine_type(self, client):
		print("server {0} received request for machinetype from client {1}.".format(self.name, client))
		if self.machinetype == "":
			print("server {0} querying machinetype information.".format(self.name))
			manufacturer = os.popen("dmidecode --type 1 | awk -F : /'Manufacturer'/'{print $2}'").read().strip()
			product_name = os. popen("dmidecode --type 1 | awk -F : /'Product Name'/'{print $2}'").read().strip()
			bbpn = os.popen("dmidecode --type 2 | awk -F : /'Product Name'/'{print $2}'").read().strip()
			if manufacturer != "" and product_name != "":
				self.machinetype = manufacturer + " " + product_name
			elif bbpn != "":
				self.machinetype = bbpn
			else:
				self.machinetype = "notdefined"
		print("server {0} responding with: {1}".format(self.name, self.machinetype))
		return self.machinetype

	  
def main():
	server = NodeServer()

	try:
		# Load the configuration file
		with open(server.conf, "r") as file:
			server_config = file.read()
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(server_config))
		print("server loaded configuration file {0}".format(server.conf))


		# Read options from configuration file
		# Read application name
		try:
			if(config.get("application", "name") != ""):
				server.name = config.get("application", "name")
	                    	print("server using name \"{0}\"".format(server.name))
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        print("server config option name not found, using default name \"{0}\"".format(server.name))


		# Read ip address
		try:
			if(config.get("connection", "ip_addr") != ""):
				server.ip_addr = config.get("connection", "ip_addr")
				print("server {0} using ip_addr \"{1}\"".format(server.name, server.ip_addr))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("server {0} config option ip_addr not found, using default value \"{1}\"".format(server.name, server.ip_addr))  
		
		
		# Read server hmac key
		try:
			if(config.get("connection", "hmac_key") != ""):
				server.hmac_key = config.get("connection", "hmac_key")
				print("server {0} using hmac_key \"{1}\"".format(server.name, server.hmac_key))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("server {0} config option hmac_key not found, using default value \"{1}\"".format(server.name, server.hmac_key))


		# Read nameserver hmac key
		try:
			if(config.get("connection", "hmac_key_ns") != ""):
				server.hmac_key_ns = config.get("connection", "hmac_key_ns")
				print("server {0} using hmac_key_ns \"{1}\"".format(server.name, server.hmac_key_ns))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("server {0} config option hmac_key_ns not found, using default value \"{1}\"".format(server.name, server.hmac_key_ns))

	except IOError:
		print("server {0} configuration file \"{1}\" not found, will use default options".format(server.name, server.conf))


	Pyro4.config.HOST = server.ip_addr
	with Pyro4.Daemon() as daemon:
		daemon._pyroHmacKey = server.hmac_key
		server_uri = daemon.register(server)
		with Pyro4.locateNS(hmac_key=server.hmac_key_ns) as ns:
			ns.register("server."+server.name, server_uri)
		print("server {0} is running.".format(server.name))
		daemon.requestLoop()

if __name__ == "__main__":
   main()

