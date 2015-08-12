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

    def __init__(self, router_id, datapath_id, interfaces=None, status=None, net_type=None, 
                 top_type=None, description=None, of_ready=False, ls_ready=False, name=None):
        '''
        Constructor
        '''
        
        self.name = name
        self.router_id = router_id
        self.datapath_id = datapath_id
        self.status = status
        self.net_type = net_type
        self.top_type = top_type
        self.description = description
        self.interfaces = interfaces
        self.of_ready = of_ready
        self.ls_ready = ls_ready

    def to_JSON(self):
        #Convert to JSON each interface
        interfaces_json = []
        for i in self.interfaces.itervalues():

            links_json = []
            for l in i.links.itervalues():
               
                links_json.append({'status': l.status, 'from_node_int': l.from_node_int.ip_address, 
                                    'to_node_int': l.to_node_int.ip_address, 'weight': str(l.weight)})

            interfaces_json.append({'ip_address':i.ip_address, 'mac_address': i.mac_address, 
                    'ovs_port': i.ovs_port, 'type': i.type, 'links': links_json, 'status': i.status, 'name': i.name, 
                    'ce_ip_address': i.ce_ip_address, 'ce_mac_address': i.ce_mac_address})

        return json.dumps({'name': self.name, 'router_id': self.router_id, 'datapath_id': self.datapath_id, 'of_ready': self.of_ready,
			                 'ls_ready': self.ls_ready, 'status': self.status, 'net_type': self.net_type, 
                             'top_type': self.top_type,'description': self.description, 
                             'interfaces': interfaces_json}, indent=2)
		
##########################################################################
########## DTINTERFACE
##########################################################################
class DTInterface(object):
    '''
    classdocs
    '''

    def __init__(self, ip_address, links=None, mac_address=None, ovs_port=None, i_type=0, name=None, status=None,
                 ce_mac_address=None, ce_ip_address=None):
        '''
        Constructor
        '''
        
        self.name = name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.ovs_port = ovs_port
        self.type = i_type
        self.status = status
        if links is None:
            self.links = {}
        else:
            self.links = links

        # If Interface Type == 1 then we have customer edge information
        self.ce_mac_address = ce_mac_address
        self.ce_ip_address = ce_ip_address
        
##########################################################################
########## DTLINK
##########################################################################   
class DTLink(object):
    '''
    classdocs
    '''

    def __init__(self, from_node_int, to_node_int, status, mpls_label=None, weight=None):
        '''
        Constructor
        '''
        
        self.from_node_int = from_node_int
        self.to_node_int = to_node_int
        self.status = status
        self.mpls_label = mpls_label

        self.weight = weight

##########################################################################
########## DTLSNODE
##########################################################################          
class DTLSNode(object):
    '''
    classdocs
    '''

    def __init__(self, router_id, status, interfaces=None):
        '''
        Constructor
        '''
        
        self.router_id = router_id
        self.status = status
        
        if interfaces is None:
            self.interfaces = {}
        else:
            self.interfaces = interfaces

    def to_JSON(self):
        #Convert to JSON each interface
        interfaces_json = []
        for i in self.interfaces.itervalues():

            links_json = []
            for l in i.links.itervalues():
                links_json.append({'from_node_int': l.from_node_int.ip_address, 
                                    'to_node_int': l.to_node_int.ip_address, 'weight': str(l.weight)})

            interfaces_json.append({'ip_address':i.ip_address, 'links': links_json})

        return json.dumps({'router_id': self.router_id, 'interfaces': interfaces_json}, indent=2)     
            
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
       
##########################################################################
########## DTLSLINK
##########################################################################   
class DTLSLink(object):
    '''
    classdocs
    '''

    def __init__(self, from_node_int, to_node_int, status=1, weight=None):
        '''
        Constructor
        '''
        
        self.from_node_int = from_node_int
        self.to_node_int = to_node_int
        self.status = status
        self.weight = weight
        
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

##########################################################################
########## DTPath
##########################################################################
class DTPath(object):

    '''
    DTPath represent a path between two nodes across the network
    Each entry represents a link
    '''

    def __init__(self, metric, path):
        '''
        Constructor
        '''
        
        self.metric = metric
        self.path = path 
 

