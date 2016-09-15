# server.py
## this is the code that runs on the nodes and provides methods for clients to get sensor
## data and execute commands
 
from __future__ import print_function
import Pyro4
import socket
import ConfigParser
import io
import os
import sys
import logging


#@Pyro4.behavior(instance_mode="percall")
class NodeServer(object):
	def __init__(self):
		self.name = socket.gethostname()
		self.conf = "server.conf"
		self.ip_addr = "127.0.0.1"
		self.hmac_key = ""
		self.hmac_key_ns = ""
		self.logfile = "server.log"
		self.loglevel = "DEBUG"
		self.methods = ["get_fan_speed", "get_temps", "get_machine_type", "set_fan_speed_offset"]
		self.machinetype = ""
		self.attached_clients = []

	def list_clients(self):
		logging.debug("server %s client list: %s", self.name, self.attached_clients)

	@Pyro4.expose	
	def list_methods(self, client):
		logging.debug("server %s received request to list supported methods from client %s.", self.name, client)
		logging.debug("server %s responding to %s with: %s", self.name, client, self.methods)
		return self.methods
		
	@Pyro4.expose
	def join(self, client):
		logging.info("server %s adding new client %s", self.name, client)
		self.attached_clients.append(client)
		self.list_clients()	

	@Pyro4.expose
	def leave(self, client):
		logging.info("server %s removing client %s", self.name, client)
		self.attached_clients.remove(client)
		self.list_clients()	
	
	@Pyro4.expose
	def get_fan_speed(self, client):
		logging.info("server %s received request for fan speed from client %s.", self.name, client)
		fanspeed = []
		fans = os.popen("ipmitool -c sdr type Fan | awk -F , /'RPM'/'{print $2}'")
		for f in fans.readlines():
                        fanspeed.append(int(f.strip()))
		logging.debug("server %s responding to %s with: %s", self.name, client,  fanspeed)
		return fanspeed

	@Pyro4.expose
	def set_fan_speed_offset(self, client):
		logging.info("server %s received request to set fan speed offset from client %s.", self.name, client)
		os.popen("racadm set system.thermalsettings.FanSpeedOffset 1")

	@Pyro4.expose
	def get_temps(self, client):
		logging.info("server %s received request for temp from client %s.", self.name, client)
		temps = []
		inlet = os.popen("ipmitool -c sdr type Temperature | awk -F , /'Inlet'/'{print $2}'").read()
		exhaust = os.popen("ipmitool -c sdr type Temperature | awk -F , /'Exhaust'/'{print $2}'").read()
		temps.append(int(inlet.strip()))
		temps.append(int(exhaust.strip()))
		logging.debug("server %s responding to %s with: %s", self.name, client, temps)
		return temps
	
	@Pyro4.expose
	def get_machine_type(self, client):
		logging.info("server %s received request for machinetype from client %s.", self.name, client)
		if self.machinetype == "":
			logging.debug("server %s querying machinetype information.", self.name)
                        manufacturer = os.popen("dmidecode --type 1 | awk -F : /'Manufacturer'/'{print $2}'").read().strip()
                        product_name = os.popen("dmidecode --type 1 | awk -F : /'Product Name'/'{print $2}'").read().strip()
			bbpn = os.popen("dmidecode --type 2 | awk -F : /'Product Name'/'{print $2}'").read().strip()
			if manufacturer != "" and product_name != "":
				self.machinetype = manufacturer + " " + product_name
			elif bbpn != "":
				self.machinetype = bbpn
			else:
				self.machinetype = "notdefined"
		logging.debug("server %s responding with: %s", self.name, self.machinetype)
		return self.machinetype

	  
def main():
	server = NodeServer()
	self_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	logging_levels = {"INFO":20, "WARNING":30, "DEBUG":10, "CRITICAL":50, "ERROR":40}

	try:
		# Load the configuration file
                conf_location = os.path.join(self_location, server.conf)
		with open(conf_location, "r") as file:
			server_config = file.read()
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(server_config))


		# Read options from configuration file
		# Read log filename
		try:
                        if(config.get("logging", "logfile") != ""):
                                server.logfile = config.get("logging", "logfile")
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        print("server config option logfile not found, using default logging file \"{0}\"".format(server.logfile), file=sys.stderr)
                logf_location = os.path.join(self_location, server.logfile)


		# Read log level and convert into numeric value
		logstr_info = ""
                try:
                        if(config.get("logging", "loglevel") != ""):
                                loglevel = config.get("logging", "loglevel").upper()
                                if(logging_levels.has_key(loglevel)):
                                        logstr_info = "server using log level \"" + loglevel + "\""
                                        server.loglevel = loglevel
                                else:
                                        logstr_info = "server config option loglevel \"" + loglevel + "\" not valid, using default logging level \"" + server.loglevel + "\""
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        logstr_info = "server config option loglevel not found, using default logging level \"" + server.loglevel + "\""
                numeric_loglevel = logging_levels[server.loglevel]
                logging.basicConfig(filename=logf_location, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=numeric_loglevel)
                logging.info("server loaded configuration file %s", server.conf)
                logging.info(logstr_info)


		# Read application name
		try:
			if(config.get("application", "name") != ""):
				server.name = config.get("application", "name")
	                        logging.debug("server using name \"%s\"", server.name)
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        logging.debug("server config option name not found, using default name \"%s\"", server.name)


		# Read ip address
		try:
			if(config.get("connection", "ip_addr") != ""):
				server.ip_addr = config.get("connection", "ip_addr")
				logging.debug("server %s using ip_addr \"%s\"", server.name, server.ip_addr)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.warning("server %s config option ip_addr not found, using default value \"%s\"", server.name, server.ip_addr)
		
		
		# Read server hmac key
		try:
			if(config.get("connection", "hmac_key") != ""):
				server.hmac_key = config.get("connection", "hmac_key")
				logging.debug("server %s using hmac_key \"%s\"", server.name, server.hmac_key)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.debug("server %s config option hmac_key not found, using default value \"%s\"", server.name, server.hmac_key)


		# Read nameserver hmac key
		try:
			if(config.get("connection", "hmac_key_ns") != ""):
				server.hmac_key_ns = config.get("connection", "hmac_key_ns")
				logging.debug("server %s using hmac_key_ns \"%s\"", server.name, server.hmac_key_ns)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.debug("server %s config option hmac_key_ns not found, using default value \"%s\"", server.name, server.hmac_key_ns)

	except IOError:
		logf_location = os.path.join(self_location, server.logfile)
                numeric_loglevel = logging_levels[server.loglevel]
                logging.basicConfig(filename=logf_location, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=numeric_loglevel)
		logging.warning("server %s configuration file \"%s\" not found, will use default options", server.name, server.conf)


	Pyro4.config.HOST = server.ip_addr
	with Pyro4.Daemon() as daemon:
		daemon._pyroHmacKey = server.hmac_key
		server_uri = daemon.register(server)
		with Pyro4.locateNS(hmac_key=server.hmac_key_ns) as ns:
			ns.register("server."+server.name, server_uri)
		print("server {0} is running.".format(server.name), file=sys.stdout)
		logging.info("server %s is running.", server.name)
		daemon.requestLoop()

if __name__ == "__main__":
   main()

