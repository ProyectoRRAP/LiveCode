'''
Created on Feb 27, 2015

@author: efviodo
'''

from ryu.base import app_manager

from dataTypes import DTNode, DTInterface, DTLink, DTFEC, DTLSNode, DTLSInterface, DTLSLink, DTService, DTNodeReduced, DTInterfaceReduced
from patterns import Singleton
import json


def listOfNodesToJSON(nodes):
    print 'Convierte a JSON una lista de nodos'
    
    nodes_json = []
    for n in nodes:
        #Convierte a JSON cada interfaz
        interfaces_json = []

        #First order list of interfaces
        ifaces = n.interfaces.keys()
        ifaces.sort()

        for ikey in ifaces:
        #for i in n.interfaces.itervalues():  

            i = n.interfaces[ikey]
            links_json = []
            for l in i.links.itervalues():
                links_json.append({'status': l.status, 'from_node_int': l.from_node_int.ip_address, 
                                    'to_node_int': l.to_node_int.ip_address, 'weight': str(l.weight)})

            interfaces_json.append({'ip_address':i.ip_address, 'mac_address': i.mac_address, 
                    'ovs_port': i.ovs_port, 'type': i.type, 'links': links_json, 'status': i.status, 'name': i.name, 
                    'ce_ip_address': i.ce_ip_address, 'ce_mac_address': i.ce_mac_address})
        
        nodes_json.append({'name': n.name, 'router_id': n.router_id, 'datapath_id': n.datapath_id, 
                             'status': n.status, 'net_type': n.net_type, 'top_type': n.top_type, 
                             'of_ready': n.of_ready, 'ls_ready': n.ls_ready, 
                             'description': n.description, 'interfaces': interfaces_json})

    return json.dumps(nodes_json, indent=2)

def listOfServicesToJSON(servs):
    servs_json = []
    for s in servs:

        servs_json.append({'in_port': s.in_port, 'in_phy_port': s.in_phy_port, 'metadata': s.metadata,
                            'eth_dst': s.eth_dst, 'eth_src': s.eth_src, 'eth_type': s.eth_type, 
                            'vlan_vID': s.vlan_vID, 'vlan_PCP': s.vlan_PCP, 'IP_dscp': s.IP_dscp, 
                            'IP_ecn': s.IP_ecn, 'IP_proto': s.IP_proto, 'IPv4_src': s.IPv4_src, 
                            'IPv4_dst': s.IPv4_dst, 'TCP_src': s.TCP_src, 'TCP_dst': s.TCP_dst, 
                            'UDP_src': s.UDP_src, 'UDP_dst': s.UDP_dst, 'SCTP_src': s.SCTP_src, 
                            'SCTP_dst': s.SCTP_dst, 'ICMPv4_type': s.ICMPv4_type, 'ICMPv4_code': s.ICMPv4_code, 
                            'ARP_op': s.ARP_op, 'ARP_spa': s.ARP_spa, 'ARP_tpa': s.ARP_tpa, 
                            'ARP_sha': s.ARP_sha, 'ARP_tha': s.ARP_tha, 'IPv6_src': s.IPv6_src, 
                            'IPv6_src': s.IPv6_src, 'IPv6_dst': s.IPv6_dst, 'IPv6_flabel': s.IPv6_flabel, 
                            'ICMPv6_type': s.ICMPv6_type, 'ICMPv6_code': s.ICMPv6_code, 
                            'IPv6_nd_target': s.IPv6_nd_target, 'IPv6_nd_ssl': s.IPv6_nd_ssl,
                            'IPv6_nd_tll': s.IPv6_nd_tll, 'MPLS_label': s.MPLS_label, 'MPLS_tc': s.MPLS_tc, 
                            'MPLS_bos': s.MPLS_bos, 'PBB_is_id': s.PBB_is_id, 'tunnel_id': s.tunnel_id, 
                            'IPv6_txhdr': s.IPv6_txhdr, 'ingress_node': s.ingress_core_node, 
                            'egress_node': s.egress_core_node, 'ID': str(s.ID), 'ingress_interface': s.ingress_interface,
                            'egress_interface': s.egress_interface, 'service_name': s.name, 'service_color': s.color, 
                            'service_label': s.label, 'VPN_service_type': s.VPN_service_type})
    
    return json.dumps(servs_json, indent=2)