##########################################################################
########## DTFec
##########################################################################
class DTFEC(object):
    '''
    classdocs
    '''

    def __init__(self, in_port=None, in_phy_port=None, metadata=None, eth_dst=None, eth_src=None,
        eth_type=None, vlan_vID=None, vlan_PCP=None, IP_dscp=None, IP_ecn=None, IP_proto=None,
        IPv4_src=None, IPv4_dst=None, TCP_src=None, TCP_dst=None, UDP_src=None, UDP_dst=None,
        SCTP_src=None, SCTP_dst=None, ICMPv4_type=None, ICMPv4_code=None, ARP_op=None, ARP_spa=None,
        ARP_tpa=None, ARP_sha=None, ARP_tha=None, IPv6_src=None, IPv6_dst=None,
        IPv6_flabel=None, ICMPv6_type=None, ICMPv6_code=None, IPv6_nd_target=None, IPv6_nd_ssl=None,
        IPv6_nd_tll =None, MPLS_label=None, MPLS_tc=None, MPLS_bos=None, PBB_is_id=None, tunnel_id =None,
        IPv6_txhdr=None):
        '''
        Constructor
        '''
        
        #Attributes from OFv1.3 matching fields
        self.in_port = in_port          # Switch input port.
        self.in_phy_port = in_phy_port      # Switch physical input port. 
        self.metadata = metadata        # Metadata passed between tables. 
        self.eth_dst = eth_dst          # Ethernet destination address.
        self.eth_src = eth_src          # Ethernet source address. 
        self.eth_type = eth_type        # Ethernet frame type. 
        self.vlan_vID = vlan_vID        # VLAN id. 
        self.vlan_PCP = vlan_PCP        # VLAN priority. 
        self.IP_dscp = IP_dscp          # IP DSCP (6 bits in ToS field). 
        self.IP_ecn = IP_ecn            # IP ECN (2 bits in ToS field). 
        self.IP_proto = IP_proto        # IP protocol. 
        self.IPv4_src = IPv4_src        # IPv4 source address. 
        self.IPv4_dst = IPv4_dst        # IPv4 destination address. 
        self.TCP_src = TCP_src          # TCP source port. 
        self.TCP_dst = TCP_dst          # TCP destination port. 
        self.UDP_src = UDP_src          # UDP source port. 
        self.UDP_dst = UDP_dst          # UDP destination port. 
        self.SCTP_src = SCTP_src        # SCTP source port. 
        self.SCTP_dst = SCTP_dst        # SCTP destination port. 
        self.ICMPv4_type = ICMPv4_type      # ICMP type. 
        self.ICMPv4_code = ICMPv4_code      # ICMP code. 
        self.ARP_op = ARP_op            # ARP opcode. 
        self.ARP_spa = ARP_spa          # ARP source IPv4 address. 
        self.ARP_tpa = ARP_tpa          # ARP target IPv4 address. 
        self.ARP_sha = ARP_sha          # ARP source hardware address. 
        self.ARP_tha = ARP_tha          # ARP target hardware address. 
        self.IPv6_src = IPv6_src        # IPv6 source address. 
        self.IPv6_dst = IPv6_dst        # IPv6 destination address. 
        self.IPv6_flabel = IPv6_flabel      # IPv6 Flow Label 
        self.ICMPv6_type = ICMPv6_type      # ICMPv6 type. 
        self.ICMPv6_code = ICMPv6_code      # ICMPv6 code. 
        self.IPv6_nd_target = IPv6_nd_target    # Target address for ND. 
        self.IPv6_nd_ssl = IPv6_nd_ssl      # Source link-layer for ND. 
        self.IPv6_nd_tll = IPv6_nd_tll      # Target link-layer for ND. 
        self.MPLS_label = MPLS_label        # MPLS label. 
        self.MPLS_tc = MPLS_tc          # MPLS TC. 
        self.MPLS_bos = MPLS_bos        # MPLS BoS bit. 
        self.PBB_is_id = PBB_is_id      # PBB I-SID. */
        self.tunnel_id = tunnel_id      # Logical Port Metadata. 
        self.IPv6_txhdr = IPv6_txhdr        # IPv6 Extension Header pseudo-field 

