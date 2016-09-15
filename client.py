# client.py
## this is the code that runs on Rpi and connects to servers found in nameserver lookup

from __future__ import print_function
import Pyro4
import ConfigParser
import io
import socket
import os
import sys
import logging


class Client(object):
	def __init__(self):
		self.name = socket.gethostname()
		self.conf = "client.conf"
		self.logfile = "client.log"
		self.loglevel = "INFO"
		self.hmac_key = ""
		self.hmac_key_ns = ""

		
def main():
	client = Client()
	self_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	logging_levels = {"INFO":20, "WARNING":30, "DEBUG":10, "CRITICAL":50, "ERROR":40}

	try:
		# Load the configuration file
		conf_location = os.path.join(self_location, client.conf)
                with open(conf_location, "r") as file:
                        client_config = file.read()
                config = ConfigParser.RawConfigParser(allow_no_value=True)
                config.readfp(io.BytesIO(client_config))

                # Read options from configuration file
		# Read log filename
		try:
			if(config.get("logging", "logfile") != ""):
				client.logfile = config.get("logging", "logfile")
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			print("client config option logfile not found, using default logging file \"{0}\"".format(client.logfile), file=sys.stderr)
		logf_location = os.path.join(self_location, client.logfile)

		# Read log level and convert into numeric value
		logstr_info = ""
		try:
                        if(config.get("logging", "loglevel") != ""):
                                loglevel = config.get("logging", "loglevel").upper()
				if(logging_levels.has_key(loglevel)):
					logstr_info = "client using log level \"" + loglevel + "\""
					client.loglevel = loglevel
				else:
					logstr_info = "client config option loglevel \"" + loglevel + "\" not valid, using default logging level \"" + client.loglevel + "\""
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logstr_info = "client config option loglevel not found, using default logging level \"" + client.loglevel + "\""
		numeric_loglevel = logging_levels[client.loglevel]
		logging.basicConfig(filename=logf_location, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=numeric_loglevel)
		logging.info("client loaded configuration file %s", client.conf)
		logging.info(logstr_info)

		# Read application name
		try:
			if(config.get("application", "name") != ""):
				client.name = config.get("application", "name")
				logging.debug("client using name \"%s\"", client.name)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.debug("client config option name not found, using default name \"%s\"", client.name)

                # Read server hmac key
                try:
                        if(config.get("connection", "hmac_key") != ""):
                                client.hmac_key = config.get("connection", "hmac_key")
				logging.debug("client %s using hmac_key \"%s\"", client.name, client.hmac_key)
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.debug("client %s config option hmac_key not found, using default value \"%s\"", client.name, client.hmac_key)

                # Read nameserver hmac key
                try:
                        if(config.get("connection", "hmac_key_ns") != ""):
                                client.hmac_key_ns = config.get("connection", "hmac_key_ns")
                                logging.debug("client %s using hmac_key_ns \"%s\"", client.name, client.hmac_key_ns)
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			logging.debug("client %s config option hmac_key_ns not found, using default value \"%s\"", client.name, client.hmac_key_ns)

	except IOError:
		logf_location = os.path.join(self_location, client.logfile)
		numeric_loglevel = logging_levels[client.loglevel]
                logging.basicConfig(filename=logf_location, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=numeric_loglevel)
		logging.warning("client %s configuration file \"%s\" not found, will use default options", client.name, client.conf)


	ns = Pyro4.locateNS(hmac_key=client.hmac_key_ns)
	for rem_server, rem_server_uri in ns.list(prefix="server.").items():
		logging.info("client %s joining %s", client.name, rem_server)
		with Pyro4.Proxy(rem_server_uri) as server:
			server._pyroHmacKey = client.hmac_key
			server.join(client.name)
		
			logging.debug("client %s requested server supported methods: %s", client.name, server.list_methods(client.name))
			logging.debug("client %s requested server machinetype: %s", client.name, server.get_machine_type(client.name))
			logging.debug("client %s requested server fan speed: %s", client.name, server.get_fan_speed(client.name))
			logging.debug("client %s requested server temps: %s", client.name, server.get_temps(client.name))

			logging.info("client %s leaving %s", client.name, rem_server)
			server.leave(client.name)
		
		
if __name__ == "__main__":
	main()
	
