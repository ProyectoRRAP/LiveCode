'''
Created on Feb 27, 2015

@author: efviodo
'''
import json



##########################################################################
########## DTNODE
##########################################################################
class DTNode(object):
    '''
    classdocs
    '''


    def __init__(self, router_id, datapath_id, interfaces, status=None, net_type=None, 
                 top_type=None, description=None):
        '''
        Constructor
        '''
        
        self.router_id = router_id
        self.datapath_id = datapath_id
        self.status = status
        self.net_type = net_type
        self.top_type = top_type
        self.description = description
        self.interfaces = interfaces
        
##########################################################################
########## DTINTERFACE
##########################################################################
class DTInterface(object):
    '''
    classdocs
    '''


    def __init__(self, ip_address, link=None, mac_address=None, ovs_port=None):
        '''
        Constructor
        '''
        
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.ovs_port = ovs_port
        self.link = link
        
##########################################################################
########## DTLINK
##########################################################################   
class DTLink(object):
    '''
    classdocs
    '''


    def __init__(self, from_node, to_node, status):
        '''
        Constructor
        '''
        
        self.from_node = from_node
        self.to_node = to_node
        status = status

##########################################################################
########## DTLSNODE
##########################################################################          
class DTLSNode(object):
    '''
    classdocs
    '''


    def __init__(self, router_id, status=1, interfaces=None, freeInterfaces = 0):
        '''
        Constructor
        '''
        
        
        self.router_id = router_id
        self.status = status
	self.freeInterfaces = freeInterfaces
        
        if interfaces is None:
            self.interfaces = {}
        else:
            self.interfaces = interfaces

    

    def to_JSON(self):
        #print 'Convierte a JSON'
        #Convierte a JSON cada interfaz
        interfaces_json = []
        for i in self.interfaces:
            links_json = []
            for l in i.links.itervalues():
		
		if l.to_node_int :
		        links_json.append({'from_node_int': l.from_node_int.ip_address, 'to_node_router_id':l.to_node_int.node.router_id,
		                            'to_node_int': l.to_node_int.ip_address, 'weight': l.weight})

            interfaces_json.append({'ip_address':i.ip_address, 'links': links_json})

        return json.dumps({'router_id': self.router_id,'freeInterfaces':self.freeInterfaces , 'interfaces': interfaces_json}, indent=2)     
        


       

            
##########################################################################
########## DTLSINTERFACE
##########################################################################      
class DTLSInterface(object):
    '''
    classdocs
    '''


    def __init__(self, node, ip_address, status=1, links=None):
        '''
        Constructor
        '''
        
        self.node = node
        self.ip_address = ip_address
        self.status = status
        if links is None:
            self.links = {}
        else:
            self.links = links
        
    def __eq__(self, other):
        if isinstance(other, DTLSInterface):
            return self.ip_address == other.ip_address 
        else:
            return NotImplemented
        
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
    def append_link(self, link):
        
        self.links[link.quagga_identifier] = link

    


    
       
##########################################################################
########## DTLSINK
##########################################################################   
class DTLSLink(object):
    '''
    classdocs
    '''


    def __init__(self, id, from_node_int, to_node_int=None,to_node_router_id =None, status=1,weight = None):
        '''
        Constructor
        '''
        self.quagga_identifier = id
        self.from_node_int = from_node_int
        self.to_node_int = to_node_int
	self.to_node_router_id = to_node_router_id
        self.weight = weight
        self.status = status
        
    def __eq__(self, other):
        if isinstance(other, DTLSLink):
            return self.from_node == other.from_node and self.to_node == other.to_node
        else:
            return NotImplemented
        
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result 

