'''
Created on March 11, 2015

@author: efviodo
'''

import ryu.lib.ofctl_v1_3
import util
from ipv4 import ipv4_text_to_int, nw_addr_aton, mask_ntob

def install_ingress_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in, action, path_len):
    '''
    A diferencia de install_node_flow_service esta instala un flujo exatra para poner etiqueta de segundo
    nivel en el nodo de ingreso utilizando dos tablas en el dispositivo para ello
    '''

    #print 'Servicio (' + service.ingress_node.router_id + ', '+ service.egress_node.router_id + ')'
    print 'Instala flujos en nodos de borde'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'accion'
    print action
    print 'label in'
    print label_in

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        table_id_1 = 0
        table_id_2 = 1
        table_id_3 = 2

        # If traffic is over IP then decrement TTL
        if service.VPN_service_type == 2: 

            # Para cada etherype del servicio instala un flujo para poner la etieueta mpls
            for eth, l in service.labels.iteritems():

                match = get_of_match_field(ofparser=parser, s=service)

                #Set port in
                if ovs_port_in is not None:
                    match.set_in_port(int(ovs_port_in))

                match.set_dl_type(int(eth,16))

                #Specify actions
                actions = []

                actions.append(parser.OFPActionPushMpls(0x8847))
                actions.append(parser.OFPActionSetField(mpls_label=int(l, 16)))
                actions.append(parser.OFPActionSetMplsTtl(128))

                if path_len == 1:
                    if ovs_port_out is not None:
                        actions.append(parser.OFPActionOutput(int(ovs_port_out)))
                       
                    add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_1)
                else:

                    inst = [parser.OFPInstructionGotoTable(table_id_2)]
                    add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_1, inst=inst)


                    # ----- Built Second Flow --> Flow asociated to Copy TTL from IP to MPLS header and second label level PUSH
                    match = parser.OFPMatch()
                    match.set_dl_type(0x8847)

                    if ovs_port_in is not None:
                        match.set_in_port(int(ovs_port_in))
                    
                    match.set_mpls_label(int(l, 16))
                    actions = []
                                   
                    #Specify MPLS label manipulation
                    if action is not None:
                        if action.isPUSH():
                            actions.append(parser.OFPActionPushMpls(0x8847))
                            actions.append(parser.OFPActionSetField(mpls_label=int(action.label, 16)))
                            actions.append(parser.OFPActionSetMplsTtl(128))

                    if ovs_port_out is not None:
                        actions.append(parser.OFPActionOutput(int(ovs_port_out)))

                    add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_2)
        else:

            # --------- Built First Flow --> Push Service Label and for LSP/Len==1 Forwarding Rule
            match = get_of_match_field(ofparser=parser, s=service)

            #Set port in
            if ovs_port_in is not None:
                match.set_in_port(int(ovs_port_in))
            
            #En LER Lanel in es none sacar!
            if label_in is not None:
                match.set_mpls_label(int(label_in, 16))

            #Specify actions
            actions = []

            if service.eth_type == '0x0800':
                #Decrement IPv4 TTL
                actions.append(parser.OFPActionDecNwTtl())

            #PUSH MPLS header
            actions.append(parser.OFPActionPushMpls(0x8847))
            actions.append(parser.OFPActionSetField(mpls_label=int(service.label, 16)))
            actions.append(parser.OFPActionSetMplsTtl(128))

            #If PathLength = 1 then only one flow, othercase we have two flows, service  abel push and forwarding label push
            if path_len == 1:
                if ovs_port_out is not None:
                    actions.append(parser.OFPActionOutput(int(ovs_port_out)))
                   
                add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_1)

            else:
                inst = [parser.OFPInstructionGotoTable(table_id_2)]
                add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_1, inst=inst)

                # ----- Built Second Flow --> Flow asociated to Copy TTL from IP to MPLS header and second label level PUSH

                match = parser.OFPMatch()
                match.set_dl_type(0x8847)

                if ovs_port_in is not None:
                    match.set_in_port(int(ovs_port_in))
                
                match.set_mpls_label(int(service.label, 16))

                actions = []
            
                #if service.eth_type == '0x0800':
                    #Copy TTL from IPv4 header to MPLS header
                    #actions.append(parser.OFPActionCopyTtlOut())

               
                #Specify MPLS label manipulation
                if action is not None:
                    if action.isPUSH():
                        actions.append(parser.OFPActionPushMpls(0x8847))
                        actions.append(parser.OFPActionSetField(mpls_label=int(action.label, 16)))
                        actions.append(parser.OFPActionSetMplsTtl(128))
                    elif action.isPOP():
                        match.set_dl_type(0x8847)
                        actions.append(parser.OFPActionPopMpls(0x8847))
                    else:
                        actions.append(parser.OFPActionSetField(mpls_label=int(action.label, 16)))

                if ovs_port_out is not None:
                    actions.append(parser.OFPActionOutput(int(ovs_port_out)))

                #inst = [parser.OFPInstructionGotoTable(table_id_3)]

                add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_2)

            # ----- Built Third Flow --> Flow asociated to forwarding Rule
            #match = parser.OFPMatch()
            #match.set_dl_type(0x8847)

            #f ovs_port_in is not None:
            #    match.set_in_port(int(ovs_port_in))
            
            #match.set_mpls_label(int(action.label, 16))

            #actions = []
            #actions.append(parser.OFPActionDecMplsTtl())

            #Specify forwarding 
            #if ovs_port_out is not None:
            #    actions.append(parser.OFPActionOutput(int(ovs_port_out)))

            #add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=table_id_3)