def listOfServicesLSPsToJSON(servs):
    servs_lsps_json = []
    
    for s in servs:
       
        lsps_json = []
        for lsp in s.lsps:

            links = []
            for l in lsp.links:
          
                links.append({'mpls_label': l.mpls_label, 'src_datapath_id': l.src_datapath_id, 
                                'src_ovs_port': l.src_ovs_port, 'dst_datapath_id': l.dst_datapath_id,
                                 'dst_ovs_port': l.dst_ovs_port,})

            lsps_json.append({'links': links})

        servs_lsps_json.append({'ID': s.ID, 'lsps': lsps_json, 'color': s.color, 'name': s.name})

    return json.dumps(servs_lsps_json, indent=2)

def listOfServicesLSPsToJSON2(lsps):
    servs_lsps_json = []

    for l in lsps:
       
        labels = l.mpls_labels_path
        nodes = l.nodes_path
        interfaces = l.interfaces_path

        servs_lsps_json.append({'metric': l.metric, 'max_rate': l.max_rate, 
                                'mpls_labels': labels, 'nodes': nodes, 'interfaces': interfaces})
    
    return json.dumps(servs_lsps_json, indent=2)

def listOfNHLEToJSON(nhlfes):
    nhlfe_json = []

    for nhlfe in nhlfes:
        
        action = None
        label = None
        if nhlfe.action is not None:
            action = nhlfe.action.actionToString()
            label = nhlfe.action.label

        nhlfe_json.append({'intreface': nhlfe.interface_ip_address, 'next_hop': nhlfe.next_hop_ip_address, 
                                'action': {'label': label, 'action': action}})
    
    return json.dumps(nhlfe_json, indent=2)

def listOfFTNJSON(ftns):
   
    ftn_json = []

    for ftn in ftns:
        nhlfe_json = []
        for nhlfe in ftn.nhlfes:
            
            action = None
            label = None
            if nhlfe.action is not None:
                action = nhlfe.action.actionToString()
                label = nhlfe.action.label

            nhlfe_json.append({'intreface': nhlfe.interface_ip_address, 'next_hop': nhlfe.next_hop_ip_address, 
                                    'action': {'label': label, 'action': action}})
        service = { 'ingress_node': ftn.service.ingress_core_node,
                    'egress_node': ftn.service.egress_core_node,
                    'ingress_interface': ftn.service.ingress_interface,
                    'egress_interface': ftn.service.egress_interface,
                    'name': ftn.service.name, 
                    'color': ftn.service.color
                }
        ftn_json.append({'service': service, 'nhlfes': nhlfe_json})

    return json.dumps(ftn_json, indent=2)

def listOfILMJSON(ilms):
   
    ilms_json = []

    for ilm in ilms:
        nhlfe_json = []
        for nhlfe in ilm.nhlfes:
            
            action = None
            label = None
            if nhlfe.action is not None:
                action = nhlfe.action.actionToString()
                label = nhlfe.action.label

            nhlfe_json.append({'intreface': nhlfe.interface_ip_address, 'next_hop': nhlfe.next_hop_ip_address, 
                                    'action': {'label': label, 'action': action}})
        ilms_json.append({'label': ilm.label, 'nhlfes': nhlfe_json})

    return json.dumps(ilms_json, indent=2)

def JSONToListOfNodes(data_nodes):
    list_nodes = json.loads(data_nodes)

    nodes = {}
   
    #Creates Nodes
    for n in list_nodes:
        router_id = n['router_id']
        interfaces = {}
        
        node = DTLSNode(router_id=router_id, status=1)

        for i in n['interfaces']:
            ip_address = i['ip_address']

            interface = DTLSInterface(node=node, ip_address=ip_address, status=1)
            interfaces[ip_address] = interface

        node.interfaces = interfaces
        nodes[router_id] = node

    #Add links between nodes
    for n in list_nodes:
        router_id = n['router_id']
        for i in n['interfaces']:
            ip_address = i['ip_address']
            links = {}
            for l in i['links']:
                from_node_int = l['from_node_int']
                weight = l['weight']
                to_node_int = l['to_node_int']
                to_node_router_id = l['to_node_router_id']

                from_node = nodes[router_id].interfaces[from_node_int]
                to_node = nodes[to_node_router_id].interfaces[to_node_int]

                link = DTLSLink(from_node_int=from_node, to_node_int=to_node, weight=weight)
                links[to_node_int] = link

            nodes[router_id].interfaces[ip_address].links = links
                

    return nodes

