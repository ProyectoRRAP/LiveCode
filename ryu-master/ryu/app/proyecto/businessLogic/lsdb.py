'''
Created on Feb 25, 2015

@author: efviodo
'''

from ryu.base import app_manager

#from controllers import TopologyController
from dataTypes import DTLSNode, DTLSInterface, DTLSLink


class LSDBSyncronizer(object):
    '''
    classdocs
    '''

    ndoes = {}

    def __init__(self):
        '''
        Constructor
        '''
        print 'Initialize LSDB Syncronizer'
        
	   #super(LSDBSyncronizer, self).__init__(*args, **kwargs)

        
        #Crea los nodos
        gimly = DTLSNode(status=1, router_id='192.168.1.10')
        nodes[gimly.router_id]=gimly
        galois = DTLSNode(status=1, router_id='192.168.1.11')
        nodes[galois.router_id]=galois
        oz = DTLSNode(status=1, router_id='192.168.1.12')
        nodes[oz.router_id]=oz
        poisson = DTLSNode(status=1, router_id='192.168.1.13')
        nodes[poisson.router_id]=poisson
        alice = DTLSNode(status=1, router_id='192.168.1.14')
        nodes[alice.router_id]=alice
        
        #Agrega Interfaces
        interfaces = {}
        i = DTLSInterface(node=gimly, status=1, ip_address='192.168.1.10')
        interfaces[i.ip_address] = i
        nodes['192.168.1.10'].interfaces[i.ip_address] = i
        
        interfaces = {}
        i = DTLSInterface(node=galois, status=1, ip_address='192.168.1.11')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=galois, status=1, ip_address='10.10.1.1')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=galois, status=1, ip_address='10.10.4.1')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=galois, status=1, ip_address='10.10.5.1')
        interfaces[i.ip_address] = i
        nodes['192.168.1.11'].interfaces = interfaces
        
        interfaces = {}
        i = DTLSInterface(node=oz, status=1, ip_address='192.168.1.12')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=oz, status=1, ip_address='10.10.1.2')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=oz, status=1, ip_address='10.10.3.1')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=oz, status=1, ip_address='10.10.6.2')
        interfaces[i.ip_address] = i
        nodes['192.168.1.12'].interfaces = interfaces
        
        interfaces = {}
        i = DTLSInterface(node=poisson, status=1, ip_address='192.168.1.13')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=poisson, status=1, ip_address='10.10.2.1')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=poisson, status=1, ip_address='10.10.6.1')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=poisson, status=1, ip_address='10.10.4.2')
        interfaces[i.ip_address] = i
        nodes['192.168.1.13'].interfaces = interfaces
        
        interfaces = {}
        i = DTLSInterface(node=alice, status=1, ip_address='192.168.1.14')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=alice, status=1, ip_address='10.10.2.2')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=alice, status=1, ip_address='10.10.3.2')
        interfaces[i.ip_address] = i
        i = DTLSInterface(node=alice, status=1, ip_address='10.10.5.2')
        interfaces[i.ip_address] = i
        nodes['192.168.1.14'].interfaces = interfaces
        
        #Set 192.168.1.x links
        gimly = nodes['192.168.1.10']
        galois = nodes['192.168.1.11']
        oz = nodes['192.168.1.12']
        poisson = nodes['192.168.1.13']
        alice = nodes['192.168.1.14']
        
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.11'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'], 
                                                                                            to_node_int=galois.interfaces['192.168.1.11'])        
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.12'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'], 
                                                                                            to_node_int=oz.interfaces['192.168.1.12'])
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.13'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'], 
                                                                                            to_node_int=poisson.interfaces['192.168.1.13'])
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.14'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'],
                                                                                            to_node_int=alice.interfaces['192.168.1.14'])
        
        nodes['192.168.1.11'].interfaces['192.168.1.11'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=galois.interfaces['192.168.1.11'], 
                                                                                            to_node_int=gimly.interfaces['192.168.10'])        
        nodes['192.168.1.11'].interfaces['10.10.1.1'].links['10.10.1.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.1.1'], 
                                                                                    to_node_int=oz.interfaces['10.10.1.2'])
        nodes['192.168.1.11'].interfaces['10.10.4.1'].links['10.10.4.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.4.1'], 
                                                                                    to_node_int=poisson.interfaces['10.10.4.2'])
        nodes['192.168.1.11'].interfaces['10.10.5.1'].links['10.10.5.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.5.1'],
                                                                                     to_node_int=alice.interfaces['10.10.5.2'])
        
        nodes['192.168.1.12'].interfaces['192.168.1.12'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=oz.interfaces['192.168.1.12'],
                                                                                             to_node_int=gimly.interfaces['192.168.1.10'])        
        nodes['192.168.1.12'].interfaces['10.10.1.2'].links['10.10.1.1'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.1.2'],
                                                                                     to_node_int=galois.interfaces['10.10.1.1'])
        nodes['192.168.1.12'].interfaces['10.10.6.2'].links['10.10.6.1'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.6.2'],
                                                                                     to_node_int=poisson.interfaces['10.10.6.1'])
        nodes['192.168.1.12'].interfaces['10.10.3.1'].links['10.10.3.2'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.3.1'],
                                                                                     to_node_int=alice.interfaces['10.10.3.2'])
        
        nodes['192.168.1.13'].interfaces['192.168.1.13'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=poisson.interfaces['192.168.1.13'],
                                                                                         	to_node_int=gimly.interfaces['192.168.1.10'])        
        nodes['192.168.1.13'].interfaces['10.10.2.1'].links['10.10.2.2'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.2.1'],
                                                                                     to_node_int=alice.interfaces['10.10.2.2'])
        nodes['192.168.1.13'].interfaces['10.10.6.1'].links['10.10.6.2'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.6.1'],
                                                                                     to_node_int=oz.interfaces['10.10.6.2'])
        nodes['192.168.1.13'].interfaces['10.10.4.2'].links['10.10.4.1'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.4.2'], 
                                                                                     to_node_int=galois.interfaces['10.10.4.1'])
        
        nodes['192.168.1.14'].interfaces['192.168.1.14'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=alice.interfaces['192.168.1.14'], 
                                                                                            to_node_int=gimly.interfaces['192.168.1.10'])        
        nodes['192.168.1.14'].interfaces['10.10.2.2'].links['10.10.2.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.2.2'],
                                                                                     to_node_int=poisson.interfaces['10.10.2.1'])
        nodes['192.168.1.14'].interfaces['10.10.5.2'].links['10.10.5.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.5.2'],
                                                                                     to_node_int=galois.interfaces['10.10.5.1'])
        nodes['192.168.1.14'].interfaces['10.10.3.2'].links['10.10.3.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.3.2'],
                                                                                     to_node_int=oz.interfaces['10.10.3.1'])
        
        #self.update_ls_topology(nodes)
	self.nodes = nodes
	#Eliminar en algun momento

    
    def update_ls_topology(self):      
	#self.topoc.update_ls_topology(nodes)
        return self.nodes
