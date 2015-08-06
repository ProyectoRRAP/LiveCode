'''
Created on Feb 22, 2015

@author: efviodo
'''

class DTFEC(object):
    '''
    classdocs
    '''

    def __init__(self, port_in=None, ethernet_src=None, ethernet_dst=None, dltype=None, 
                 VLANid=None, VLAN_priority=None, IPv4_src=None, IPv4_dst=None, 
                 TCP_src_port=None, TCP_dst_port=None, UDP_src_port=None, UDP_dst_port=None, 
                      ICMP_type, ICMP_code, MPLS_label, MPLS_tc, MPLS_bos):
        '''
        Constructor
        '''
        
        self.port_in         = port_in
        self.ethernet_src     = ethernet_src
        self.ethernet_dst     = ethernet_dst
        self.dltype         = dltype
        self.VLANid         = VLANid
        self.VLAN_priority     = VLAN_priority
        self.IPv4_src         = IPv4_src
        self.IPv4_dst         = IPv4_dst
        self.TCP_src_port     = TCP_src_port
        self.TCP_dst_port     = TCP_dst_port
        self.UDP_src_port     = UDP_src_port
        self.UDP_dst_port     = UDP_dst_port
        self.ICMP_type         = ICMP_type
        self.ICMP_code         = ICMP_code
        self.MPLS_label     = MPLS_label
        self.MPLS_tc         = MPLS_tc
        self.MPLS_bos         = MPLS_bos

    
        