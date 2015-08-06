'''
Created on Feb 27, 2015

@author: efviodo
'''

import json

##########################################################################
########## NODE
##########################################################################
class Node(object):
    '''
    Represents a Node 
    For top_type attribute we use the following convention
    0 -> CORE
    1 -> EDGE
    
    For status we use the following convention
    0 -> DOWN
    1 -> UP
    
    For net_type attribute we use the following convention
    0-> IP enabled node
    1-> OpenFlow enabled node
    
    For state attribute we use the following convention
    0 -> LS Ok
    1 -> OF and LS Ok
    '''
    
    def __init__(self,  router_id, status, of_ready=False, ls_ready=False, top_type=0, net_type=0, 
                 datapath_id=None, description=None, datapath=None, name=None,):
        '''
        Constructor
        '''
        
        self.name = name
        self.router_id = router_id
        self.description = description
        self.status = status
        self.top_type = top_type
        self.net_type = net_type
        self.datapath_id = datapath_id
        self.of_ready = of_ready
        self.ls_ready = ls_ready

        #OpenFlow
        self.datapath = datapath
               
        self.interfaces = {}
        self.nhlfe = []
        self.ilm = []
        self.ftn = []
    
    #Operations 
    def add_interface(self, iface):
        '''
        Add interface to the switch interfaces collection order by Mac-address.
        Params: iface-> Interface to add 
        '''
        
        self.interfaces[iface.ip_address] = iface
        
    def del_interface(self, ip_address):
        '''
        Delete interface to the switch interfaces collection.
        Params: mac_address-> Interface MAC address from the switch interface to remove 
        '''
                
        self.interfaces.pop(ip_address)
    
    def add_nhlfe_entry(self, nhlfe): 
        '''
        Add NHLFE entry to the switch nhlfe's collection.
        Params: nhlfe-> NHLFE entry 
        '''

        #Si la tabla NHLFE ya tiene una entrada identica simplemente incrementa la cantidad de referencias
        entry = self.get_nhlfe_entry(nhlfe)
        if entry is None:
            self.nhlfe.append(nhlfe)
        else:
            entry.references += 1
    
    def get_nhlfe_entry(self, nhlfe): 
        '''
        '''

        i = 0
        entry = None
        while i<len(self.nhlfe) and entry is None:
            if self.nhlfe[i] == nhlfe:
                entry = self.nhlfe[i]
            else:
                i += 1

        return entry
                       
    def decrement_nhlfe_entry_references(self, nhlfe):
        '''
        '''
        i = 0
        entry = None
        while i<len(self.nhlfe) and entry is None:
            if self.nhlfe[i] == nhlfe:
                entry = nhlfe
            else:
                i += 1

        if entry is not None:
            entry.references -= 1

        if entry.references <= 0:
            self.nhlfe.remove(entry)
        


   # def del_nhlfe_entry(self, nhlfe_id): 
   #     '''
   #     Remove NHLFE entry to the switch nhlfe's collection.
   #     Params: nhlfe_id-> NHLFE entry ID
   #     '''
   #     
   #     self.nhlfe.pop(nhlfe_id)
        
    def clear_nhlfe(self):
        '''
        Remove all NHLFE instances from the ftn's collection 
        Params:  
        '''
        
        self.nhlfe.clear()
           
    def add_ilm_entry(self, ilm): 
        '''
        Add ILM entry to the switch ilm's collection.
        Params: ilm-> ILM entry 
        '''
        
        self.ilm.append(ilm)
    
    def get_ilm_entry(self, ilm): 
        '''
        '''
        
        i = 0
        entry = None
        while i<len(self.ilm) and entry is None:
            if self.ilm[i] == ilm:
                entry = self.ilm[i]
            else:
                i += 1

        return entry 

    def remove_ilm_entry(self, ilm):
        '''
        '''

        i = 0
        entry = None
        while i<len(self.ilm) and entry is None:
            if self.ilm[i] == ilm:
                entry = self.ilm[i]
            else:
                i += 1

        if ilm is not None:
            self.ilm.remove(entry)
                       
    #def del_ilm_entry(self, ilm_id): 
    #    '''
    ###    Remove ILM entry to the switch ilm's collection.
    #    Params: ilm_id-> ILM entry ID
    #    '''
    #    
    #    self.nhlfe.pop(ilm_id) 
            
    def clear_ilm(self):
        '''
        Remove all ILM instances from the ftn's collection 
        Params:  
        '''
        
        self.ftn.clear()
        
    def add_ftn_entry(self, ftn): 
        '''
        Add FTN entry to the switch ftn's collection.
        Params: FTN-> FTN entry 
        '''
        
        self.ftn.append(ftn)
        
    
    def get_ftn_entry(self, ftn):
        '''
        '''

        i = 0
        entry = None
        while i<len(self.ftn) and entry is None:
            if self.ftn[i] == ftn:
                entry = self.ftn[i]
            else:
                i += 1

        return entry 

    def remove_ftn_entry(self, ftn):
        '''
        '''

        i = 0
        entry = None
        while i<len(self.ftn) and entry is None:
            if self.ftn[i] == ftn:
                entry = self.ftn[i]
            else:
                i += 1

        if ftn is not None:
            self.ftn.remove(entry)
         
                       

    #def del_ftn_entry(self, ftn_id): 
    #    '''
    #    Remove FTN entry to the switch ftn's collection.
    ##    Params: ftn_id-> FTN entry ID
    #   '''
        
    #    self.nhlfe.pop(ftn_id) 
                    
    def clear_ftn(self):
        '''
        Remove all FTN instances from the ftn's collection 
        Params:  
        '''
        
        self.ftn.clear()   

    def toJSON(self):
        '''
        Converts Node to JSON 
        '''

        dpid = self.datapath_id
        ports = []

        for i in self.interfaces.itervalues():

            mac_address = i.mac_address
            name = i.name
            port = i.ovs_port

            ports.append({
                            'hw_addr': mac_address, 
                            'name': name, 
                            'port_no': port, 
                            'dpid': dpid
                        })
               
            
        node = {'ports': ports, 'dpid': dpid}

        return json.dumps(node, indent=2)

    def toDict(self):
        '''
        Converts Node to Dict 
        '''

        dpid = self.datapath_id
        ports = []

        for i in self.interfaces.itervalues():

            mac_address = i.mac_address
            name = i.name
            port = i.ovs_port

            ports.append({
                            'hw_addr': mac_address, 
                            'name': 'name', 
                            'port_no': port, 
                            'dpid': str(dpid)
                        })
               
            
        node = {'ports': ports, 'dpid': str(dpid)}

        return node

