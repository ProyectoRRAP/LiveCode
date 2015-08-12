'''
Created on Feb 25, 2015

@author: efviodo
'''
#Ryu OF imports
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto.ofproto_v1_2 import OFPG_ANY
from ryu.lib.packet import mpls
#Model imports
from util import increment_hex_value, shortestPathMultiGraph
from management_agents import ManagementApp
from topology import Node, Interface, Link, FTN, NHLFE, ILM
from dataTypes import DTNode, DTInterface, DTLink, DTLSNode, DTLSInterface, DTLSLink, DTService
from dataTypes import DTLSP, DTMPLSAction, DTNHLFE, DTFTN, DTILM, DTServiceLSP, DTLSPLink
from patterns import Singleton
from mpls import Service, PathNode, LSP
import datapath
import settings

import copy

#######################################################################################
################# TOPOLOGY CONTROLLER #################################################
##### 
##### Description: All functionalities asociated with 
##### topology abstraction
#######################################################################################
class TopologyController(Singleton, object):
    '''
    classdocs
    '''

    #Attributes are initialized outside __init__ method to prevent overwrite
    nodes = {}
    datapath_nodes_cache = {} #Nodos que se registraron por el canal seguro OF pero que aun no existen en la topo

    #Constants

    ####################### MPLS/LDP ##########
    MPLS_LABEL_SPACE_MIN = '0x0001e'
    MPLS_LABEL_SPACE_MAX = '0xfffff'

    mpls_label_sec = MPLS_LABEL_SPACE_MIN;

    servs = {}

    lsps = []
    ###########################################

    def __init__(self, mngapp):
        '''
        Constructor
        '''

        self.mng_app = mngapp
	
    #######################################################
    ####### TOPOLOGY primitives
    ####################################################### 
    def get_topology_node(self, router_id):

        print 'Search for node with router_id: ' + router_id + '/'

        node = None
        
        #Check if topology has node with router_id=param
        if self.nodes.has_key(router_id):
            
            n = self.nodes[router_id]
            
            interfaces = {}
            for i in n.interfaces.itervalues():
                links = {}
                for l in i.links.itervalues():
                    link = DTLink(from_node_int=l.from_node_int, to_node_int=l.to_node_int, status=l.status, 
                                    mpls_label=l.mpls_label, weight=l.weight)
                    links[link.to_node_int.ip_address] = link

                interface = DTInterface(ip_address=i.ip_address, links=links, mac_address=i.mac_address,
                                        ovs_port=i.ovs_port, i_type=i.type, status=i.status, name=i.name, 
                                        ce_mac_address=i.ce_mac_address, ce_ip_address=i.ce_ip_address)
                interfaces[interface.ip_address] = interface

            node = DTNode(router_id=n.router_id, datapath_id=n.datapath_id, status=n.status, interfaces=interfaces, 
                            net_type=n.net_type, top_type=n.top_type, of_ready=n.of_ready, ls_ready=n.ls_ready, name=n.name)
        else:
            print 'Node not found'

        return node

    def get_topology(self):

        print 'Returns all nodes'
        
        nodes = []
        for n in self.nodes.itervalues():
            interfaces = {}
            for i in n.interfaces.itervalues():
                links = {}
                for l in i.links.itervalues():
                    link = DTLink(from_node_int=l.from_node_int, to_node_int=l.to_node_int, status=l.status, 
                        mpls_label=l.mpls_label, weight=l.weight)
                    links[link.to_node_int.ip_address] = link

                interface = DTInterface(ip_address=i.ip_address, links=links, mac_address=i.mac_address,
                                        ovs_port=i.ovs_port, i_type=i.type, status=i.status, name=i.name, 
                                        ce_mac_address=i.ce_mac_address, ce_ip_address=i.ce_ip_address)
                interfaces[interface.ip_address] = interface

            node = DTNode(name=n.name, router_id=n.router_id, datapath_id=n.datapath_id, status=n.status, interfaces=interfaces, 
                        net_type=n.net_type, top_type=n.top_type, of_ready=n.of_ready, ls_ready=n.ls_ready)
            nodes.append(node)    
        
        return nodes

    def get_ls_topology(self):
        '''
        Returns a list with nodes in memory representation of topology. 
        Only link state information of nodes, interfaces and links  
        '''
        nodes = {}
        
        for n in self.nodes:
            interfaces = {}
            for i in n.interfaces:
                link = i.link
                l = DTLink(from_node_int=link.from_node, to_node_int=link.to_node, status=link.status, weight=l.weight)
                i = DTInterface(ip_address=i.ip_address, link=l, status=i.status)
                interfaces[i.ip_address] = i
            node = DTLSNode(router_id=n.router_id, status=n.status, interfaces=interfaces)
            nodes[node.router_id] = node
       
        return nodes

    def update_ls_topology(self, nodes):
        '''
        Doc
        '''
        
        #Inner class only for this functionality
        class DTNewLink:
            def __init__(self, router_id, ip_address, link):
                self.router_id = router_id
                self.ip_address = ip_address
                self.link = link

        #Compare each node in topology with each node in lspdb topology seeking for updates and nws 
        #nodes, interfaces and links
        
        #Update Nodes lookin lsdb nodes
        
        print 'Update nodes on topology, new topology: ' + str(len(nodes)) + ' nodes'

        topology = self.nodes

        new_links = []

        #We agregate as a result three lists, nodes disabled and links disabled
        nodes_disabled = []
        links_disabled = []

        #First we update nodes and interfaces to avoid links modifications to non-existing interfaces
        nodes_chk = []
        for n in nodes.itervalues():

            if topology.has_key(n.router_id):
                #Node exists in topology
                node = topology[n.router_id]
                
                print 'Updates node router_id: ' + n.router_id

                #Check interfaces
                interfaces_chk = []
                for i in n.interfaces.itervalues():

                    # If inteface has not ip address then ignore it
                    if i.ip_address != None:
                        if node.interfaces.has_key(i.ip_address):

                            print 'Updates interface ip_address: ' + i.ip_address

                            interface = node.interfaces[i.ip_address]
                            
                            links_chk = []
                            for l in i.links.itervalues():
                               
                                if interface.links.has_key(l.to_node_int.ip_address):
                                    self.update_topology_ls_node_interface_link(router_id=n.router_id, 
                                        ip_address=i.ip_address, ip_address_dest=l.to_node_int.ip_address, link=l)
                                    print 'Updates link ip_address: ' + l.to_node_int.ip_address
                                else:
                                    new_links.append(DTNewLink(n.router_id, i.ip_address, l))
                                
                                links_chk.append(l.to_node_int.ip_address)
                            
                            #Update Interface information    
                            self.update_topology_ls_node_interface(router_id=n.router_id, ip_address=i.ip_address, interface=i)
                            
                            #Update all links in topology there are not in lsdb
                            for l2 in interface.links.itervalues():
                                if l2.to_node_int.ip_address not in links_chk:
                                    self.disable_topology_node_interface_link(node.router_id, 
                                                                              interface.ip_address, l2.to_node_int.ip_address)
                                    links_disabled.append(l2.toDict())
                                
                            interfaces_chk.append(i.ip_address)
                        else:
                            #Interface does not exist in topology we add the interface
                            self.add_topology_ls_interface(n, n.router_id, i)
                            
                            #We save interface links for later creation
                            for l in i.links.itervalues():
                                new_links.append(DTNewLink(router_id=n.router_id, ip_address=i.ip_address, link=l))
                              
                            interfaces_chk.append(i.ip_address)      
                            print 'Creates interface ip_address: ' + i.ip_address

                #Update Node information
                self.update_topology_ls_node(n.router_id, n)
                
                #Update all interfaces in toplogy there are not in lsdb
                for i in node.interfaces.itervalues():
                    if i.ip_address not in interfaces_chk and i.type != 1:
                        self.disable_topology_node_interface(n.router_id, i.ip_address)

                        #Add each interface link to disabled links list
                        for l in i.links.itervalues():
                                links_disabled.append(l.toDict())
                
                nodes_chk.append(n.router_id)

            else:
                #Node does not exist in topology, thereforce we add the node
                self.add_topology_ls_node(n)
                
                #We save all interfaces links for later creation
                for i in n.interfaces.itervalues():    
                    for l in i.links.itervalues():
                      new_links.append(DTNewLink(router_id=n.router_id, ip_address=i.ip_address, link=l))

                nodes_chk.append(n.router_id)
                print 'Creates node router_id: ' + n.router_id

        #Update all nodes in toplogy there are not in lsdb
        for n in topology.itervalues():
            if n.router_id not in nodes_chk:
                self.disable_topology_node(n.router_id)
                nodes_disabled.append(n.toDict())
    
        #Second we create new links
        for link in new_links:
            self.add_topology_ls_interface_link(link.router_id, link.ip_address, link.link)

        return nodes_disabled, links_disabled
        
    def update_topology_ls_node(self, router_id, node):
        
        print 'Update LS Node'
        #Get old Node
        node_old = self.nodes.pop(router_id)
        
        #Update Node values
        node_old.router_id = node.router_id
        node_old.status = 1

        # updates all external interfaces
        data = self.mng_app.get_node_full_data(node)        
        for i in node_old.interfaces.itervalues():

            if i.type == 1:

                if data.interfaces.has_key(i.ip_address):
                    iface = data.interfaces[i.ip_address]
                    i.status = 1
                else:
                    i.status = 0 
        
        #Put updated node
        self.nodes[node_old.router_id] = node_old
        
    def update_topology_ls_node_interface(self, router_id, ip_address, interface): 

        print 'Update LS Interface' 
        #Get old Interface
        node_interface_old = self.nodes[router_id].interfaces.pop(ip_address)
        
        #Update interface values
        node_interface_old.ip_address = interface.ip_address
        node_interface_old.status = 1
        
        #Put updated interface
        self.nodes[router_id].interfaces[node_interface_old.ip_address] = node_interface_old
            
    def update_topology_ls_node_interface_link(self, router_id, ip_address, ip_address_dest, link):

        print 'Update LS Link'
        #Get old Link
        node_interface_link_old = self.nodes[router_id].interfaces[ip_address].links.pop(ip_address_dest)
        
        #Update interface values
        node_interface_link_old.weight = link.weight

        #Enables by default link
        node_interface_link_old.status = 1
        
        #Put updated interface
        self.nodes[router_id].interfaces[ip_address].links[ip_address_dest] = node_interface_link_old    
        
    def disable_topology_node(self, router_id):
        print 'Disable Node: ' + str(router_id) 
        
        n = self.nodes[router_id]
        n.status = 0
        for i in n.interfaces.itervalues():
            i.status = 0
            for l in i.links.itervalues():
                l.status = 0

                #Disable oposite link
                iface = l.to_node_int
                if iface.links.has_key(l.from_node_int.ip_address):
                    link = iface.links[l.from_node_int.ip_address]
                    link.status = 0
        
          
    def disable_topology_node_interface(self, router_id, ip_address):
        print 'Disable Interface: ' + str(router_id) + '-' + str(ip_address) 

        i = self.nodes[router_id].interfaces[ip_address]
        i.status = 0
        for l in i.links.itervalues():
            #Disable link
            l.status = 0

            #Disable oposite link
            iface = l.to_node_int
            if iface.links.has_key(l.from_node_int.ip_address):
                link = iface.links[l.from_node_int.ip_address]
                link.status = 0
        
    def disable_topology_node_interface_link(self, router_id, ip_address, ip_address_dest):
        print 'Disable Link: ' + str(router_id) + '-' + str(ip_address) + '-' + str(ip_address_dest)

        self.nodes[router_id].interfaces[ip_address].links[ip_address_dest].status = 0
    
    def get_of_node_by_datapath_id(self, datapath_id):

        i = 0
        node = None
        find = False
        values = self.nodes.values()
        while i < len(values) and not find:
            if values[i].datapath_id == datapath_id:
                node = values[i]
                find = True
            else:
                i = i + 1

        return node


    def get_best_path(self, node_src, node_dst):
        '''
        Calcula el mejor camino entre dos nodos en la topologia 
        el resultado es una lista ordenada de links
        '''

        result = []

        G = {}

        #First built Multi graph with links weight for spf alghoritm 
        for n1 in self.nodes.itervalues():

            if n1.ls_ready and n1.of_ready:

                U = {}
                for n2 in self.nodes.itervalues():
                   
                    if n2.ls_ready and n2.of_ready:

                        neighbors = False
                        V = {}
                        for i in n1.interfaces.itervalues():

                            if i.status == 1:

                                #From one specific interface to other only exists one link
                                for l in i.links.itervalues():

                                    if (l.status == 1) and (l.to_node_int.node.router_id == n2.router_id):
                                        V[i] = l.weight
                                        neighbors = True
                            
                        #If exists at least one link between n1 and n2 by one specific n1 interface then n1 and n2
                        #are adjacents    
                        if neighbors:
                            U[n2] = V

                G[n1] = U 

        #Then call spf alghoritm
        path = shortestPathMultiGraph(G, node_src, node_dst)

        result = path

        return result


    def get_topology_nodes_datapaths(self):
        '''
        '''

        datapath_ids = {}
        for n in self.nodes.itervalues():
            datapath_ids[n.router_id] = n.datapath_id

        return datapath_ids

    def get_topology_nodes_interfaces_by_datapath_id(self, datapath_id):
        '''
        '''

        interfaces = []
        node = self.get_of_node_by_datapath_id(datapath_id)
        for i in node.interfaces.itervalues():
            interfaces.append(i.ip_address)

        return interfaces

    #######################################################
    ####### NODES primitives
    #######################################################        
    def add_topology_ls_node(self, node):
        '''
        Add new node to topology with router_id and network type according to
        parameters recived
        '''
        
        # We use ManagementApp to geth Full topology information about the Node
        #mapp = ManagementApp()

        data = self.mng_app.get_node_full_data(node)
        
        if data is not None:
            #By default we create Node on UP state
            status = 1
            
            #Create the Node
            n = Node(router_id=data.router_id, status=1, top_type=data.top_type, net_type=data.net_type,
    			  datapath_id=data.datapath_id, of_ready=False, ls_ready=True)

            #Look datapath cache in case node was register via OF chanell
            if self.datapath_nodes_cache.has_key(data.datapath_id):
                n.of_ready = True
                n.net_type = 1
                n.datapath = self.datapath_nodes_cache.pop(data.datapath_id)
                print 'Enables OF Node on Node Add'

            for i in data.interfaces.itervalues():
                iface = Interface(node=n, ovs_port=i.ovs_port, ip_address=i.ip_address, 
                                  mac_address=i.mac_address, status=i.status, i_type=i.type, name=i.name)                    
                n.add_interface(iface)
            
            self.nodes[data.router_id] = n

    def register_of_node(self, datapath_id, datapath):
        '''
        Change of_ready node value to True
        '''
        self.update_of_state_node(datapath_id=datapath_id, datapath=datapath, state=True)

    def unregister_of_node(self, datapath_id, datapath):
        '''
        Change of_ready node value to False
        '''
        self.update_of_state_node(datapath_id=datapath_id, datapath=datapath, state=False)

    def update_of_state_node(self, datapath_id, datapath, state):
        print 'node state update: ' + str(datapath_id)        
        
        node = self.get_of_node_by_datapath_id(datapath_id)

        if node is None:
            #Node does not exist, save datapath on cache
            self.datapath_nodes_cache[datapath_id] = datapath

            print 'Node: ' + str(datapath_id) + ' does not exist on LSDB yet'
            
        else:    
            node.of_ready = state
            node.datapath = datapath

            #Update all services LSPs according to node registration
            self.update_services_lsps()

            print 'Node already exists'

        print 'node ' + datapath_id + ' change state to: OF ' + str(state)

    def get_topology_nodes_interfaces(self, router_id):
        '''
        '''
        interfaces = []
        for i in self.nodes[router_id].interfaces.itervalues():
            interfaces.append(i.ip_address)

        return interfaces

    def modify_topology_node(self, router_id, node_data):
        '''
        '''

        result = False

        #Sanity check
        if(self.nodes.has_key(router_id)):
            node = self.nodes[router_id]

            #Update data info
            node.name = node_data.name
            node.top_type = node_data.top_type

            result = True

        return result

    #######################################################
    ####### INTERFACES primitives
    #######################################################
    def add_topology_ls_interface(self, node, router_id, interface):
        '''
        Add new interface to topology 
        '''
        
        # We use ManagementApp to geth Full topology information about the N
        #mapp = ManagementApp()
        data = self.mng_app.get_node_interface_full_data(node, router_id, interface)
        
        if data is not None:
            #Create the Interface
            iface = Interface(node=node, ovs_port=data.ovs_port, ip_address=data.ip_address, 
                                  mac_address=data.mac_address, status=1, i_type=data.type, name=data.name)
                            
            #Add Interface to corresponding node
            self.nodes[router_id].interfaces[iface.ip_address] = iface
        
    def modify_topology_node_interface(self, router_id, interface_data):
        '''
        '''

        print 'ce_ip_address' +  str(interface_data.ce_ip_address)
        print 'ce_mac_address' + str(interface_data.ce_mac_address)

        result = False
        ip_address = interface_data.ip_address

        #Sanity check
        if(self.nodes.has_key(router_id)):
            node = self.nodes[router_id]

            if(node.interfaces.has_key(ip_address)):
                interface = node.interfaces[ip_address]

                #Update data info
                interface.type = interface_data.type

                if interface_data.type == 1:
                    interface.ce_ip_address = interface_data.ce_ip_address
                    interface.ce_mac_address = interface_data.ce_mac_address

                data = self.mng_app.get_node_interface_full_data(node, router_id, interface)
                if data is not None:
                    status = 1

                result = True
                
        return result

    #######################################################
    ####### LINKS primitives
    #######################################################
    def add_topology_ls_interface_link(self, router_id, ip_address, link):
        '''
        Add new link to topology. If some of two nodes does not exists the link is not created,
        if some of two interfaces does not exists the link is not created, and some kind of combinatios neither
        '''
        
        if(self.nodes.has_key(router_id) and self.nodes.has_key(link.to_node_int.node.router_id)): 

            if(self.nodes[router_id].interfaces.has_key(ip_address) 
                and self.nodes[link.to_node_int.node.router_id].interfaces.has_key(link.to_node_int.ip_address)):

                from_node_int = self.nodes[link.from_node_int.node.router_id].interfaces[link.from_node_int.ip_address]
                to_node_int = self.nodes[link.to_node_int.node.router_id].interfaces[link.to_node_int.ip_address]
                link = Link(from_node_int=from_node_int, to_node_int=to_node_int, status=1, weight=link.weight)
                self.nodes[router_id].interfaces[ip_address].links[link.to_node_int.ip_address] = link

    #######################################################
    ####### MPLS/LDP primitives
    #######################################################

    ########### Services primitives ############################
    def add_service(self, service):
        '''
        Documentation
        '''

        result = True

        #Get MPLS label for new service
        label = self.mpls_label_sec
        self.mpls_label_sec = increment_hex_value(self.mpls_label_sec)

        #Create Service with service information
        data = Service(in_port=service.in_port, in_phy_port=service.in_phy_port, metadata=service.metadata, eth_dst=service.eth_dst, 
                    eth_src=service.eth_src, eth_type=service.eth_type, vlan_vID=service.vlan_vID, vlan_PCP=service.vlan_PCP, 
                    IP_dscp=service.IP_dscp, IP_ecn=service.IP_ecn, IP_proto=service.IP_proto, IPv4_src=service.IPv4_src, 
                    IPv4_dst=service.IPv4_dst, TCP_src=service.TCP_src, TCP_dst=service.TCP_dst, UDP_src=service.UDP_src, 
                    UDP_dst=service.UDP_dst, SCTP_src=service.SCTP_src, SCTP_dst=service.SCTP_dst, ICMPv4_type=service.ICMPv4_type, 
                    ICMPv4_code=service.ICMPv4_code, ARP_op=service.ARP_op, ARP_spa=service.ARP_spa, ARP_tpa=service.ARP_tpa, 
                    ARP_sha=service.ARP_sha, ARP_tha=service.ARP_tha, IPv6_src=service.IPv6_src, 
                    IPv6_dst=service.IPv6_dst, IPv6_flabel=service.IPv6_flabel, ICMPv6_type=service.ICMPv6_type, 
                    ICMPv6_code=service.ICMPv6_code, IPv6_nd_target=service.IPv6_nd_target, IPv6_nd_ssl=service.IPv6_nd_ssl,
                    IPv6_nd_tll =service.IPv6_nd_tll, MPLS_label=service.MPLS_label, MPLS_tc=service.MPLS_tc, MPLS_bos=service.MPLS_bos, 
                    PBB_is_id=service.PBB_is_id, tunnel_id =service.tunnel_id, IPv6_txhdr=service.IPv6_txhdr, 
                    VPN_service_type=service.VPN_service_type)

        #Asociates source and destination service nodes on MPLS core 7
        src_node = self.nodes[service.ingress_core_node]
        dst_node = self.nodes[service.egress_core_node]

        ingress_interface = src_node.interfaces[service.ingress_interface]
        egress_interface = dst_node.interfaces[service.egress_interface]
        data.ingress_node = src_node
        data.egress_node = dst_node
        data.ingress_interface = ingress_interface
        data.egress_interface = egress_interface
        data.name = service.name
        data.color = service.color
        data.label = label

        # If service VPN type == 2 then have a list of mpls labels for each ethertype
        if service.VPN_service_type == 2:
            data.labels = self.get_mpls_labels_for_service_ethertypes(self.mpls_label_sec)

        #Creates an LSP for new service
        lsp = self.get_lsp(service=data)
        data.lsps.append(lsp)

        #Agregate service to controller services collection
        self.servs[data.ID] = data

        return result

    def get_mpls_labels_for_service_ethertypes(self, mpls_label_sec):
        '''
        Asigna una etiqueta mpls a cada ethertype para un servicio determinado utilizando el espacio de etiquetas
        mpls que se utilza para las etiquetas de los servicios
        '''

        label = mpls_label_sec
        labels = {}

        for item in settings.SUPPORTED_ETHERTYPES:
            labels[item] = label    
            label = increment_hex_value(label)
            
        # labels['0x0800'] = label
        # label = increment_hex_value(label)
        # labels['0x0806']= label
        # label = increment_hex_value(label)
        # labels['0x0842']= label
        # label = increment_hex_value(label)
        # labels['0x22F0']= label
        # label = increment_hex_value(label)
        # labels['0x22F3']= label
        # label = increment_hex_value(label)
        # labels['0x6003']= label
        # label = increment_hex_value(label)
        # labels['0x8035']= label
        # label = increment_hex_value(label)
        # labels['0x809B']= label
        # label = increment_hex_value(label)
        # labels['0x80F3']= label
        # label = increment_hex_value(label)
        # labels['0x8100']= label
        # label = increment_hex_value(label)
        # labels['0x8137']= label
        # label = increment_hex_value(label)
        # labels['0x8138']= label
        # label = increment_hex_value(label)
        # labels['0x8204']= label
        # label = increment_hex_value(label)
        # labels['0x86DD']= label
        # label = increment_hex_value(label)
        # labels['0x8808']= label
        # label = increment_hex_value(label)
        # labels['0x8809']= label
        # label = increment_hex_value(label)
        # labels['0x8809']= label
        # label = increment_hex_value(label)
        # labels['0x8847']= label
        # label = increment_hex_value(label)
        # labels['0x8848']= label
        # label = increment_hex_value(label)
        # labels['0x8863']= label
        # label = increment_hex_value(label)
        # labels['0x8864']= label
        # label = increment_hex_value(label)
        # labels['0x8870']= label
        # label = increment_hex_value(label)
        # labels['0x0800']= label
        # label = increment_hex_value(label)
        # labels['0x887B']= label
        # label = increment_hex_value(label)
        # labels['0x888E']= label
        # label = increment_hex_value(label)
        # labels['0x8892']= label
        # label = increment_hex_value(label)
        # labels['0x889A']= label
        # label = increment_hex_value(label)
        # labels['0x88A2']= label
        # label = increment_hex_value(label)
        # labels['0x88A4']= label
        # label = increment_hex_value(label)
        # labels['0x88A8']= label
        # label = increment_hex_value(label)
        # labels['0x88AB']= label
        # label = increment_hex_value(label)
        # labels['0x88CC']= label
        # label = increment_hex_value(label)
        # labels['0x88CD']= label
        # label = increment_hex_value(label)
        # labels['0x88E1']= label
        # label = increment_hex_value(label)
        # labels['0x88E3']= label
        # label = increment_hex_value(label)
        # labels['0x88E5']= label
        # label = increment_hex_value(label)
        # labels['0x88F7']= label
        # label = increment_hex_value(label)
        # labels['0x8902']= label
        # label = increment_hex_value(label)
        # labels['0x8906']= label
        # label = increment_hex_value(label)
        # labels['0x8914']= label
        # label = increment_hex_value(label)
        # labels['0x8915']= label
        # label = increment_hex_value(label)
        # labels['0x892F']= label
        # label = increment_hex_value(label)
        # labels['0x9000']= label
        # label = increment_hex_value(label)
        # labels['0xCAFE']= label
        # label = increment_hex_value(label)

        self.mpls_label_sec = label

        return labels

    def update_service(self, service):
        '''
        Documentation
        '''

        result = True

        s = self.servs[service.ID]

        #Update service data
        s.in_port=service.in_port 
        s.in_phy_port=service.in_phy_port 
        s.metadata=service.metadata
        s.eth_dst=service.eth_dst
        s.eth_src=service.eth_src
        s.eth_type=service.eth_type 
        s.vlan_vID=service.vlan_vID 
        s.vlan_PCP=service.vlan_PCP 
        s.IP_dscp=service.IP_dscp 
        s.IP_ecn=service.IP_ecn
        s.IP_proto=service.IP_proto 
        s.IPv4_src=service.IPv4_src 
        s.IPv4_dst=service.IPv4_dst 
        s.TCP_src=service.TCP_src 
        s.TCP_dst=service.TCP_dst 
        s.UDP_src=service.UDP_src 
        s.UDP_dst=service.UDP_dst 
        s.SCTP_src=service.SCTP_src 
        s.SCTP_dst=service.SCTP_dst 
        s.ICMPv4_type=service.ICMPv4_type 
        s.ICMPv4_code=service.ICMPv4_code 
        s.ARP_op=service.ARP_op 
        s.ARP_spa=service.ARP_spa 
        s.ARP_tpa=service.ARP_tpa 
        s.ARP_sha=service.ARP_sha 
        s.ARP_tha=service.ARP_tha 
        s.IPv6_src=service.IPv6_src 
        s.IPv6_dst=service.IPv6_dst 
        s.IPv6_flabel=service.IPv6_flabel 
        s.ICMPv6_type=service.ICMPv6_type 
        s.ICMPv6_code=service.ICMPv6_code 
        s.IPv6_nd_target=service.IPv6_nd_target 
        s.IPv6_nd_ssl=service.IPv6_nd_ssl
        s.IPv6_nd_tll =service.IPv6_nd_tll 
        s.MPLS_label=service.MPLS_label 
        s.MPLS_tc=service.MPLS_tc 
        s.MPLS_bos=service.MPLS_bos 
        s.PBB_is_id=service.PBB_is_id
        s.tunnel_id =service.tunnel_id 
        s.IPv6_txhdr=service.IPv6_txhdr

        #Asociates source and destination service nodes on MPLS core 
        src_node = self.nodes[service.ingress_core_node]
        dst_node = self.nodes[service.egress_core_node]
        ingress_interface = src_node.interfaces[service.ingress_interface]
        egress_interface = dst_node.interfaces[service.egress_interface]
        
        s.ingress_node = src_node
        s.egress_node = dst_node
        s.ingress_interface = ingress_interface
        s.egress_interface = egress_interface
        s.name = service.name
        s.color = service.color

        return result

    def get_services(self):
        '''
        Doc
        '''    

        services = []

        for s in self.servs.itervalues():
            data = DTService(ID=s.ID, in_port=s.in_port, in_phy_port=s.in_phy_port, metadata=s.metadata, eth_dst=s.eth_dst, 
                    eth_src=s.eth_src, eth_type=s.eth_type, vlan_vID=s.vlan_vID, vlan_PCP=s.vlan_PCP, 
                    IP_dscp=s.IP_dscp, IP_ecn=s.IP_ecn, IP_proto=s.IP_proto, IPv4_src=s.IPv4_src, 
                    IPv4_dst=s.IPv4_dst, TCP_src=s.TCP_src, TCP_dst=s.TCP_dst, UDP_src=s.UDP_src, 
                    UDP_dst=s.UDP_dst, SCTP_src=s.SCTP_src, SCTP_dst=s.SCTP_dst, ICMPv4_type=s.ICMPv4_type, 
                    ICMPv4_code=s.ICMPv4_code, ARP_op=s.ARP_op, ARP_spa=s.ARP_spa, ARP_tpa=s.ARP_tpa, 
                    ARP_sha=s.ARP_sha, ARP_tha=s.ARP_tha, IPv6_src=s.IPv6_src, 
                    IPv6_dst=s.IPv6_dst, IPv6_flabel=s.IPv6_flabel, ICMPv6_type=s.ICMPv6_type, 
                    ICMPv6_code=s.ICMPv6_code, IPv6_nd_target=s.IPv6_nd_target, IPv6_nd_ssl=s.IPv6_nd_ssl,
                    IPv6_nd_tll =s.IPv6_nd_tll, MPLS_label=s.MPLS_label, MPLS_tc=s.MPLS_tc, MPLS_bos=s.MPLS_bos, 
                    PBB_is_id=s.PBB_is_id, tunnel_id =s.tunnel_id, IPv6_txhdr=s.IPv6_txhdr,
                    ingress_core_node=s.ingress_node.router_id, egress_core_node=s.egress_node.router_id, 
                    ingress_interface=s.ingress_interface.ip_address, egress_interface=s.egress_interface.ip_address, name=s.name,
                    color=s.color, VPN_service_type=s.VPN_service_type)
            services.append(data)

        return services

    def get_service(self, service_ID):
        '''
        Doc
        '''    

        service = self.servs[service_ID]

       
        data = DTService(ID=s.ID, in_port=s.in_port, in_phy_port=s.in_phy_port, metadata=s.metadata, eth_dst=s.eth_dst, 
                eth_src=s.eth_src, eth_type=s.eth_type, vlan_vID=s.vlan_vID, vlan_PCP=s.vlan_PCP, 
                IP_dscp=s.IP_dscp, IP_ecn=s.IP_ecn, IP_proto=s.IP_proto, IPv4_src=s.IPv4_src, 
                IPv4_dst=s.IPv4_dst, TCP_src=s.TCP_src, TCP_dst=s.TCP_dst, UDP_src=s.UDP_src, 
                UDP_dst=s.UDP_dst, SCTP_src=s.SCTP_src, SCTP_dst=s.SCTP_dst, ICMPv4_type=s.ICMPv4_type, 
                ICMPv4_code=s.ICMPv4_code, ARP_op=s.ARP_op, ARP_spa=s.ARP_spa, ARP_tpa=s.ARP_tpa, 
                ARP_sha=s.ARP_sha, ARP_tha=s.ARP_tha, IPv6_src=s.IPv6_src, 
                IPv6_dst=s.IPv6_dst, IPv6_flabel=s.IPv6_flabel, ICMPv6_type=s.ICMPv6_type, 
                ICMPv6_code=s.ICMPv6_code, IPv6_nd_target=s.IPv6_nd_target, IPv6_nd_ssl=s.IPv6_nd_ssl,
                IPv6_nd_tll =s.IPv6_nd_tll, MPLS_label=s.MPLS_label, MPLS_tc=s.MPLS_tc, MPLS_bos=s.MPLS_bos, 
                PBB_is_id=s.PBB_is_id, tunnel_id =s.tunnel_id, IPv6_txhdr=s.IPv6_txhdr,
                ingress_core_node=s.ingress_node.router_id, egress_core_node=s.egress_node.router_id, 
                ingress_interface=s.ingress_interface.ip_address, egress_interface=s.egress_interface.ip_address, name=s.name)

        return data

    def delete_service(self, sid):
        '''
        doc
        '''

        result = True

        print 'Deletes Service wieth service-ID: ' + sid

        #Sanity check
        if self.servs.has_key(sid):
            #Remove service from services collection
            s = self.servs.pop(sid)

            #For each service LSP remove asociated MPLS table entries on rcorresponding node tables
            for lsp in s.lsps:
                self.delete_lsp(s, lsp) 

        else:
            result = False

        return result

    ########### LSPs primitives ############################
    def get_lsp(self, service):
        '''
        Creates LSP for specific service
        '''

        #Get the best path between source and destination nodes on MPLS core (Links collection)
        path = self.get_best_path(service.ingress_node, service.egress_node)

        #Get lsp from best path
        lsp_labels = self.get_path_mpls_labels(path)

        #Creates instance of LSP
        path_nodes = []
        for i in range(len(path)):

            pn = PathNode(label=lsp_labels[i], link=path[i])
            path_nodes.append(pn)

        lsp = LSP(path=path_nodes)

        #Update MPLS tables in each path node with specific label processing
        ftn_add = {}
        ilm_add = {}
        ftn_add, ilm_add = self.update_mpls_tables(service, path, lsp_labels)

        ### Update OF tables

        #Remove flow from FTN entry
        items = ftn_add.items()
        n = self.nodes[items[0][0]]
        ftn = items[0][1]

        #If LSP length = 1 then only have service PUSH label so one only NHLFE entry. Othercase we have 2 NHLFE entry
        nhlfe = None
        path_len = len(path)
        if path_len == 1:
            nhlfe = ftn.nhlfes[0]
        else:
            nhlfe = ftn.nhlfes[1]

        #Get ovs port for interface
        interface = None 
        if nhlfe.interface is not None:
            interface = nhlfe.interface.ovs_port

        #Get ovs port for next hop
        next_hop = None 
        if nhlfe.next_hop is not None:
            next_hop = nhlfe.next_hop.ovs_port

        datapath.install_ingress_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                ovs_port_out=next_hop, label_in=None, 
                                                action=nhlfe.action, path_len=path_len)

        #Remove flow from ILM entry
        #First remove ultimate hop
        ilm_last = ilm_add.pop(service.egress_node.router_id)

        for ilm_key in ilm_add:
            n = self.nodes[ilm_key]
            ilm = ilm_add[ilm_key]

            for nhlfe in ilm.nhlfes:

                #Get ovs port for interface
                interface = None 
                if nhlfe.interface is not None:
                    interface = nhlfe.interface.ovs_port
                #Get ovs port for next hop
                next_hop = None 
                if nhlfe.next_hop is not None:
                    next_hop = nhlfe.next_hop.ovs_port

                datapath.install_node_flow_for_service(service=Service(), node=n, ovs_port_in=interface, 
                                                        ovs_port_out=next_hop, label_in=ilm.label, 
                                                        action=nhlfe.action)


        #Get ovs port for interface
        interface = ilm_last.nhlfes[0].interface.ovs_port
        action = ilm_last.nhlfes[0].action

        #Get ovs port for next hop
        next_hop = service.egress_interface.ovs_port
        
        datapath.install_egress_node_flow_for_service(service=service, node=service.egress_node, 
                                                        ovs_port_in=interface, 
                                                        ovs_port_out=next_hop, label_in=service.label, 
                                                        action=action, interface=service.egress_interface)

        return lsp

    def delete_lsp(self, service, lsp):
        '''
        Delete LSP fo
        '''

        #Get lsp path
        path = lsp.path

        ftn_removes = {}
        ilm_removes = {}
            
        #Sanity check
        if len(path) != 0:

            #First remove all MPLS tables entries asociated with specific LSP
            if len(path) == 1:

                node = path[0].link.from_node_int.node
                
                action = DTMPLSAction(label=service.label)
                action.set_action_PUSH()

                nhlfe = NHLFE(interface=service.ingress_interface, next_hop=path[0].link.from_node_int, action=action,
                                label_level=1)

                #Check if entry already exists
                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                #Removes nhlfe entry if only actual ftn reference nhlfe entry in table
                node.decrement_nhlfe_entry_references(nhlfe)

                ftn = FTN(service=service, nhlfes=[nhlfe_entry])

                #Only exists one unique FTN entry for each service
                node.remove_ftn_entry(ftn)
                ftn_removes[node.router_id] = ftn

                #Remove ILM entry asociated to POP service label
                node = service.egress_node
                action = DTMPLSAction(label=service.label)
                action.set_action_POP()
                nhlfe = NHLFE(interface=path[0].link.to_node_int, next_hop=service.egress_interface, action=action)

                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                #Removes nhlfe entry if only actual ftn reference nhlfe entry in table
                node.decrement_nhlfe_entry_references(nhlfe)

                ilm = ILM(label=service.label, nhlfes=[nhlfe_entry], ilm_type=1, service=service)

                node.remove_ilm_entry(ilm)
                ilm_removes[node.router_id] = ilm

            else:

                # Path lenth is bigger than 1, so we have ingress node, penultimate hop and egress node
                node = path[0].link.from_node_int.node

                action = DTMPLSAction(label=service.label)
                action.set_action_PUSH()

                nhlfe0 = NHLFE(interface=service.ingress_interface, next_hop=path[0].link.from_node_int, action=action,
                                label_level=1)
                node.decrement_nhlfe_entry_references(nhlfe0)

                #Instance FTN and NHLFE entry for first hop
                action = DTMPLSAction(label=path[0].label)
                action.set_action_PUSH()
               
                nhlfe = NHLFE(interface=service.ingress_interface, next_hop=path[0].link.from_node_int, action=action)
                
                nhlfe_entry = node.get_nhlfe_entry(nhlfe)
               
                #Removes nhlfe entry if only actual ftn reference nhlfe entry in table
                node.decrement_nhlfe_entry_references(nhlfe)

                ftn = FTN(service=service, nhlfes=[nhlfe0, nhlfe_entry])
                node.remove_ftn_entry(ftn)

                ftn_removes[node.router_id] = ftn

                #Process all other nodes except penultimate and ultimate nodes
                ingress_int = path[0].link.from_node_int
                label_in = path[0].label
                for i in range(1, len(path)-1):
                    node = path[i].link.from_node_int.node

                    #Instance ILM and NHLFE entry
                    action = DTMPLSAction(label=path[i].label)
                    action.set_action_SWAP()
                    nhlfe = NHLFE(interface=ingress_int, next_hop=path[i].link.from_node_int, action=action)
                
                    nhlfe_entry = node.get_nhlfe_entry(nhlfe)
                   
                    #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                    node.decrement_nhlfe_entry_references(nhlfe_entry)

                    ilm = ILM(label=label_in, nhlfes=[nhlfe_entry])

                    #Check if exists ILM entry for service
                    node.remove_ilm_entry(ilm)

                    ilm_removes[node.router_id] = ilm

                    #Update ingress interface and label for next hop
                    ingress_int = path[i].link.from_node_int
                    label_in = path[i].label

                #Process penultimate hop that is equal to process ultimate link
                node = path[-1].link.from_node_int.node

                action = DTMPLSAction(label=label_in)
                action.set_action_POP()
                nhlfe = NHLFE(interface=ingress_int, next_hop=path[-1].link.from_node_int, action=action)

                nhlfe_entry = node.get_nhlfe_entry(nhlfe)
                   
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.decrement_nhlfe_entry_references(nhlfe_entry)

                ilm = ILM(label=label_in, nhlfes=[nhlfe_entry])

                #Check if exists ILM entry for service
                node.remove_ilm_entry(ilm)

                ilm_removes[node.router_id] = ilm

                #Remove ILM entry asociated to POP service label
                node = service.egress_node
                action = DTMPLSAction(label=service.label)
                action.set_action_POP()
                nhlfe = NHLFE(interface=path[-1].link.to_node_int, next_hop=service.egress_interface, action=action)

                #Removes nhlfe entry if only actual ftn reference nhlfe entry in table
                node.decrement_nhlfe_entry_references(nhlfe)

                ilm = ILM(label=service.label, nhlfes=[nhlfe], ilm_type=1, service=service)

                node.remove_ilm_entry(ilm)
                ilm_removes[node.router_id] = ilm

            ### Remove flows from nodes OF tables

            #Remove flow from FTN entry
            for ftn_key in ftn_removes:
                n = self.nodes[ftn_key]
                ftn = ftn_removes[ftn_key]
                service = ftn.service
                
                nhlfe = None
                path_len = len(path)
                if path_len == 1:
                    nhlfe = ftn.nhlfes[0]
                else:
                    nhlfe = ftn.nhlfes[1]

                #Second NHLFE is entry for outer label                   
                #Get ovs port for interface
                interface = None 
                if nhlfe.interface is not None:
                    interface = nhlfe.interface.ovs_port

                #Get ovs port for next hop
                next_hop = None 
                if nhlfe.next_hop is not None:
                    next_hop = nhlfe.next_hop.ovs_port

                datapath.remove_ingress_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                    ovs_port_out=next_hop, label_in=None, path_len=path_len)

            #Remove flow from ILM entry
            for ilm_key in ilm_removes:
                n = self.nodes[ilm_key]
                ilm = ilm_removes[ilm_key]
                service = Service() #Uses empty services

                for nhlfe in ilm.nhlfes:

                    #Get ovs port for interface
                    interface = None 
                    if nhlfe.interface is not None:
                        interface = nhlfe.interface.ovs_port
                    #Get ovs port for next hop
                    next_hop = None 
                    if nhlfe.next_hop is not None:
                        next_hop = nhlfe.next_hop.ovs_port

                    #If next_hop is an external interface then is an egress node
                    if next_hop != None and nhlfe.next_hop.type == 1:
                        datapath.remove_egress_node_flow_for_service(ilm.service, n, interface, next_hop, ilm.label)
                    else:
                        datapath.remove_node_flow_for_service(service, n, interface, next_hop, ilm.label)

    def get_path_mpls_labels(self, path):
        '''
        Calculates for each hop on path wich is the most suitable mpls label and save them
        on node interface labels in use list
        '''

        print 'get_path_mpls_labels'

        mpls_path = []

        if len(path) == 0:
            #Ther is not path betwen nodes
            print 'NO path found'

        elif len(path) == 1:
            #If path have only one hop, them the lsp is empty becouse first node is penultimate hop
            mpls_path.append(None)
        
        else:
            #We asign labels for mpls path secuencialy starting on the lowest label value
            label_base = self.MPLS_LABEL_SPACE_MIN

            #We separates ultimate hop
            for l in path[:-1]:
                
                #Gets avaiable label
                label = self.get_avaiable_mpls_label_for_interface(l, label_base)

                #Add label to lsp
                mpls_path.append(label)

                #Increments mpls label_base
                label_base = increment_hex_value(label_base)

            #The penultimate hop remove all mpls labels, then the last link has not asociated label
            mpls_path.append(None)

        return mpls_path

    def get_avaiable_mpls_label_for_interface(self, link, label_base):
        '''
        docs
        '''

        #Get labels in use for specific interface
        labels_in_use = link.to_node_int.mpls_labels

        #Look for avaiable mpls label
        next_label = label_base
        label = None
        while label is None and next_label < self.MPLS_LABEL_SPACE_MAX:
            if next_label in labels_in_use:
                next_label = increment_hex_value(next_label)
            else:
                label = next_label

        
        if label is not None:
            #Add label to the interface list of labels in use
            link.to_node_int.mpls_labels.append(label)

        return label

    def get_service_lsps(self, service_ID):
        '''
        Return all lsp asociated wieth specific service
        '''

        lsps = []
        
        if self.servs.has_key(service_ID):
            service = self.servs[service_ID]
            for lsp in service.lsps:
                #Get mpls labels, nodes, interfaces and links of the LSP
                mpls_labels = []
                nodes = []
                interfaces = []
                links = []
                
                
                for i in lsp.path:
                    mpls_labels.append(i.label)
                    nodes.append(i.link.to_node_int.node.router_id)
                    interfaces.append(i.link.from_node_int.ip_address)
                    link = DTLSPLink(mpls_label=i.label, 
                                     src_datapath_id=i.link.from_node_int.node.datapath_id, 
                                     src_ovs_port=i.link.from_node_int.ovs_port, 
                                     dst_datapath_id=i.link.to_node_int.node.datapath_id, 
                                     dst_ovs_port=i.link.to_node_int.ovs_port)
                    links.append(link)

                data = DTLSP(links=links, mpls_labels_path=mpls_labels, nodes_path=nodes, interfaces_path=interfaces)

                lsps.append(data)

        else:
            print 'No Service with ID: ' + service_ID
            
        return lsps

    def get_services_lsps(self):
        '''
        
        '''

        services = []
        for s in self.servs.itervalues():

            lsps = []
            for lsp in s.lsps:
                links = []
                
                for i in lsp.path:

                    data = DTLSPLink(mpls_label=i.label, src_datapath_id=i.link.from_node_int.node.datapath_id, 
                                src_ovs_port=i.link.from_node_int.ovs_port, 
                                dst_datapath_id=i.link.to_node_int.node.datapath_id, 
                                dst_ovs_port=i.link.to_node_int.ovs_port)
                    links.append(data)

                data_lsp = DTLSP(links=links)
                lsps.append(data_lsp)
            
            data_service = DTServiceLSP(ID=s.ID, lsps=lsps, color=s.color, name=s.name)
            services.append(data_service)

        return services

    def update_mpls_tables(self, service, path, mpls_labels):
        '''
        For each node in the path, update node mpls tables (FTN, NHLFE, ILM) according to 
        the specific mpls processing
        '''

        ilm_adds = {}
        ftn_adds = {}

        #Sanity check
        if len(path) != 0:

            # We process path according to the followings rules:
            #    First node on path is a border core node thereforce we need to specify an FTN and NHLFE entries
            #    All other nodes except last one are middle nodes thereforce we need to specify ILM and NHLFE entries
            #    Last node is a border and egress node so traffic must arribe without labels to them. For that penultimate
            #    hop does not push MPLS label

            if len(path) == 1:

                node = path[0].from_node_int.node
                
                #There is no labels and no penultimate hop, only a forwarding rule and Service label
                
                #Instance FTN and NHLFE entry for first hop, if nhlfe already exists FTN reference existing entry,
                #in other case creates new NHLFE entry

                #Action for MPLS service label identification push
                action = DTMPLSAction(label=service.label)
                action.set_action_PUSH()

                nhlfe = NHLFE(interface=service.ingress_interface, next_hop=path[0].from_node_int, action=action,
                                label_level=1)
                
                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                if nhlfe_entry is None:
                    nhlfe_entry = nhlfe
               
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry)

                ftn = FTN(service=service, nhlfes=[nhlfe_entry])

                #Only exists one unique FTN entry for each service
                node.add_ftn_entry(ftn)

                ftn_adds[node.router_id] = ftn

                ### Removes Label on ultimate hop

                #Update node to egress node
                node = service.egress_node
                action = DTMPLSAction(label=service.label)
                action.set_action_POP()
                nhlfe = NHLFE(interface=path[0].to_node_int, next_hop=service.egress_interface, action=action)

                nhlfe_entry = None
                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                if nhlfe_entry is None:
                    nhlfe_entry = nhlfe
                   
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry)

                ilm = ILM(label=service.label, nhlfes=[nhlfe_entry], ilm_type=1, service=service)

                #Check if exists ILM entry for service
                ilm_entry = node.get_ilm_entry(ilm)

                if ilm_entry is None:
                    #There is not an ILM entry for specific service
                    node.add_ilm_entry(ilm)
                    ilm_adds[node.router_id] = ilm
                else:
                    #Ther is an ILM entry for specific service
                    ilm_entry.add_nhlfe_entry(nhlfe_entry)
                    ilm_adds[node.router_id] = ilm_entry
            else:

                # Path lenth is bigger than 1, so we have ingress node, penultimate hop and egress node
                node = path[0].from_node_int.node

                #Put label used to identificate service -> Inner label
                action = DTMPLSAction(label=service.label)
                action.set_action_PUSH()

                nhlfe0 = NHLFE(interface=service.ingress_interface, next_hop=path[0].from_node_int, action=action,
                                label_level=1)
                nhlfe_entry0 = node.get_nhlfe_entry(nhlfe0)

                if nhlfe_entry0 is None:
                    nhlfe_entry0 = nhlfe0
               
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry0)

                #Put second level of label -> Outer label

                #Instance FTN and NHLFE entry for first hop
                action = DTMPLSAction(label=mpls_labels[0])
                action.set_action_PUSH()
               
                #Instance FTN and NHLFE entry for first hop, if nhlfe already exists FTN reference existing entry,
                #in other case creates new NHLFE entry
                nhlfe = NHLFE(interface=service.ingress_interface, next_hop=path[0].from_node_int, action=action)
                
                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                if nhlfe_entry is None:
                    nhlfe_entry = nhlfe
               
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry)

                #Add NHLFE entry to push label service
                ftn = FTN(service=service, nhlfes=[nhlfe_entry0, nhlfe_entry])

                node.add_ftn_entry(ftn)
                ftn_adds[node.router_id] = ftn

                #Install flow on datapath

                #Process all other nodes except penultimate and ultimate nodes
                ingress_int = path[0].from_node_int
                label_in = mpls_labels[0]
                for i in range(1, len(path)-1):
                    node = path[i].from_node_int.node


                    #Instance ILM and NHLFE entry
                    action = DTMPLSAction(label=mpls_labels[i])
                    action.set_action_SWAP()
                    nhlfe = NHLFE(interface=ingress_int, next_hop=path[i].from_node_int, action=action)
                
                    nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                    if nhlfe_entry is None:
                        nhlfe_entry = nhlfe
                   
                    #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                    node.add_nhlfe_entry(nhlfe_entry)

                    ilm = ILM(label=label_in, nhlfes=[nhlfe])

                    #Check if exists ILM entry for service
                    ilm_entry = node.get_ilm_entry(ilm)

                    if ilm_entry is None:
                        #There is not an ILM entry for specific service
                        ilm_entry = ilm
                        ilm_entry.add_nhlfe_entry(nhlfe_entry)
                    else:
                        #Ther is an ILM entry for specific service
                        ilm_entry.add_nhlfe_entry(nhlfe_entry)

                    #Add ILM entry
                    node.add_ilm_entry(ilm_entry)
                    ilm_adds[node.router_id] = ilm_entry

                    #Update ingress interface and label for next hop
                    ingress_int = path[i].from_node_int
                    label_in = mpls_labels[i]

                #Process penultimate hop that is equal to process ultimate link
                node = path[-1].from_node_int.node

                action = DTMPLSAction(label=label_in)
                action.set_action_POP()
                nhlfe = NHLFE(interface=ingress_int, next_hop=path[-1].from_node_int, action=action)

                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                if nhlfe_entry is None:
                    nhlfe_entry = nhlfe
                   
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry)

                ilm = ILM(label=label_in, nhlfes=[nhlfe_entry])

                #Check if exists ILM entry for service
                ilm_entry = node.get_ilm_entry(ilm)

                if ilm_entry is None:
                    #There is not an ILM entry for specific service
                    node.add_ilm_entry(ilm)
                    ilm_adds[node.router_id] = ilm
                else:
                    #Ther is an ILM entry for specific service
                    ilm_entry.add_nhlfe_entry(nhlfe_entry)
                    ilm_adds[node.router_id] = ilm_entry

                #Removes service Label on ultimate hop
                node = path[-1].to_node_int.node
                action = DTMPLSAction(label=service.label)
                action.set_action_POP()
                nhlfe = NHLFE(interface=path[-1].to_node_int, next_hop=service.egress_interface, action=action)

                nhlfe_entry = node.get_nhlfe_entry(nhlfe)

                if nhlfe_entry is None:
                    nhlfe_entry = nhlfe
                   
                #In case NHLFE entry already exist add_nhlfe_entry increment references counter
                node.add_nhlfe_entry(nhlfe_entry)

                ilm = ILM(label=service.label, nhlfes=[nhlfe_entry], ilm_type=1, service=service)

                #Check if exists ILM entry for service
                ilm_entry = node.get_ilm_entry(ilm)

                if ilm_entry is None:
                    #There is not an ILM entry for specific service
                    node.add_ilm_entry(ilm)
                    ilm_adds[node.router_id] = ilm
                else:
                    #Ther is an ILM entry for specific service
                    ilm_entry.add_nhlfe_entry(nhlfe_entry)
                    ilm_adds[node.router_id] = ilm_entry
 

        return ftn_adds, ilm_adds

    def update_services_lsps(self):
        '''
        Update each service lspsu
        '''

        #First clear all MPLS tables for each node, but before create a copy of the table
        mpls_tables_ftn = {}
        mpls_tables_ilm = {}

        for n in self.nodes.itervalues():
            #Copy only the object pointers
        
            mpls_tables_ilm[n.router_id] = n.ilm
            n.ilm = []

            mpls_tables_ftn[n.router_id] = n.ftn
            n.ftn = []

            n.nhlfe = []
            
        #Second recalculate besth path and then update LSP for each Service
        #For each service
        for s in self.servs.itervalues():

            #For each service LSP
            lsps_nuevos = []
            for lsp in s.lsps:
                
                #Update LSP
                lsp_nuevo = self.update_lsp(s, lsp)
                lsps_nuevos.append(lsp_nuevo)
        
            s.lsps = lsps_nuevos

        #Finally install flows for all entries on new MPLS tables ther is not in old MPLS tables and remove 
        #flows for all entries on old MPLS tables there is not in new MPLS tables
        for n in self.nodes.itervalues():
            
            ftn_adds = set(n.ftn) - set(mpls_tables_ftn[n.router_id])
            ftn_removes = set(mpls_tables_ftn[n.router_id]) - set(n.ftn)

            ilm_adds = set(n.ilm) - set(mpls_tables_ilm[n.router_id])
            ilm_removes = set(mpls_tables_ilm[n.router_id]) - set(n.ilm)

            ##### First eliminate all old flows on datapath

            #Remove flows for old FTN entries
            for ftn in ftn_removes:
                service = ftn.service

                nhlfe = None
                path_len = len(ftn.nhlfes)
                if path_len == 1:
                    nhlfe = ftn.nhlfes[0]
                else:
                    nhlfe = ftn.nhlfes[1]

                #Get ovs port for interface
                interface = None 
                if nhlfe.interface is not None:
                    interface = nhlfe.interface.ovs_port

                #Get ovs port for next hop
                next_hop = None 
                if nhlfe.next_hop is not None:
                    next_hop = nhlfe.next_hop.ovs_port

                datapath.remove_ingress_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                    ovs_port_out=next_hop, label_in=None, path_len=path_len)
                    

            #Remove flows for old ILM entries
            for ilm in ilm_removes:
                service = Service()
                #service = ilm.service

                for nhlfe in ilm.nhlfes:

                    #Get ovs port for interface
                    interface = None 
                    if nhlfe.interface is not None:
                        interface = nhlfe.interface.ovs_port
                    #Get ovs port for next hop
                    next_hop = None 
                    if nhlfe.next_hop is not None:
                        next_hop = nhlfe.next_hop.ovs_port

                    #If next_hop is an external interface then is an egress node
                    if next_hop != None and nhlfe.next_hop.type == 1:
                        datapath.remove_egress_node_flow_for_service(service, n, interface, next_hop, ilm.label)
                    else:
                        datapath.remove_node_flow_for_service(service, n, interface, next_hop, ilm.label)


            ##### Tnen install all new flows on datapath
            #Install flows for new FTN entries
            for ftn in ftn_adds:
                service = ftn.service

                nhlfe = None
                path_len = len(ftn.nhlfes)#A los efectos de determinar si la entrada tiene 1 o 2 NHLFE sirve
                if path_len == 1:
                    nhlfe = ftn.nhlfes[0]
                else:
                    nhlfe = ftn.nhlfes[1]

                #Get ovs port for interface
                interface = None 
                if nhlfe.interface is not None:
                    interface = nhlfe.interface.ovs_port

                #Get ovs port for next hop
                next_hop = None 
                if nhlfe.next_hop is not None:
                    next_hop = nhlfe.next_hop.ovs_port

                datapath.install_ingress_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                        ovs_port_out=next_hop, label_in=None, 
                                                        action=nhlfe.action, path_len=path_len)

            #Install flows for new FTN entries
            for ilm in ilm_adds:
                service = Service()
                
                for nhlfe in ilm.nhlfes:

                    #Get ovs port for interface
                    interface = None 
                    if nhlfe.interface is not None:
                        interface = nhlfe.interface.ovs_port
                    #Get ovs port for next hop
                    next_hop = None 
                    if nhlfe.next_hop is not None:
                        next_hop = nhlfe.next_hop.ovs_port

                    #If next_hop is an external interface then is an egress node
                    if next_hop != None and nhlfe.next_hop.type == 1:
                        service = ilm.service
                        datapath.install_egress_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                                        ovs_port_out=next_hop, label_in=ilm.label, 
                                                                        action=nhlfe.action, interface=service.egress_interface)
                    else:
                        datapath.install_node_flow_for_service(service=service, node=n, ovs_port_in=interface, 
                                                                ovs_port_out=next_hop, label_in=ilm.label, 
                                                                action=nhlfe.action)

    def update_lsp(self, service, lsp):
        '''
        Update LSP
        First recalculate path and for each hop check for diferents in old LSP
        ''' 

        print 'Updates LSP for path: (' + service.ingress_node.router_id + ',' + service.egress_node.router_id + ')' 


        #Get the best path between source and destination nodes on MPLS core (Links collection)
        path = self.get_best_path(service.ingress_node, service.egress_node)
        labels = []

        print 'BESTH PATH LENGTH:'+ str(len(path))

        new_lsp_path = []
        old_lsp_path = lsp.path

        #We asign labels for mpls path secuencialy starting on the lowest label value
        label_base = self.MPLS_LABEL_SPACE_MIN

        if len(path) > 0:
            if len(path) == 1:
                l = path[0]
                pe = self.get_lsp_entry_by_link(old_lsp_path, l)
                if pe is None:
                    #Get avaiable label
                    label = None
                    pe = PathNode(label=label, link=l)
                    new_lsp_path.append(pe)
                    labels.append(label)
                else:
                    new_lsp_path.append(pe)
                    old_lsp_path.remove(pe)
                    labels.append(pe.label)
            else:

                #Process all other elements    
                for l in path[0:-1]:

                    #Chequea si el link se corresponde con alguna entrada del path del lsp viejo, en ese caso no se debe cambiar 
                    #datapath
                    pe = self.get_lsp_entry_by_link(old_lsp_path, l)
                    if pe is None:
                        #Get avaiable label
                        label = self.get_avaiable_mpls_label_for_interface(l, label_base)
                        pe = PathNode(label=label, link=l)
                        new_lsp_path.append(pe)
                        labels.append(label)
                    else:
                        new_lsp_path.append(pe)
                        old_lsp_path.remove(pe)
                        labels.append(pe.label)

                #Process the last element
                pe = self.get_lsp_entry_by_link(old_lsp_path, path[-1])
                if pe is None:
                    pe = PathNode(label=None, link=path[-1])
                    new_lsp_path.append(pe)
                    labels.append(None)
                else:
                    new_lsp_path.append(pe)
                    old_lsp_path.remove(pe)
                    labels.append(pe.label)
            
        new_lsp = LSP(path=new_lsp_path)

        #Update MPLS tables in each path node with specific label processing
        self.update_mpls_tables(service, path, labels)

        #Remove from interface labels in use, labels for unused lsps hop in new LSP
        for pe in old_lsp_path:

            #Removes mpls label for labels in use for interface
            if pe.label is not None:
                pe.link.to_node_int.mpls_labels.remove(pe.label)
            
        return new_lsp

    def get_lsp_entry_by_link(self, path, link):

        i = 0
        entry = None
        while i<len(path) and entry == None:
            if path[i].link == link:
                entry = path[i]
            else:
                i = i + 1

    def get_node_mpls_tables_nhlfe(self, router_id):
        '''
        Return all entries of NHLFE node table with router_id
        '''

        entries = []

        #Get node 
        if self.nodes.has_key(router_id):
            node = self.nodes[router_id]

            for nhlfe in node.nhlfe:
                action = None 
                if nhlfe.action is not None:
                    action = copy.copy(nhlfe.action)

                interface = None
                if nhlfe.interface is not None:
                    interface = nhlfe.interface.ip_address

                next_hop = None
                if nhlfe.next_hop is not None:
                    next_hop = nhlfe.next_hop.ip_address

                data = DTNHLFE(interface_ip_address=interface, 
                                next_hop_ip_address=next_hop,
                                action=action)

                entries.append(data)


        return entries

    def get_node_mpls_tables_ftn(self, router_id):
        '''
        Return all entries of NHLFE node table with router_id
        '''

        entries = []

        #Get node 
        if self.nodes.has_key(router_id):
            node = self.nodes[router_id]

            for ftn in node.ftn:
                service = ftn.service.To_DTService()

                nhlfes = []
                for nhlfe in ftn.nhlfes:
                    action = None 
                    if nhlfe.action is not None:
                        action = copy.copy(nhlfe.action)

                    interface = None
                    if nhlfe.interface is not None:
                        interface = nhlfe.interface.ip_address

                    next_hop = None
                    if nhlfe.next_hop is not None:
                        next_hop = nhlfe.next_hop.ip_address

                    data = DTNHLFE(interface_ip_address=interface, 
                                    next_hop_ip_address=next_hop,
                                    action=action)

                    nhlfes.append(data)

                data = DTFTN(service=service, nhlfes=nhlfes)
                entries.append(data)

        return entries

    def get_node_mpls_tables_ilm(self, router_id):
        '''
        Return all entries of NHLFE node table with router_id
        '''

        entries = []

        #Get node 
        if self.nodes.has_key(router_id):
            node = self.nodes[router_id]

            for ilm in node.ilm:
                label = ilm.label

                nhlfes = []
                for nhlfe in ilm.nhlfes:
                    action = None 
                    if nhlfe.action is not None:
                        action = copy.copy(nhlfe.action)

                    interface = None
                    if nhlfe.interface is not None:
                        interface = nhlfe.interface.ip_address

                    next_hop = None
                    if nhlfe.next_hop is not None:
                        next_hop = nhlfe.next_hop.ip_address

                    data = DTNHLFE(interface_ip_address=interface, 
                                    next_hop_ip_address=next_hop,
                                    action=action)

                    nhlfes.append(data)

                data = DTILM(label=label, nhlfes=nhlfes)
                entries.append(data)

        return entries

    def get_topology_node_of_table(self, dpid):
        '''
        '''

        #Get Node datapath
        node = self.get_of_node_by_datapath_id(dpid)

        result = datapath.send_table_stats_request(node.datapath, self.waiters)