def JSONToDTService(service):
    '''
    '''

    data = json.loads(service)

    print data 

    ID = data['ID']
    name = data['service_name']
    color = data['service_color']
    ingress_node = data['ingress_node']
    egress_node = data['egress_node']
    ingress_interface = data['ingress_interface']
    egress_interface = data['egress_interface']

    eth_src = str(data['eth_src'])
    eth_dst = str(data['eth_dst'])
    eth_type = str(data['eth_type'])
    vlan_vID = data['vlan_vID']
    vlan_PCP = data['vlanPCP']
    ARP_spa = data['ARP_spa']
    ARP_tpa = data['ARP_tpa']
    IPv4_src = data['IPv4_src']
    IPv4_dst = data['IPv4_dst']
    IPv6_src = data['IPv6_src']
    IPv6_dst = data['IPv6_dst']
    ICMPv4_type = data['ICMPv4_type']
    ICMPv4_code = data['ICMPv4_code']
    ICMPv6_type = data['ICMPv6_type']
    ICMPv6_code = data['ICMPv6_code']
    TCP_src = data['TCP_src']
    TCP_dst = data['TCP_dst']
    UDP_src = data['UDP_src']
    UDP_dst = data['UDP_dst']
    SCTP_src = data['SCTP_src']
    SCTP_dst = data['SCTP_dst']
    IP_proto = data['IP_proto']
    VPN_service_type = data['VPN_service_type']

    #For each attribute convert emptys string to None values
    if eth_src == '' or eth_src == "":
        eth_src = None

    if eth_dst == '':
        eth_dst = None

    if eth_type == '':
        eth_type = None

    if vlan_vID == '':
        vlan_vID = None
     
    if vlan_PCP == '':
        vlan_PCP = None

    if ARP_spa == '':
        ARP_spa = None

    if ARP_tpa == '':
        ARP_tpa = None
        
    if IPv4_src == '':
        IPv4_src = None

    if IPv4_dst == '':
        IPv4_dst = None

    if IPv6_src == '':
        IPv6_src = None

    if IPv6_dst == '':
        IPv6_dst = None

    if ICMPv4_type == '':
        ICMPv4_type = None

    if ICMPv4_code == '':
        ICMPv4_code = None

    if ICMPv6_type == '':
        ICMPv6_type = None

    if ICMPv6_code == '':
        ICMPv6_code = None

    if TCP_src == '':
        TCP_src = None

    if TCP_dst == '':
        TCP_dst = None

    if UDP_src == '':
        UDP_src = None

    if UDP_dst == '':
        UDP_dst = None

    if SCTP_src == '':
        SCTP_src = None

    if SCTP_dst == '':
        SCTP_dst = None

    if IP_proto == '':
        IP_proto = None

    if VPN_service_type == '':
        VPN_service_type = 3;

    service = DTService(ID=ID, eth_src=eth_src, eth_dst=eth_dst, eth_type=eth_type, vlan_vID=vlan_vID, vlan_PCP=vlan_PCP, 
                        IPv4_src=IPv4_src, IPv4_dst=IPv4_dst, IPv6_src=IPv6_src, IPv6_dst=IPv6_dst, ICMPv4_type=ICMPv4_type,
                        ICMPv4_code=ICMPv4_code, ICMPv6_type=ICMPv6_type, ICMPv6_code=ICMPv6_code, TCP_src=TCP_src, 
                        TCP_dst=TCP_dst, UDP_src=UDP_src, UDP_dst=UDP_dst, SCTP_src=SCTP_src, SCTP_dst=SCTP_dst, 
                        IP_proto=IP_proto, ARP_spa=ARP_spa, ARP_tpa=ARP_tpa, VPN_service_type=VPN_service_type 
                        )
   
    service.ingress_core_node = ingress_node
    service.egress_core_node = egress_node
    service.ingress_interface = ingress_interface
    service.egress_interface = egress_interface
    service.name = name
    service.color = color

    return service