##########################################################################
########## INTERFACE
##########################################################################
class Interface(object):
    '''
    Represent Node interface
    
    For net_type attribute we use the following convention
    0-> IP enabled node
    1-> OpenFlow enabled node

    For type we use the following convention
    0 -> internal interface: forward traffic inside the network core
    1 -> external interface: forward traffic outiside the network core
    '''


    def __init__(self, node=None, ovs_port=None, ip_address=None, mac_address=None, 
                    status=1, name=None, i_type=0, mpls_labels=None, ce_mac_address=None, ce_ip_address=None):
        '''
        Constructor
        '''
        
        self.node =  node
        self.name = name
        self.ovs_port = ovs_port
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.status = status
        self.type = i_type
        self.links = {}

        # If Interface Type == 1 then we have customer edge information
        self.ce_mac_address = ce_mac_address
        self.ce_ip_address = ce_ip_address

        if mpls_labels is None:
            self.mpls_labels = []
        else:
            self.mpls_labels = mpls_labels

    def __eq__(self, other):
        if isinstance(other, NHLFE):
            c = self.ip_address == other.ip_address and self.mac_address == other.mac_address and self.ovs_port == other.ovs_port 
            c = c and self.ce_ip_address == other.ce_ip_address and self.ce_mac_address == other.ce_mac_address

            return c
        else:
            return NotImplemented

