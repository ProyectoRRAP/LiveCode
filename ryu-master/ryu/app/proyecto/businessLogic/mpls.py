'''
Created on March 05, 2015

@author: efviodo
'''

import uuid
from dataTypes import DTService

class LSP(object):
	'''
	classdocs
	'''

	def __init__(self, metric=-1, max_rate=-1, path=None):
		'''
		Constructor
		'''
        
		self.metric = metric
		self.max_rate = max_rate
        
		self.path = path

	def get_links_path(self):
		'''
		Return an ordered list of links with the lsp path across the network
		'''

		path = []
		for pe in self.path:
			path.append(pe.link)

		return path

class PathNode(object):
	'''
	classdocs
	'''

	def __init__(self, label=None, link=None, bandwidth=-1, ftn=None, ilm=None):

		self.label = label
		self.link = link
		self.bandwidth = bandwidth

		self.ftn = ftn
		self.ilm = ilm

class Service(object):
	'''
	classdocs
	'''

	def __init__(self, in_port=None, in_phy_port=None, metadata=None, eth_dst=None, eth_src=None,
				eth_type=None, vlan_vID=None, vlan_PCP=None, IP_dscp=None, IP_ecn=None, IP_proto=None,
				IPv4_src=None, IPv4_dst=None, TCP_src=None, TCP_dst=None, UDP_src=None, UDP_dst=None,
				SCTP_src=None, SCTP_dst=None, ICMPv4_type=None, ICMPv4_code=None, ARP_op=None, ARP_spa=None,
				ARP_tpa=None, ARP_sha=None, ARP_tha=None,  IPv6_src=None, IPv6_dst=None,
				IPv6_flabel=None, ICMPv6_type=None, ICMPv6_code=None, IPv6_nd_target=None, IPv6_nd_ssl=None,
				IPv6_nd_tll =None, MPLS_label=None, MPLS_tc=None, MPLS_bos=None, PBB_is_id=None, tunnel_id =None,
				IPv6_txhdr=None, label=None, VPN_service_type=None):
		'''
		Constructor
		'''
        
		#Attributes from OFv1.3 matching fields
		self.ID = str(uuid.uuid4()) 			# Unique ID 

		self.in_port = in_port	 		# Switch input port.
		self.in_phy_port = in_phy_port		# Switch physical input port. 
		self.metadata = metadata		# Metadata passed between tables. 
		self.eth_dst = eth_dst			# Ethernet destination address.
		self.eth_src = eth_src			# Ethernet source address. 
		self.eth_type = eth_type		# Ethernet frame type. 
		self.vlan_vID = vlan_vID 		# VLAN id. 
		self.vlan_PCP = vlan_PCP 		# VLAN priority. 
		self.IP_dscp = IP_dscp			# IP DSCP (6 bits in ToS field). 
		self.IP_ecn = IP_ecn 			# IP ECN (2 bits in ToS field). 
		self.IP_proto = IP_proto		# IP protocol. 
		self.IPv4_src = IPv4_src		# IPv4 source address. 
		self.IPv4_dst = IPv4_dst		# IPv4 destination address. 
		self.TCP_src = TCP_src			# TCP source port. 
		self.TCP_dst = TCP_dst			# TCP destination port. 
		self.UDP_src = UDP_src			# UDP source port. 
		self.UDP_dst = UDP_dst			# UDP destination port. 
		self.SCTP_src = SCTP_src		# SCTP source port. 
		self.SCTP_dst = SCTP_dst		# SCTP destination port. 
		self.ICMPv4_type = ICMPv4_type		# ICMP type. 
		self.ICMPv4_code = ICMPv4_code		# ICMP code. 
		self.ARP_op = ARP_op 			# ARP opcode. 
		self.ARP_spa = ARP_spa 			# ARP source IPv4 address. 
		self.ARP_tpa = ARP_tpa			# ARP target IPv4 address. 
		self.ARP_sha = ARP_sha 			# ARP source hardware address. 
		self.ARP_tha = ARP_tha 			# ARP target hardware address. 
		self.IPv6_src = IPv6_src		# IPv6 source address. 
		self.IPv6_dst = IPv6_dst		# IPv6 destination address. 
		self.IPv6_flabel = IPv6_flabel		# IPv6 Flow Label 
		self.ICMPv6_type = ICMPv6_type		# ICMPv6 type. 
		self.ICMPv6_code = ICMPv6_code		# ICMPv6 code. 
		self.IPv6_nd_target = IPv6_nd_target 	# Target address for ND. 
		self.IPv6_nd_ssl = IPv6_nd_ssl		# Source link-layer for ND. 
		self.IPv6_nd_tll = IPv6_nd_tll 		# Target link-layer for ND. 
		self.MPLS_label = MPLS_label		# MPLS label. 
		self.MPLS_tc = MPLS_tc 			# MPLS TC. 
		self.MPLS_bos = MPLS_bos		# MPLS BoS bit. 
		self.PBB_is_id = PBB_is_id 		# PBB I-SID. */
		self.tunnel_id = tunnel_id 		# Logical Port Metadata. 
		self.IPv6_txhdr = IPv6_txhdr 		# IPv6 Extension Header pseudo-field 

		self.ingress_node = None
		self.egress_node = None
		self.ingress_interface = None
		self.egress_interface = None
		
		self.label = label
		self.name = None
		self.color = 'RGB(0,0,0)'
		self.VPN_service_type = VPN_service_type

		self.labels = {} # In case VPN_service_type == 2 this attrobute has a dictionary of specific MPLS label for each ethertype
		self.lsps = []      

	def __eq__(self, other):
		if isinstance(other, Service):
			c = True
			c = c and self.in_port == other.in_port and self.in_phy_port == other.in_phy_port 
			c = c and self.metadata == other.metadata and self.eth_dst == other.eth_dst 
			c = c and self.eth_src == other.eth_src and self.eth_type == other.eth_type 
			c = c and self.vlan_vID == other.vlan_vID and self.vlan_PCP == other.vlan_PCP 
			c = c and self.IP_dscp == other.IP_dscp and self.IP_ecn == other.IP_ecn 
			c = c and self.IP_proto == other.IP_proto and self.IPv4_src == other.IPv4_src 
			c = c and self.IPv4_dst == other.IPv4_dst and self.TCP_src == other.TCP_src 
			c = c and self.TCP_dst == other.TCP_dst and self.UDP_src == other.UDP_src 
			c = c and self.UDP_dst == other.UDP_dst and self.SCTP_src == other.SCTP_src 
			c = c and self.SCTP_dst == other.SCTP_dst and self.ICMPv4_type == other.ICMPv4_type 
			c = c and self.ICMPv4_code == other.ICMPv4_code and self.ARP_op == other.ARP_op 
			c = c and self.ARP_spa == other.ARP_spa and self.ARP_tpa == other.ARP_tpa 
			c = c and self.ARP_sha == other.ARP_sha and self.ARP_tha == other.ARP_tha 
			c = c and self.IPv6_src == other.IPv6_src and self.IPv6_dst == other.IPv6_dst 
			c = c and self.IPv6_flabel == other.IPv6_flabel and self.ICMPv6_type == other.ICMPv6_type 
			c = c and self.ICMPv6_code == other.ICMPv6_code and self.IPv6_nd_target == other.IPv6_nd_target 
			c = c and self.IPv6_nd_ssl == other.IPv6_nd_ssl and self.IPv6_nd_tll == other.IPv6_nd_tll 
			c = c and self.MPLS_label == other.MPLS_label and self.MPLS_tc == other.MPLS_tc 
			c = c and self.MPLS_bos == other.MPLS_bos and self.PBB_is_id == other.PBB_is_id 
			c = c and self.tunnel_id == other.tunnel_id and self.IPv6_txhdr == other.IPv6_txhdr 	
			c = c and self.label == other.label 
			c = c and self.VPN_service_type == other.VPN_service_type
			return c
		else:
			return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result

	def To_DTService(self):
		'''
		'''

		data = DTService(ID=self.ID, in_port=self.in_port, in_phy_port=self.in_phy_port, metadata=self.metadata, 
							eth_dst=self.eth_dst, eth_src=self.eth_src,
       						eth_type=self.eth_type, vlan_vID=self.vlan_vID, vlan_PCP=self.vlan_PCP, 
       						IP_dscp=self.IP_dscp, IP_ecn=self.IP_ecn, IP_proto=self.IP_proto,
        					IPv4_src=self.IPv4_src, IPv4_dst=self.IPv4_dst, TCP_src=self.TCP_src, 
        					TCP_dst=self.TCP_dst, UDP_src=self.UDP_src, UDP_dst=self.UDP_dst,
        					SCTP_src=self.SCTP_src, SCTP_dst=self.SCTP_dst, ICMPv4_type=self.ICMPv4_type,
        					ICMPv4_code=self.ICMPv4_code, ARP_op=self.ARP_op, ARP_spa=self.ARP_spa,
        					ARP_tpa=self.ARP_tpa, ARP_sha=self.ARP_sha, ARP_tha=self.ARP_tha, 
        					IPv6_src=self.IPv6_src, IPv6_dst=self.IPv6_dst,
        					IPv6_flabel=self.IPv6_flabel, ICMPv6_type=self.ICMPv6_type, ICMPv6_code=self.ICMPv6_code,
        					IPv6_nd_target=self.IPv6_nd_target, IPv6_nd_ssl=self.IPv6_nd_ssl,
        					IPv6_nd_tll =self.IPv6_nd_tll, MPLS_label=self.MPLS_label, MPLS_tc=self.MPLS_tc, 
        					MPLS_bos=self.MPLS_bos, PBB_is_id=self.PBB_is_id, tunnel_id =self.tunnel_id,
        					IPv6_txhdr=self.IPv6_txhdr, 
        					ingress_core_node=self.ingress_node.router_id, 
        					egress_core_node=self.egress_node.router_id,
        					ingress_interface=self.ingress_interface.ovs_port, 
        					egress_interface=self.egress_interface.ovs_port, 
        					name=self.name, 
        					color=self.color,
        					label=self.label,
        					VPN_service_type=self.VPN_service_type
        				)
		return data
