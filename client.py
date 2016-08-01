# client.py
## this is the code that runs on Rpi and connects to servers found in nameserver lookup

from __future__ import print_function
import Pyro4
import ConfigParser
import io


class Client(object):
	def __init__(self):
		self.name = "Rpi"
		self.conf = "client.conf"
		self.hmac_key = ""
		self.hmac_key_ns = ""

		
def main():
	client = Client()

	try:
		# Load the configuration file
                with open(client.conf, "r") as file:
                        client_config = file.read()
                config = ConfigParser.RawConfigParser(allow_no_value=True)
                config.readfp(io.BytesIO(client_config))
                print("client {0} loaded configuration file {1}".format(client.name, client.conf))


                # Read options from configuration file
                # Read server hmac key
                try:
                        if(config.get("connection", "hmac_key") != ""):
                                client.hmac_key = config.get("connection", "hmac_key")
                                print("client {0} using hmac_key \"{1}\"".format(client.name, client.hmac_key))
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        print("client {0} config option hmac_key not found, using default value \"{1}\"".format(client.name, client.hmac_key))


                # Read nameserver hmac key
                try:
                        if(config.get("connection", "hmac_key_ns") != ""):
                                client.hmac_key_ns = config.get("connection", "hmac_key_ns")
                                print("client {0} using hmac_key_ns \"{1}\"".format(client.name, client.hmac_key_ns))
                except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        print("client {0} config option hmac_key_ns not found, using default value \"{1}\"".format(client.name, client.hmac_key_ns))


	except IOError:
                print("client {0} configuration file \"{1}\" not found, will use default options".format(client.name, client.conf))



	ns = Pyro4.locateNS(hmac_key=client.hmac_key_ns)
	for rem_server, rem_server_uri in ns.list(prefix="server.").items():
		print("client {0} joining {1}".format(client.name, rem_server))
		with Pyro4.Proxy(rem_server_uri) as server:
			server._pyroHmacKey = client.hmac_key
			server.join(client.name)
		
			print("client {0} requested server supported methods: {1}".format(client.name, server.list_methods()))
			print("client {0} requested server machinetype: {1}".format(client.name, server.get_machine_type()))
			print("client {0} requested server fan speed: {1}".format(client.name, server.get_fan_speed()))
			print("client {0} requested server temps: {1}".format(client.name, server.get_temps()))
		
			print("client {0} leaving {1}".format(client.name, rem_server))
			server.leave(client.name)
		
		
if __name__ == "__main__":
	main()
	
