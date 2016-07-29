# server.py
## this is the code that runs on the nodes and provides methods for clients to get sensor
## data and execute commands
 
from __future__ import print_function
import Pyro4
import socket

class NodeServer(object):
	def __init__(self):
		self.name = socket.gethostname()
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
        Pyro4.config.HOST = "192.168.0.100"
	with Pyro4.Daemon() as daemon:
		server_uri = daemon.register(server)
		with Pyro4.locateNS() as ns:
			ns.register("server.hostname1", server_uri)
		print("Server {0} is running.".format(server.name))
		daemon.requestLoop()

if __name__ == "__main__":
   main()

