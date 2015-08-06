'''
Created on April 08 , 2015

@author: efviodo
'''

from patterns import Singleton
from dataTypes import DTNode, DTInterface, DTLink
import requests
import json


HOST = '192.168.1.12'
PORT = '5000'
URI_APP_SNMP = 'http://' + HOST + ':' + PORT + '/snmp/atp/' 

class ManagementApp(Singleton, object):
	'''
	classdocs
	'''

	topology = {}

	def __init__(self, debug_mode=False, topology=None):
		'''
		Constructor:

		Debug_mode indicates if the management app run on debug mode or not.
		On debug mode, management app get extra node and interface information from local
		stub witch recives as a parametter
		'''

		print 'Initialize management app'
        
		self.debug_mode = debug_mode

		if topology is not None:
			self.topology = topology

	def set_topology_stub(self, topology):
		self.topology = topology
    

	def _get_stub_node_full_data(self, node):
		'''
		doc
		'''

		n = self.topology[node.router_id]
		result = DTNode(router_id=node.router_id, datapath_id=n.datapath_id, status=node.status, net_type=n.net_type, 
						top_type=n.top_type)
        
		interfaces = {}
		for i in node.interfaces.itervalues():
			inter = self.topology[node.router_id].interfaces[i.ip_address]
            
			#Actually Links has not many information than lsdb information
			links = {}
            
			for l in i.links.itervalues():
				print l.to_node_int
				link = DTLink(status=l.status, from_node_int=l.from_node_int, to_node_int=l.to_node_int, weight=l.weight)
				links[link.to_node_int.ip_address] = link

			
			res = DTInterface(ip_address=i.ip_address, mac_address=inter.mac_address, ovs_port=inter.ovs_port, links=links, 
									i_type=inter.type)
			interfaces[i.ip_address] = res
            
		result.interfaces = interfaces

		return result


	def _get_ws_node_full_data(self, node):
		'''
		Connect via web service to SNMP agent app to get 
		specific node extra data
		'''

		url = URI_APP_SNMP + node.router_id
		result = None

		try:
			json_data = requests.get(url)
			data = json.loads(json_data.json())

			if data is not None:
				datapath_id = str(int(data["dpid"], 16))
				ports = data['puertos']
				port = None
				ip_address = None
				mac_address =  None
				ovs_port = None
				result = DTNode(router_id=node.router_id, datapath_id=datapath_id, status=1, net_type=0, 
								top_type=0)
	            
				interfaces = {}
				for port in ports:
	            
					ip_address = port['ip']
					mac_address = port['mac']
					ovs_port = port['numeroOVS']
					name = port['nombreInterfaz']

					if(node.interfaces.has_key(ip_address)):
						inter = node.interfaces[ip_address]
		                
						#Actually Links has not many information than lsdb information
						links = {}

						for l in inter.links.itervalues():
							
							link = DTLink(status=l.status, from_node_int=l.from_node_int, to_node_int=l.to_node_int, weight=l.weight)
							links[link.to_node_int.ip_address] = link

						res = DTInterface(ip_address=ip_address, mac_address=mac_address, ovs_port=ovs_port, links=links, 
											i_type=0, name=name, status=1)
				
						interfaces[ip_address] = res
					
					else:
						# La interfaz no existe en la LSDB puede ser una interfaz externa asi que la agrega como interfaz down

						# La crea solamente si tiene direccion IP, puerto ovs y direccion mac
						if ip_address != None and mac_address != None and ovs_port != None:
							links = {}
						
							res = DTInterface(ip_address=ip_address, mac_address=mac_address, ovs_port=ovs_port, links=links, 
											i_type=0, name=name, status=0)
							interfaces[ip_address] = res
	                
				result.interfaces = interfaces

		except ValueError:
			print "ERROR" + str(ValueError)

		except requests.exceptions.ConnectionError:
			print "Connection error: Could not connect to snmp agent"  

		return result

	def _get_stub_node_interface_full_data(self, router_id, iface):
		'''
		docs
		'''

		inter = self.topology[router_id].interfaces[iface.ip_address]
		result = DTInterface(ip_address=iface.ip_address, mac_address=inter.mac_address, ovs_port=inter.ovs_port, i_type=inter.type)

		return result

	def _get_ws_node_interface_full_data(self, node, iface):
		'''
		docs
		'''

		result = None
		node_data = self._get_ws_node_full_data(node)

		if node_data is None:
			return None
		else:

			if(node_data.interfaces.has_key(iface.ip_address)):

				interface = node_data.interfaces[iface.ip_address]
			
				ip_address = interface.ip_address
				mac_address = interface.mac_address
				ovs_port = interface.ovs_port
				name = interface.name
				result = None

				#Actually Links has not many information than lsdb information
				links = {}
		        
				for l in iface.links.itervalues():
					print l.to_node_int
					link = DTLink(status=l.status, from_node_int=l.from_node_int, to_node_int=l.to_node_int, weight=l.weight)
					links[link.to_node_int.ip_address] = link

				result = DTInterface(ip_address=ip_address, mac_address=mac_address, ovs_port=ovs_port, links=links, 
										i_type=0, name=name)
			
                   
			return result


	def get_node_full_data(self, node):
       
		if self.debug_mode:
			print 'Management App running on Debug Mode' 
			return self._get_stub_node_full_data(node)
		else:
			print 'Management App running on Normal Mode' 
			return self._get_ws_node_full_data(node)

	def get_node_interface_full_data(self, node, router_id, iface):
        
		if self.debug_mode:
			print 'Management App running on Debug Mode' 
			return self._get_stub_node_interface_full_data(router_id, iface)
		else:
			print 'Management App running on Normal Mode' 
			return self._get_ws_node_interface_full_data(node, iface)