##########################################################################
########## DTService
##########################################################################
class DTService(object):
    '''
    classdocs
    '''

    def __init__(self, ID=None, in_port=None, in_phy_port=None, metadata=None, eth_dst=None, eth_src=None,
        eth_type=None, vlan_vID=None, vlan_PCP=None, IP_dscp=None, IP_ecn=None, IP_proto=None,
        IPv4_src=None, IPv4_dst=None, TCP_src=None, TCP_dst=None, UDP_src=None, UDP_dst=None,
        SCTP_src=None, SCTP_dst=None, ICMPv4_type=None, ICMPv4_code=None, ARP_op=None, ARP_spa=None,
        ARP_tpa=None, ARP_sha=None, ARP_tha=None, IPv6_src=None, IPv6_dst=None,
        IPv6_flabel=None, ICMPv6_type=None, ICMPv6_code=None, IPv6_nd_target=None, IPv6_nd_ssl=None,
        IPv6_nd_tll =None, MPLS_label=None, MPLS_tc=None, MPLS_bos=None, PBB_is_id=None, tunnel_id =None,
        IPv6_txhdr=None, ingress_core_node=None, egress_core_node=None,
        ingress_interface=None, egress_interface=None, name=None, color='RGB(0,0,0)', label=None, VPN_service_type=None):
        '''
        Constructor
        '''
        
        #Unique ID
        self.ID = ID

        #Attributes from OFv1.3 matching fields
        self.in_port = in_port          # Switch input port.
        self.in_phy_port = in_phy_port      # Switch physical input port. 
        self.metadata = metadata        # Metadata passed between tables. 
        self.eth_dst = eth_dst          # Ethernet destination address.
        self.eth_src = eth_src          # Ethernet source address. 
        self.eth_type = eth_type        # Ethernet frame type. 
        self.vlan_vID = vlan_vID        # VLAN id. 
        self.vlan_PCP = vlan_PCP        # VLAN priority. 
        self.IP_dscp = IP_dscp          # IP DSCP (6 bits in ToS field). 
        self.IP_ecn = IP_ecn            # IP ECN (2 bits in ToS field). 
        self.IP_proto = IP_proto        # IP protocol. 
        self.IPv4_src = IPv4_src        # IPv4 source address. 
        self.IPv4_dst = IPv4_dst        # IPv4 destination address. 
        self.TCP_src = TCP_src          # TCP source port. 
        self.TCP_dst = TCP_dst          # TCP destination port. 
        self.UDP_src = UDP_src          # UDP source port. 
        self.UDP_dst = UDP_dst          # UDP destination port. 
        self.SCTP_src = SCTP_src        # SCTP source port. 
        self.SCTP_dst = SCTP_dst        # SCTP destination port. 
        self.ICMPv4_type = ICMPv4_type      # ICMP type. 
        self.ICMPv4_code = ICMPv4_code      # ICMP code. 
        self.ARP_op = ARP_op            # ARP opcode. 
        self.ARP_spa = ARP_spa          # ARP source IPv4 address. 
        self.ARP_tpa = ARP_tpa          # ARP target IPv4 address. 
        self.ARP_sha = ARP_sha          # ARP source hardware address. 
        self.ARP_tha = ARP_tha          # ARP target hardware address. 
        self.IPv6_src = IPv6_src        # IPv6 source address. 
        self.IPv6_dst = IPv6_dst        # IPv6 destination address. 
        self.IPv6_flabel = IPv6_flabel      # IPv6 Flow Label 
        self.ICMPv6_type = ICMPv6_type      # ICMPv6 type. 
        self.ICMPv6_code = ICMPv6_code      # ICMPv6 code. 
        self.IPv6_nd_target = IPv6_nd_target    # Target address for ND. 
        self.IPv6_nd_ssl = IPv6_nd_ssl      # Source link-layer for ND. 
        self.IPv6_nd_tll = IPv6_nd_tll      # Target link-layer for ND. 
        self.MPLS_label = MPLS_label        # MPLS label. 
        self.MPLS_tc = MPLS_tc          # MPLS TC. 
        self.MPLS_bos = MPLS_bos        # MPLS BoS bit. 
        self.PBB_is_id = PBB_is_id      # PBB I-SID. */
        self.tunnel_id = tunnel_id      # Logical Port Metadata. 
        self.IPv6_txhdr = IPv6_txhdr        # IPv6 Extension Header pseudo-field 

        self.ingress_core_node = ingress_core_node #Ingress core node for specific service traffic
        self.egress_core_node = egress_core_node #Egress core node for specific service traffic
        self.ingress_interface = ingress_interface
        self.egress_interface = egress_interface
        self.name = name
        self.color = color
        self.label = label
        self.VPN_service_type = VPN_service_type