def install_egress_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in, action, interface=None):
    '''

    '''
    print 'Install node egress flow'

    print 'Instala flujos en nodos de borde'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'accion'
    print action
    print 'label in'
    print label_in

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Built OF match field
        #match = get_of_match_field(ofparser=parser, s=service
    
        if service.VPN_service_type == 2:

            # Para cada etherype del servicio instala un flujo para poner la etieueta mpls
            for eth, l in service.labels.iteritems():

                match = parser.OFPMatch()

                #Modify specific match fields
                if ovs_port_in is not None:
                    match.set_in_port(int(ovs_port_in))
                
                match.set_dl_type(0x8847)
                match.set_mpls_bos(1)

                #Specify actions
                actions = []

                if label_in is not None:
                    match.set_mpls_label(int(l, 16))

                if action is not None:
                    if action.isPOP():
                        match.set_dl_type(0x8847)
                        actions.append(parser.OFPActionPopMpls(util.string_to_hexa(eth)))
                    
                #Specify forwarding 
                if ovs_port_out is not None:
                    actions.append(parser.OFPActionOutput(int(ovs_port_out)))

                inst = []
                add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=0)
        else:

            match = parser.OFPMatch()

            #Modify specific match fields
            if ovs_port_in is not None:
                match.set_in_port(int(ovs_port_in))
            
            match.set_dl_type(0x8847)
            match.set_mpls_bos(1)

            #Specify actions
            actions = []

            if label_in is not None:
                match.set_mpls_label(int(label_in, 16))

            #Specify MPLS label manipulation
            if action is not None:
                if action.isPOP():
                    match.set_dl_type(0x8847)
                    actions.append(parser.OFPActionPopMpls(util.string_to_hexa(service.eth_type)))
                
            #Specify forwarding 
            actions.append(parser.OFPActionSetField(eth_dst=interface.ce_mac_address))
            
            if ovs_port_out is not None:
                actions.append(parser.OFPActionOutput(int(ovs_port_out)))

            #actions.append(parser.OFPActionOutput(ofproto.OFPP_NORMAL, 0))
           
            inst = []
            add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=0)

def install_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in, action):
    '''

    '''

    #print 'Servicio (' + service.ingress_node.router_id + ', '+ service.egress_node.router_id + ')'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'accion'
    print action
    print 'label in'
    print label_in

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Built OF match field
        #match = get_of_match_field(ofparser=parser, s=service)
        match = parser.OFPMatch()

        #Modify specific match fields
        if ovs_port_in is not None:
            match.set_in_port(int(ovs_port_in))
        
        if label_in is not None:
            match.set_mpls_label(int(label_in, 16))
        
        match.set_dl_type(0x8847)

        match.set_mpls_bos(0)

        #Specify actions
        actions = []
    
        #Specify MPLS label manipulation
        if action is not None:
            if action.isPUSH():
                actions.append(parser.OFPActionPushMpls(0x8847))
                actions.append(parser.OFPActionSetField(mpls_label=int(action.label, 16)))
            elif action.isPOP():
                match.set_dl_type(0x8847)
                actions.append(parser.OFPActionPopMpls(0x8847))
            else:
                actions.append(parser.OFPActionSetField(mpls_label=int(action.label, 16)))
                actions.append(parser.OFPActionDecMplsTtl())
            
        #Specify forwarding 
        if ovs_port_out is not None:
            actions.append(parser.OFPActionOutput(int(ovs_port_out)))
            print 'accion de salida'

        inst = []
    
        add_flow(datapath=datapath, priority=0, match=match, actions=actions, tableid=0)

