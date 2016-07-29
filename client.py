# client.py
## this is the code that runs on Rpi and connects to servers found in nameserver lookup

from __future__ import print_function
import Pyro4

class Client(object):
	def __init__(self):
		self.name = "Rpi"

		
def main():
	client = Client()
	ns = Pyro4.locateNS()
	for rem_server, rem_server_uri in ns.list(prefix="server.").items():
		print("client {0} joining server {1}".format(client.name, rem_server))
		server = Pyro4.Proxy(rem_server_uri)
		server.join(client.name)
		
		print("client {0} requested server supported methods: {1}".format(client.name, server.list_methods()))
		print("client {0} requested server machinetype: {1}".format(client.name, server.get_machine_type()))
		print("client {0} requested server fan speed: {1}".format(client.name, server.get_fan_speed()))
		print("client {0} requested server temps: {1}".format(client.name, server.get_temps()))
		
		print("client {0} leaving server {1}".format(client.name, rem_server))
		server.leave(client.name)
		
		
if __name__ == "__main__":
	main()
	