##########################################################################
########## LINK
##########################################################################
class Link(object):
    '''
    Represent a link between two Nodes
    For represent status attribute we use the following convention
    0 -> DOWN
    1 -> UP

    mpls_label represents the asignated MPLS label to reach ip interace target
    on to_node_int 
    '''


    def __init__(self, status, from_node_int, to_node_int, mpls_label=None, weight=0):
        '''
        Constructor
        '''
        
        self.status = status
        self.from_node_int = from_node_int
        self.to_node_int = to_node_int
        self.mpls_label = mpls_label

        #Dikjstra
        self.weight = weight

    def toJSON(self):
        '''
        Converts LINK to JSON 
        '''

        src_mac_address = self.from_node_int.mac_address
        src_name = self.from_node_int.name
        src_port = self.from_node_int.ovs_port
        src_dpid = self.from_node_int.node.datapath_id
        src = {
                'hw_addr': src_mac_address, 
                'name': src_name, 
                'port_no': src_port, 
                'dpid': str(src_dpid)
            }

        dst_mac_address = self.to_node_int.mac_address
        dst_name = self.to_node_int.name
        dst_port = self.to_node_int.ovs_port
        dst_dpid = self.to_node_int.node.datapath_id
        dst = {
                'hw_addr': dst_mac_address, 
                'name': dst_name, 
                'port_no': dst_port, 
                'dpid': str(dst_dpid)
            }

        link = {'src': src, 'dst': dst}

        return json.dumps(link, indent=2)

    def toDict(self):
        '''
        Converts LINK to JSON 
        '''

        src_mac_address = self.from_node_int.mac_address
        src_name = self.from_node_int.name
        src_port = self.from_node_int.ovs_port
        src_dpid = self.from_node_int.node.datapath_id
        src = {
                'hw_addr': src_mac_address, 
                'name': 'src_name', 
                'port_no': src_port, 
                'dpid': str(src_dpid)
            }

        dst_mac_address = self.to_node_int.mac_address
        dst_name = self.to_node_int.name
        dst_port = self.to_node_int.ovs_port
        dst_dpid = self.to_node_int.node.datapath_id
        dst = {
                'hw_addr': dst_mac_address, 
                'name': 'dst_name', 
                'port_no': dst_port, 
                'dpid': str(dst_dpid)
            }

        link = {'src': src, 'dst': dst}

        return link

##########################################################################
########## FTN
##########################################################################
class FTN(object):
    '''
    classdocs
    '''


    def __init__(self, service, nhlfes):
        '''
        Constructor
        '''
        
        self.service = service
        self.nhlfes  = nhlfes
        
    def __eq__(self, other):
        if isinstance(other, FTN):
            return self.service == other.service
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

class ILM(object):
    '''
    classdocs
    '''

    
    def __init__(self, label, nhlfes, ilm_type=0, service=None):
        '''
        Constructor

        Type:
        0 --> ILM for internal node
        1 --> ILM for border node
        '''
        
        self.label = label
        self.nhlfes = nhlfes
        self.type = ilm_type
        self.service = service #If type = 1 then ILM have reference to service

    def __eq__(self, other):
        if isinstance(other, ILM):
            return self.label == other.label and self.type == other.type
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def add_nhlfe_entry(self, nhlfe):
        
        #Looks if nhlfe is already on ilm collection

        i = 0
        entry = None
        while i<len(self.nhlfes) and entry is None:
            if self.nhlfes[i] == nhlfe:
                entry = self.nhlfes[i]
            else:
                i += 1

        if entry is None:
            self.nhlfes.append(nhlfe)
        else:
            entry.references += 1

    
##########################################################################
########## NHLFE
##########################################################################
class NHLFE(object):
    '''
    classdocs
    '''


    def __init__(self, interface, next_hop, action, label_level=2):
        '''
        Constructor
        '''
        
        self.interface = interface          #Interface packet in
        self.next_hop = next_hop            #We need interface_out and next hop node to know NEXT HOP since net is multigraph   
        self.action = action

        self.references = 1
        #Extra para saber si la entrada se corresponde a una etiqueta de Nivel 1 o 2 -> 1 = Inner label , 2=Outer label 
        self.label_level = label_level

        
    def __eq__(self, other):
        if isinstance(other, NHLFE):
            return self.interface == other.interface and self.next_hop == other.next_hop and self.action == other.action and self.label_level == other.label_level
        else:
            return NotImplemented
        
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