def remove_egress_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in):
    '''
    docs
    '''

    print 'Remueve flujo en nodo de borde'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'service label'
    print service.label

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        table_id = 0

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if service.VPN_service_type == 2:

            # Para cada etherype del servicio instala un flujo para poner la etieueta mpls
            for eth, l in service.labels.iteritems():
                match = parser.OFPMatch()

                print 'entro papa'
                #Modify specific match fieldsinstall_node_flow_for_service
                if ovs_port_in is not None:
                    match.set_in_port(int(ovs_port_in))

                if label_in is not None:
                    match.set_mpls_label(int(l, 16))

                match.set_dl_type(0x8847)
                match.set_mpls_bos(1)

                del_flow(datapath=datapath, tableid=table_id, match=match)
        else:
            #### Remove First Flow asociated to PUSH service inner label 
            #Built OF match field
            match = parser.OFPMatch()

            #Modify specific match fieldsinstall_node_flow_for_service
            if ovs_port_in is not None:
                match.set_in_port(int(ovs_port_in))

            if label_in is not None:
                match.set_mpls_label(int(label_in, 16))

            match.set_dl_type(0x8847)
            match.set_mpls_bos(1)

            del_flow(datapath=datapath, tableid=table_id, match=match)


def remove_ingress_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in, path_len):
    '''
    docs
    '''

    print 'Remueve flujo de entrada'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'service label'
    print service.label

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        table_id = 0
        next_table_id = 1

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if service.VPN_service_type == 2:
             # Para cada etherype del servicio instala un flujo para poner la etieueta mpls
            for eth, l in service.labels.iteritems():

                match = get_of_match_field(parser, service)
                match.set_dl_type(int(eth,16))

                #Modify specific match fieldsinstall_node_flow_for_service
                if ovs_port_in is not None:
                    match.set_in_port(int(ovs_port_in))

                del_flow(datapath=datapath, tableid=table_id, match=match)

                if path_len > 1:

                    #### Remove Second Flow asociated to PUSH forwarding outer label
                    match2 = parser.OFPMatch()
                    match2.set_dl_type(0x8847)

                    if ovs_port_in is not None:
                        match2.set_in_port(int(ovs_port_in))
                    
                    match.set_mpls_label(int(l, 16))

                    del_flow(datapath=datapath, tableid=next_table_id, match=match2)

        else:

            #### Remove First Flow asociated to PUSH service inner label 
            #Built OF match field
            match = get_of_match_field(parser, service)

            #Modify specific match fieldsinstall_node_flow_for_service
            if ovs_port_in is not None:
                match.set_in_port(int(ovs_port_in))

            del_flow(datapath=datapath, tableid=table_id, match=match)

            if path_len > 1:

                #### Remove Second Flow asociated to PUSH forwarding outer label
                match2 = parser.OFPMatch()
                match2.set_dl_type(0x8847)

                if ovs_port_in is not None:
                    match2.set_in_port(int(ovs_port_in))
                
                match.set_mpls_label(int(service.label, 16))

                del_flow(datapath=datapath, tableid=next_table_id, match=match2)