def getHTTPBody(http_request):
    request = str(http_request)
    body = ''

    pattern = '\r\n\r\n'
    start = request.find(pattern, 0, len(request))

    if start != -1:
        body = request[start:]

    return body

def increment_hex_value(value):
    value = str(value)
    # First converts hexa value to integer
    decimal = int(value,16)
    # Then we increment decimal value
    decimal = decimal + 1
    # Finally convert result to hexa 
    return hex(decimal)

def string_to_hexa(value):
    return int(value, 16)




def get_nodes_min_cost_link(a, b):
    '''
    We asume that exist link between a and b
    '''

    min_link = None
    for i in a.interfaces.itervalues():

        #We have te find the link
        link = None
        j = 0
        links = i.links.values()
        while link is None and j < len(i.links):
            l = links[j] 
            if l.to_node_int.node.router_id == b.router_id:
                link = l
            else:
                j = j + 1

        if link is not None:
            if min_link == None:
                min_link = link 
            elif link.weight < min_link.weight:
                min_link = link

    return min_link

def select_min_cost_adj_node(g_minu_s, D):
    w = None
    min_cost = 0
    for i in g_minu_s.itervalues():
        if D[i] != -1:
            if w is None:
                w = i
                min_cost = D[w]
            elif D[i] < min_cost:
                w = i
                min_cost = D[i]
        
    return w

def MultiDijkstra(G, start, end):
    '''
    docs
    '''

    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors
    S = {}  # Dictionary with processed nodes
    g_minu_s = {}

    #Inicializa G/S como G
    for g in G:
        g_minu_s[g.router_id] = g

    #Stars processing start node
    S[start.router_id] = start
    g_minu_s.pop(start.router_id) 
    for i in G:
        if(G[start].has_key(i)):
            #They are adjacents so we get the minimum weight link between them
            print 'start: ' + str(start.router_id) + ', end: ' + str(i.router_id)
            link = get_nodes_min_cost_link(start, i)
            D[i] = link.weight
            #P[i.router_id] = {'node': start, 'interface': link.from_node_int}
            P[i] = link
        else:
            D[i] = -1
            P[i] = None 

    #Process nodes untill S has all nodes in G
    for i in range(1, len(G)):
       
        w = select_min_cost_adj_node(g_minu_s, D)
        print w.router_id
        S[w.router_id] = w
        g_minu_s.pop(w.router_id)

        for v in g_minu_s.itervalues():
            l = get_nodes_min_cost_link(w,v)
            
            print 'Info: start=' + str(start.router_id) + ' end=' + str(end.router_id) 

            if (l != None) and (((D[v] == -1) and (D[w] != -1)) or (D[w] + l.weight < D[v])):
                
                print 'v='+ str(v.router_id) + ', D[w]=' + str(D[w]) + ', l.weight='+ str(l.weight) + ', D[v]=' + str(D[v])

                D[v] = D[w] + l.weight
                #P[v.router_id] = {'node': w, 'interface': link.from_node_int}
                P[v] = l

    return (D,P)

def shortestPathMultiGraph(G, start, end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as Dijkstra().
    The output is a list of the vertices in order along
    the shortest path.
    """

    Path = []
    
    #Sanity check
    if G.has_key(start) and G.has_key(end):

        D,P = MultiDijkstra(G,start,end)

        i = end
        while i != start:
            l = P[i]
            Path.append(l)
            i = l.from_node_int.node
            
        Path.reverse()

    return Path

def JSONToDTNodeReduced(node):
    '''
    '''

    data = json.loads(node)

    result = DTNodeReduced(router_id=data['router_id'], 
                                name=data['node_name'],
                                top_type=data['node_top_type']) 

    return result

def JSONToDTInterfaceReduced(node):
    '''
    '''

    data = json.loads(node)
    result = DTInterfaceReduced(ip_address=data['ip_address'], router_id=data['router_id'],
                                i_type=data['iface_top_type'], ce_mac_address=data['ce_mac_address'],
                                ce_ip_address=data['ce_ip_address']) 

    return result