##########################################################################
########## DTServiceLSP
##########################################################################
class DTServiceLSP(object):
    '''
    classdocs
    '''

    def __init__(self, ID=None, lsps=None, color='RGB(0,0,0)', name=None):
        '''
        Constructor
        '''
        
        self.ID = ID
        self.color = color
        self.name = name
        self.lsps = lsps

##########################################################################
########## DTLSP
##########################################################################
class DTLSP(object):
    '''
    classdocs
    '''

    def __init__(self, links=None, mpls_labels_path=None, nodes_path=None, interfaces_path=None, metric=None, max_rate=None):
        '''
        Constructor
        '''
        
        self.metric = metric
        self.max_rate = max_rate
        
        self.mpls_labels_path = mpls_labels_path
        self.nodes_path = nodes_path
        self.interfaces_path = interfaces_path
        self.links = links

##########################################################################
########## DTLSPLink
##########################################################################
class DTLSPLink(object):
    '''
    classdocs
    '''

    def __init__(self, mpls_label=None, src_datapath_id=None, src_ovs_port=None, 
                    dst_datapath_id=None, dst_ovs_port=None):
        '''
        Constructor
        '''
        
        self.mpls_label = mpls_label
        self.src_datapath_id = src_datapath_id        
        self.src_ovs_port = src_ovs_port
        self.dst_datapath_id = dst_datapath_id
        self.dst_ovs_port = dst_ovs_port


##########################################################################
########## DTMPLSAction
##########################################################################\
##########################################################################
class DTMPLSAction(object):
    '''
    classdocs

    For action attribute we use the following conventions
    None -> Only forwarding none MPLS manipulation
    0 -> PUSH mpls label
    1 -> POP mpls label 
    2 -> SWAP mpls label

    '''

    def __init__(self, label=None, action=None):
        '''
        Constructor
        '''
        
        self.label = label
        self.action = action

    def __eq__(self, other):
        if isinstance(other, DTMPLSAction):
            return self.label == other.label and self.action == other.action 
        else:
            return NotImplemented
        
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def set_action_PUSH(self):
        self.action = 0
        
    def set_action_POP(self):
        self.action = 1
        
    def set_action_SWAP(self):
        self.action = 2

    def isPUSH(self):
        return self.action == 0
        
    def isPOP(self):
        return self.action == 1

    def isSWAP(self):
        return self.action == 2

    def actionToString(self):
        if self.isPUSH():
            return 'PUSH'
        elif self.isPOP():
            return 'POP'
        else:
            return 'SWAP'

##########################################################################
########## DTNHLFE
##########################################################################   
class DTNHLFE(object):
    '''
    classdocs
    '''

    def __init__(self, interface_ip_address, next_hop_ip_address, action):
        '''
        Constructor
        '''
        
        self.interface_ip_address = interface_ip_address
        self.next_hop_ip_address = next_hop_ip_address
        self.action = action

##########################################################################
########## DTFTN
##########################################################################   
class DTFTN(object):
    '''
    classdocs
    '''

    def __init__(self, service, nhlfes):
        '''
        Constructor
        '''
        
        self.service = service
        self.nhlfes = nhlfes

##########################################################################
########## DTILM
##########################################################################   
class DTILM(object):
    '''
    classdocs
    '''

    def __init__(self, label, nhlfes):
        '''
        Constructor
        '''
        
        self.label = label
        self.nhlfes = nhlfes

        
##########################################################################
########## DTNodeReduced
##########################################################################   
class DTNodeReduced(object):
    '''
    classdocs
    '''

    def __init__(self, router_id, name, top_type):
        '''
        Constructor
        '''
        
        self.router_id = router_id
        self.name = name
        self.top_type = top_type

##########################################################################
########## DTInterfaceReduced
##########################################################################   
class DTInterfaceReduced(object):
    '''
    classdocs
    '''

    def __init__(self, router_id=None, ip_address=None, i_type=None, ce_ip_address=None, ce_mac_address=None):
        '''
        Constructor
        '''
        
        self.router_id = router_id
        self.ip_address = ip_address
        self.type = i_type 

        self.ce_ip_address = ce_ip_address
        self.ce_mac_address = ce_mac_address   


        