def remove_node_flow_for_service(service, node, ovs_port_in, ovs_port_out, label_in):
    '''
    docs
    '''

    print 'Remueve flujo en nodo de core'
    print 'Puerto entrada ' +  str(ovs_port_in)
    print 'Puerto salida ' + str(ovs_port_out)
    print 'Node ' + node.router_id

    print 'label in'
    print label_in

    #Check if node is OF type and the state is OF functional
    if node.net_type == 1 and node.of_ready:

        #Get access to node datapath
        datapath = node.datapath

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Built OF match field
        #match = get_of_match_field(parser, service)
        match = parser.OFPMatch()

        match.set_dl_type(0x8847)

        match.set_mpls_bos(0)
        
        #Modify specific match fieldsinstall_node_flow_for_service
        if ovs_port_in is not None:
            match.set_in_port(int(ovs_port_in))
        
        if label_in is not None:
            match.set_mpls_label(int(label_in, 16))

        #Specify actions
        #actions = []

        #Specify forwarding 
        #actions.append(parser.OFPActionOutput(ovs_port_out))
    
        #Specify MPLS label manipulation
        #if action is not None:
         #   if action.isPUSH():
         #       actions.append(parser.OFPActionPushMpls(0x8847))
         #       actions.append(parser.OFPActionSetField(mpls_label=action.label))
         #   elif action.isPOP():
         #       actions.append(parser.OFPActionPopMpls(0x8847))
         #   else:
         #       actions.append(parser.OFPActionSetField(mpls_label=action.label))

        #inst = []
    
        del_flow(datapath=datapath, tableid=0, match=match)

def get_of_match_field(ofparser, s):
    '''
    Creates OF macth field from service openflow section
    '''
    
    match = ofparser.OFPMatch()

    if s.in_port is not None:
        match.set_in_port(s.in_port)

    if s.in_phy_port is not None:
        match.set_in_phy_port(s.in_phy_port)

    if s.metadata is not None:
        match.set_metadata(s.metadata)

    if s.eth_dst is not None:
        match.set_dl_dst(s.eth_dst)

    if s.eth_src is not None:
        match.set_dl_src(s.eth_src)

    if s.eth_type is not None:
        match.set_dl_type(util.string_to_hexa(s.eth_type))

    if s.vlan_vID is not None:
        match.set_vlan_vid(int(s.vlan_vID, 16))

    if s.vlan_PCP is not None:
        match.set_vlan_pcp(int(s.vlan_PCP, 16))

    if s.IP_dscp is not None:
        match.set_ip_dscp(s.IP_dscp)

    if s.IP_ecn is not None:
        match.set_ip_ecn(s.IP_ecn)

    if s.IP_proto is not None:
        match.set_ip_proto(int(s.IP_proto, 16))

    if s.IPv4_src is not None:
        print 'Parsea direccion IP'
        ip_src, ip_mask_src = stringToIPAddress(s.IPv4_src)
        match.set_ipv4_src_masked(ip_src, ip_mask_src)
        #match.set_ipv4_src(ip_src)
        print ip_src
        print ip_mask_src

    if s.IPv4_dst is not None:
        ip_dst, ip_mask_dst = stringToIPAddress(s.IPv4_dst)
        match.set_ipv4_dst_masked(ip_dst, ip_mask_dst)
        #match.set_ipv4_dst(s.IPv4_dst)

    if s.TCP_src is not None:
        match.set_tcp_src(int(s.TCP_src))

    if s.TCP_dst is not None:
        match.set_tcp_dst(int(s.TCP_dst))

    if s.UDP_src is not None:
        match.set_udp_src(int(s.UDP_src))

    if s.UDP_dst is not None:
        match.set_udp_dst(int(s.UDP_dst))

    if s.SCTP_src is not None:
        match.set_sctp_src(s.SCTP_src)

    if s.SCTP_dst is not None:
        match.set_sctp_dst(s.SCTP_dst)

    if s.ICMPv4_type is not None:
        match.set_icmpv4_type(s.ICMPv4_type)

    if s.ICMPv4_code is not None:
        match.set_icmpv4_code(s.ICMPv4_code)

    if s.ARP_op is not None:
        match.set_arp_opcode(s.ARP_op)

    if s.ARP_spa is not None:
        #match.set_arp_spa(s.ARP_spa)
        arp_spa, arp_mask_src = stringToIPAddress(s.ARP_spa)
        match.set_arp_spa_masked(arp_spa, arp_mask_src)

    if s.ARP_tpa is not None:
        #match.set_arp_tpa(s.ARP_tpa)
        arp_tpa, arp_mask_dst = stringToIPAddress(s.ARP_tpa)
        match.set_arp_tpa_masked(arp_tpa, arp_mask_dst)

    if s.ARP_sha is not None:
        match.set_arp_sha(s.ARP_sha)

    if s.ARP_tha is not None:
        match.set_arp_tha(s.ARP_tha)

    if s.IPv6_src is not None:
        match.set_ipv6_src(s.IPv6_src)

    if s.IPv6_dst is not None:
        match.set_ipv6_dst(s.IPv6_dst)

    if s.IPv6_flabel is not None:
        match.set_ipv6_flabel(s.IPv6_flabel)

    if s.ICMPv6_type is not None:
        match.set_icmpv6_type(s.ICMPv6_type)

    if s.ICMPv6_code is not None:
        match.set_icmpv6_code(s.ICMPv6_code)
   
    if s.IPv6_nd_target is not None:
        match.set_ipv6_nd_target(s.IPv6_nd_target)

    if s.IPv6_nd_ssl is not None:
        match.set_ipv6_nd_sll(s.IPv6_nd_ssl)

    if s.IPv6_nd_tll is not None:
        match.set_ipv6_nd_tll(s.IPv6_nd_tll)

    if s.MPLS_label is not None:
        match.set_mpls_label(s.MPLS_label)

    if s.MPLS_tc is not None:
        match.set_mpls_tc(s.MPLS_tc)

    if s.MPLS_bos is not None:
        match.set_mpls_bos(s.MPLS_bos)

    if s.PBB_is_id is not None:
        match.set_pbb_isid(s.PBB_is_id)

    if s.tunnel_id is not None:
        match.set_tunnel_id(s.tunnel_id)

    if s.IPv6_txhdr is not None:
        match.set_ipv6_exthdr(s.IPv6_txhdr)

    return match 

def stringToIPAddress(ip_address):
    '''
    Recives an ip address string with format like "xxx.xxx.xxx.xxx/xx" and returns an IP Address
    '''

    #Get network address, mask and default gateway from IP address
    nw_addr, mask, default_gw = nw_addr_aton(ip_address)

    #Converts network address to ipv4 int address
    ip_int = ipv4_text_to_int(nw_addr)
        
    return ip_int, mask_ntob(mask)

#######################################################
####### FLOW primitives
####################################################### 
def add_flow(datapath, priority, match, actions, tableid=0, inst=[], buffer_id=None):
    print 'Add Flow to datapath'
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
 
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                 actions)] + inst
    if buffer_id:
        mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                        priority=priority, match=match,
                        instructions=inst, command=ofproto.OFPFC_ADD)
    else:
        print 'Flow sin buffer'
        mod = parser.OFPFlowMod(datapath=datapath, cookie=0, cookie_mask=0, table_id=tableid, command=ofproto.OFPFC_ADD,
                        idle_timeout=0, hard_timeout=0, priority=5, 
                        flags=0, match=match, instructions=inst, out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY)

    #flags=ofproto.OFPFF_CHECK_OVERLAP  

    datapath.send_msg(mod)        
     
def del_flow(datapath, match, priority=0, tableid=0, buffer_id=None):
    print 'Remove Flow from datapath'
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
 
    if buffer_id:
        mod = parser.OFPFlowMod(datapath=datapath, cookie=0, cookie_mask=0, table_id=tableid, command=ofproto.OFPFC_DELETE,
                        idle_timeout=0, hard_timeout=0, buffer_id=buffer_id, out_port=ofproto.OFPP_ANY, 
                        out_group=ofproto.OFPG_ANY, flags=0, match=match, instructions=[])
    else:
        mod = parser.OFPFlowMod(datapath=datapath, cookie=0, cookie_mask=0, table_id=tableid, command=ofproto.OFPFC_DELETE,
                        idle_timeout=0, hard_timeout=0, buffer_id=ofproto.OFPCML_NO_BUFFER, out_port=ofproto.OFPP_ANY, 
                        out_group=ofproto.OFPG_ANY, flags=0, match=match, instructions=[])
 
    datapath.send_msg(mod)

def send_table_stats_request2(datapath):
    '''
    '''
    print 'Envia table stats request'
    ofp = datapath.ofproto
    ofp_parser = datapath.ofproto_parser

    cookie = cookie_mask = 0
    match = ofp_parser.OFPMatch()
    #req = ofp_parser.OFPTableStatsRequest(datapath)
    req = ofp_parser.OFPAggregateStatsRequest(datapath,  0,
                                                      ofp.OFPTT_ALL,
                                                      ofp.OFPP_ANY,
                                                      ofp.OFPG_ANY,
                                                      cookie, cookie_mask,
                                                      match)
    datapath.send_msg(req)

def send_table_stats_request(datapath, waiters):
    return ofctl_v1_3.get_flow_stats(datapath, waiters)