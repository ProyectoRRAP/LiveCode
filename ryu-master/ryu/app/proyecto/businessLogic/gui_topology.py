'''
Created on Feb 26, 2015

@author: efviodo
'''

import json
import logging

from ryu.base import app_manager

from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from dataTypes import DTNode, DTInterface, DTLink, DTLSNode, DTLSInterface, DTLSLink
from management_agents import ManagementApp
from util import listOfNodesToJSON, listOfServicesToJSON, listOfServicesLSPsToJSON, listOfNHLEToJSON, JSONToDTInterfaceReduced
from util import listOfFTNJSON, listOfILMJSON, JSONToListOfNodes, JSONToDTService, getHTTPBody, JSONToDTNodeReduced 
from controllers import TopologyController
from patterns import Singleton

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import mpls
from ryu.controller import dpset

import os

from webob.static import DirectoryApp

from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.base import app_manager

#####
from socket import error as SocketError
from ryu.contrib.tinyrpc.exc import InvalidReplyError


from ryu.app.wsgi import (
    ControllerBase,
    WSGIApplication,
    websocket,
    WebSocketRPCClient
)
from ryu.topology import event, switches
from ryu.controller.handler import set_ev_cls
#####

#API REST config
##VIEJAS
url_node = '/topology/{rid}'
url_topo = '/topology/'
url_mpls = '/mpls/'
url_services = '/services/'
##NUEVAS

URI_API_REST_TOPOLOGY = '/topology'
URI_API_REST_TOPOLOGY_NODE = URI_API_REST_TOPOLOGY + '/node'
URI_API_REST_TOPOLOGY_NODE_INTERFACE = URI_API_REST_TOPOLOGY_NODE + '/interfaces'
URI_API_REST_TOPOLOGY_NODE_MPLS = URI_API_REST_TOPOLOGY_NODE + '/mpls'
URI_API_REST_TOPOLOGY_NODE_MPLS_ILM = URI_API_REST_TOPOLOGY_NODE_MPLS + '/ilm'
URI_API_REST_TOPOLOGY_NODE_MPLS_FTN = URI_API_REST_TOPOLOGY_NODE_MPLS + '/ftn'
URI_API_REST_TOPOLOGY_NODE_MPLS_NHLFE = URI_API_REST_TOPOLOGY_NODE_MPLS + '/nhlfe'
URI_API_REST_TOPOLOGY_DATAPATHS = URI_API_REST_TOPOLOGY + '/datapaths'
URI_API_REST_SERVICES = '/services'
URI_API_REST_SERVICE = URI_API_REST_SERVICES + '/service'
URI_API_REST_SERVICES_LSPS = URI_API_REST_SERVICES + '/lsps'
URI_API_REST_TOPOLOGY_NODE_OF = URI_API_REST_TOPOLOGY_NODE + '/of'

PATH = os.path.dirname(__file__)


class Proxy(Singleton, object):

    management_app = ManagementApp(debug_mode=False)
    topo_controller = TopologyController(management_app)

    def __init__(self):
        super(Proxy, self).__init__()

        ### ELIMINAR: Temporal mientras no esta implementada la management_app
    #### 
    ##self.initialize_management_app()
        ## ELIMINAR

        #Creates mpls/ldp controller
        #self.mpls_controller = MPLSController()

        ### ELIMINAR: Temporal mientras no esta implementada LSDBSyncronizer
    #### 
    #lsdb = {}
    #### 
    #self.initialize_lsdb()
        ## ELIMINAR

        print 'Se VA A INICIALIZAR LSDB'
        ## ELIMINAR: Temporal mientras la actualizacion de la LSDB no se hace via ws
    #### 
    #self.topo_controller.update_ls_topology(self.lsdb)
        #self.topo_controller.redistribute_mpls_labels()
        ## ELIMINAR

        ## ATENCION!: Esto aun no se si va y en caso de ir donde ponerlo
        #topology = self.topo_controller.get_topology()
        #self.topo_controller.initialize_services()
        ## ATENCION!

        ## ELIMINAR: Lo pongo aca pero en toeoria se deberia hacer despues de redestribuir etiquetas
        #self.topo_controller.update_lsps()
        ## ELIMINAR
        

    #self.topoc = TopologyController(self.mngapp)

    #topo_update = self.lsdb.update_ls_topology()
    #self.topoc.update_ls_topology(topo_update)


    #ef get_topology_node(self, router_id):
    #eturn self.topoc.get_topology_node(router_id)


    ########## TOPOLOGY ######################################################
    def get_topology_node(self, router_id):
        return self.topo_controller.get_topology_node(router_id)

    def get_topology(self):
        return self.topo_controller.get_topology()

    def update_ls_topology(self, topo):
        return self.topo_controller.update_ls_topology(topo)

    def get_topology_nodes_datapaths(self):
        return self.topo_controller.get_topology_nodes_datapaths()

    def get_topology_nodes_interfaces(self, router_id):
        return self.topo_controller.get_topology_nodes_interfaces(router_id)

    def modify_topology_node(self, router_id, node_data):
        return self.topo_controller.modify_topology_node(router_id, node_data)

    def modify_topology_node_interface(self, router_id, interface_data):
        return self.topo_controller.modify_topology_node_interface(router_id, interface_data)

        

    ########## MPLS ##########################################################
    def get_node_mpls_tables_nhlfe(self, router_id):
        return self.topo_controller.get_node_mpls_tables_nhlfe(router_id)

    def get_node_mpls_tables_ilm(self, router_id):
        return self.topo_controller.get_node_mpls_tables_ilm(router_id)

    def get_node_mpls_tables_ftn(self, router_id):
        return self.topo_controller.get_node_mpls_tables_ftn(router_id)

    ########## Services ######################################################
    def add_service(self, service):
        '''
        doc
        '''
        return self.topo_controller.add_service(service)

    def update_service(self, service):
        '''
        doc
        '''
        return self.topo_controller.update_service(service)


    def get_services(self):
        '''
        doc
        '''
        return self.topo_controller.get_services()     

    def delete_service(self, sid):
        '''
        doc
        '''
        return self.topo_controller.delete_service(sid)  

    ########## LSPs #########################################################
    def get_service_lsps(self, service_ID):
        '''
        '''
        return self.topo_controller.get_service_lsps(service_ID) 

    def get_services_lsps(self):
        '''
        '''
        return self.topo_controller.get_services_lsps()  

    def update_services_lsps(self):
        '''
        '''
        return self.topo_controller.update_services_lsps()

    ########## OpenFlow #####################################################

    def get_topology_node_of_table(self, dpid):
        '''
        '''
        return self.topo_controller.get_topology_node_of_table(dpid)

    ################## COSAS TEMPORALES ELIMINAR
    ################## ELIMINAR
    def initialize_management_app(self):
        #Carga en la variable de topologia de la aplicacion de gestion toda la informacion extra de la
        # topologia
        nodes = {}
        n = DTNode(router_id='192.168.1.10', datapath_id='10', net_type=0, top_type=1, name='Gimly')
        interfaces = {}
        interfaces['192.168.1.10']=DTInterface(ip_address='192.168.1.10', mac_address='mac', ovs_port=0, i_type=1)
        n.interfaces =  interfaces
        nodes['192.168.1.10'] = n
      

        n = DTNode(router_id='192.168.1.11', datapath_id='11', net_type=1, top_type=1, name='Galois')
        interfaces = {}
        interfaces['192.168.1.11']=DTInterface(ip_address='192.168.1.11', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['192.168.2.11']=DTInterface(ip_address='192.168.2.11', mac_address='mac', ovs_port=1, i_type=1, name='veth1')
        interfaces['10.10.1.1']=DTInterface(ip_address='10.10.1.1', mac_address='mac', ovs_port=2, i_type=0, name='vnf0')
        interfaces['10.10.5.1']=DTInterface(ip_address='10.10.5.1', mac_address='mac', ovs_port=3, i_type=0, name='vnf1')
        interfaces['10.10.4.1']=DTInterface(ip_address='10.10.4.1', mac_address='mac', ovs_port=4, i_type=0, name='vnf2')
        n.interfaces =  interfaces
        nodes['192.168.1.11'] = n
        
        n = DTNode(router_id='192.168.1.12', datapath_id='12', net_type=1, top_type=1, name='Oz')
        interfaces = {}
        interfaces['192.168.1.12']=DTInterface(ip_address='192.168.1.12', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['192.168.2.12']=DTInterface(ip_address='192.168.2.12', mac_address='mac', ovs_port=1, i_type=1, name='veth1')
        interfaces['10.10.1.2']=DTInterface(ip_address='10.10.1.2', mac_address='mac', ovs_port=2, i_type=0, name='vnf0')
        interfaces['10.10.6.2']=DTInterface(ip_address='10.10.6.2', mac_address='mac', ovs_port=3, i_type=0, name='vnf0')
        interfaces['10.10.3.1']=DTInterface(ip_address='10.10.3.1', mac_address='mac', ovs_port=4, i_type=0, name='vnf0')
        n.interfaces =  interfaces
        nodes['192.168.1.12'] = n
        
        n = DTNode(router_id='192.168.1.13', datapath_id='13', net_type=1, top_type=1, name='Poisson')
        interfaces = {}
        interfaces['192.168.1.13']=DTInterface(ip_address='192.168.1.13', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['192.168.2.13']=DTInterface(ip_address='192.168.2.13', mac_address='mac', ovs_port=1, i_type=1, name='veth1')
        interfaces['10.10.4.2']=DTInterface(ip_address='10.10.4.2', mac_address='mac', ovs_port=4, i_type=0, name='vnf0')
        interfaces['10.10.2.1']=DTInterface(ip_address='10.10.2.1', mac_address='mac', ovs_port=2, i_type=0, name='vnf0')
        interfaces['10.10.6.1']=DTInterface(ip_address='10.10.6.1', mac_address='mac', ovs_port=3, i_type=0, name='vnf0')
        n.interfaces =  interfaces
        nodes['192.168.1.13'] = n
                
        n = DTNode(router_id='192.168.1.14', datapath_id='14', net_type=1, top_type=1, name='Alice')
        interfaces = {}
        interfaces['192.168.1.14']=DTInterface(ip_address='192.168.1.14', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['192.168.2.14']=DTInterface(ip_address='192.168.2.14', mac_address='mac', ovs_port=1, i_type=1, name='veth1')
        interfaces['10.10.3.2']=DTInterface(ip_address='10.10.3.2', mac_address='mac', ovs_port=4, i_type=0, name='vnf0')
        interfaces['10.10.2.2']=DTInterface(ip_address='10.10.2.2', mac_address='mac', ovs_port=2, i_type=0, name='vnf1')
        interfaces['10.10.5.2']=DTInterface(ip_address='10.10.5.2', mac_address='mac', ovs_port=3, i_type=0, name='vnf2')
        n.interfaces =  interfaces
        nodes['192.168.1.14'] = n

        self.management_app.topology = nodes

    def initialize_lsdb(self):
        nodes = {}

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
        i = DTLSInterface(node=galois, status=1, ip_address='192.168.2.11')
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
        i = DTLSInterface(node=oz, status=1, ip_address='192.168.2.12')
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
        i = DTLSInterface(node=poisson, status=1, ip_address='192.168.2.13')
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
        i = DTLSInterface(node=alice, status=1, ip_address='192.168.2.14')
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
                                                                                        to_node_int=galois.interfaces['192.168.1.11'], weight=float("inf"))        
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.12'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'], 
                                                                                        to_node_int=oz.interfaces['192.168.1.12'], weight=float("inf"))
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.13'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'], 
                                                                                        to_node_int=poisson.interfaces['192.168.1.13'],weight=float("inf"))
        nodes['192.168.1.10'].interfaces['192.168.1.10'].links['192.168.1.14'] = DTLSLink(status=1, from_node_int=gimly.interfaces['192.168.1.10'],
                                                                                        to_node_int=alice.interfaces['192.168.1.14'], weight=float("inf"))
        
        nodes['192.168.1.11'].interfaces['192.168.1.11'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=galois.interfaces['192.168.1.11'], 
                                                                                        to_node_int=gimly.interfaces['192.168.1.10'], weight=float("inf"))        
        nodes['192.168.1.11'].interfaces['10.10.1.1'].links['10.10.1.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.1.1'], 
                                                                                    to_node_int=oz.interfaces['10.10.1.2'], weight=1)
        nodes['192.168.1.11'].interfaces['10.10.4.1'].links['10.10.4.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.4.1'], 
                                                                                    to_node_int=poisson.interfaces['10.10.4.2'], weight=1)
        nodes['192.168.1.11'].interfaces['10.10.5.1'].links['10.10.5.2'] = DTLSLink(status=1, from_node_int=galois.interfaces['10.10.5.1'],
                                                                                     to_node_int=alice.interfaces['10.10.5.2'], weight=3)
        
        nodes['192.168.1.12'].interfaces['192.168.1.12'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=oz.interfaces['192.168.1.12'],
                                                                                        to_node_int=gimly.interfaces['192.168.1.10'], weight=float("inf"))        
        nodes['192.168.1.12'].interfaces['10.10.1.2'].links['10.10.1.1'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.1.2'],
                                                                                     to_node_int=galois.interfaces['10.10.1.1'], weight=1)
        nodes['192.168.1.12'].interfaces['10.10.6.2'].links['10.10.6.1'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.6.2'],
                                                                                     to_node_int=poisson.interfaces['10.10.6.1'], weight=1)
        nodes['192.168.1.12'].interfaces['10.10.3.1'].links['10.10.3.2'] = DTLSLink(status=1, from_node_int=oz.interfaces['10.10.3.1'],
                                                                                     to_node_int=alice.interfaces['10.10.3.2'], weight=2)
        
        nodes['192.168.1.13'].interfaces['192.168.1.13'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=poisson.interfaces['192.168.1.13'],
                                                                                        to_node_int=gimly.interfaces['192.168.1.10'], weight=float("inf"))        
        nodes['192.168.1.13'].interfaces['10.10.2.1'].links['10.10.2.2'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.2.1'],
                                                                                     to_node_int=alice.interfaces['10.10.2.2'], weight=1)
        nodes['192.168.1.13'].interfaces['10.10.6.1'].links['10.10.6.2'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.6.1'],
                                                                                     to_node_int=oz.interfaces['10.10.6.2'], weight=1)
        nodes['192.168.1.13'].interfaces['10.10.4.2'].links['10.10.4.1'] = DTLSLink(status=1, from_node_int=poisson.interfaces['10.10.4.2'], 
                                                                                     to_node_int=galois.interfaces['10.10.4.1'], weight=1)
        
        nodes['192.168.1.14'].interfaces['192.168.1.14'].links['192.168.1.10'] = DTLSLink(status=1, from_node_int=alice.interfaces['192.168.1.14'], 
                                                                                        to_node_int=gimly.interfaces['192.168.1.10'], weight=float("inf"))        
        nodes['192.168.1.14'].interfaces['10.10.2.2'].links['10.10.2.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.2.2'],
                                                                                     to_node_int=poisson.interfaces['10.10.2.1'], weight=1)
        nodes['192.168.1.14'].interfaces['10.10.5.2'].links['10.10.5.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.5.2'],
                                                                                     to_node_int=galois.interfaces['10.10.5.1'], weight=3)
        nodes['192.168.1.14'].interfaces['10.10.3.2'].links['10.10.3.1'] = DTLSLink(status=1, from_node_int=alice.interfaces['10.10.3.2'],
                                                                                     to_node_int=oz.interfaces['10.10.3.1'], weight=2)
    
        self.lsdb = nodes
       
##########################################################################
class WebSocketTopologyController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(WebSocketTopologyController, self).__init__(
            req, link, data, **config)
        self.app = data['app']

    @websocket('topology', '/v1.0/topology/ws')
    def _websocket_handler(self, ws):
        rpc_client = WebSocketRPCClient(ws)
        self.app.rpc_clients.append(rpc_client)
        rpc_client.serve_forever()

##########################################################################
##########################################################################
########## RYU MAIN APP
########################################################################## 
class GUIServerApp(app_manager.RyuApp):
    _CONTEXTS = {
        'wsgi': WSGIApplication,
        'dpset': dpset.DPSet,
        'switches': switches.Switches,
    }

    def __init__(self, *args, **kwargs):
        super(GUIServerApp, self).__init__(*args, **kwargs)

        # GET Proxy reference
        self.proxy = Proxy()

        wsgi = kwargs['wsgi']
        wsgi.register(GUIServerController, {'Proxy' : self.proxy, 'app': self})
        wsgi.register(WebSocketTopologyController, {'app': self})

        #For web socket connections
        self.rpc_clients = []

    ##########################################################################
    ########## OPENFLOW events handllers
    ########################################################################## 
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print str(datapath.id) + ' se ha conectado'
        
        #Notify to OFController that new node has reported
        #self.of_controller.report_of_switch(datapath.id)
        #Upgrade node state to OF Ready if node
        self.proxy.topo_controller.register_of_node(str(datapath.id), datapath)

        # install table-miss flow entry

    # OROIGINALMENTE LO PROGRAME PARA DETECTAR LA SALIDA DE UN SWITCH DESDE ACA PERO NO FUNCIONA
    # Y PARECE SER UN BUG DE RYU ASI QUE USAMOS dpSET y la funcion de ABAJO POR AHORA
    @set_ev_cls(ofp_event.EventOFPEchoRequest, MAIN_DISPATCHER)
    def _echo_rep_dead(self, ev):
        print 'EMI!!'
        print str(ev.msg)

        datapath = ev.msg.datapath
        print 'Datapath: ' + str(datapath)

        print 'Tipo: ' + str(ev.msg.msg_type)

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print str(datapath.id) + ''
        
    @set_ev_cls(ofp_event.EventOFPEchoRequest, DEAD_DISPATCHER)
    def _echo_rep_dead2(self, ev):
        print "DEBUG: In Handler for Echo Request (Dead)"

    #OTRA FORMA POR AHORA    
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        if ev.enter:
            print 'datapath join'
        else:
            print 'datapath leave'
            datapath = ev.dp
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            print str(datapath.id) + ' se ha desconectado'

            self.proxy.topo_controller.unregister_of_node(str(datapath.id), datapath)
        #Update node state to OpenFlow not enable

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
         # If you hit this you might want to increase
        # the "miss_send_length" of your switch
     #   if ev.msg.msg_len < ev.msg.total_len:
        #    self.logger.debug("packet truncated: only %s of %s bytes",
         #                     ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
       
        pkt = packet.Packet(msg.data)
        ip = pkt.get_protocol(ipv4.ipv4)
        #print ip

        #print 'Direccion IP SOURCE'
        #print ip.src 

        #print 'Direccion IP DESTINO'
        #print ip.dst 


    ####### EVENTOS PARA MANTENER ACTUALIZADA LA TOPO EN LA GUI #######

    # @set_ev_cls(event.EventSwitchEnter)
    # def _event_switch_enter_handler(self, ev):
    #     msg = ev.switch.to_dict()
    #     print 'Switch Enter'
    #     #self._rpc_broadcall('event_switch_enter', msg)

   #@set_ev_cls(event.EventSwitchLeave)
    #def _event_switch_leave_handler(self, msg):
        #print 'Switch Leave Emiliano'
        #data = json.dumps(msg, indent=2) 
        #print str(data)
        #self._rpc_broadcall('event_lsdb_switch_leave', msg)
        #self._rpc_broadcall('event_switch_leave', msg)

    # @set_ev_cls(event.EventLinkAdd)
    # def _event_link_add_handler(self, ev):
    #     msg = ev.link.to_dict()
    #     print 'Link Enter'
        #self._rpc_broadcall('event_link_add', msg)

    #@set_ev_cls(event.EventLinkDelete)
    #def _event_link_delete_handler(self, msg):
        #print 'Link Leave OF Event'
        #data = json.dumps(msg, indent=2) 
        #print str(data)
        #self._rpc_broadcall('event_lsdb_link_delete', msg)

        #self._rpc_broadcall('event_prueba', msg)


    # def _rpc_broadcall(self, func_name, msg):
    #     disconnected_clients = []
    #     for rpc_client in self.rpc_clients:
    #         # NOTE: Although broadcasting is desired,
    #         #       RPCClient#get_proxy(one_way=True) does not work well
    #         rpc_server = rpc_client.get_proxy()
    #         try:
    #             getattr(rpc_server, func_name)(msg)
    #         except SocketError:
    #             self.logger.debug('WebSocket disconnected: %s' % rpc_client.ws)
    #             disconnected_clients.append(rpc_client)
    #         except InvalidReplyError as e:
    #             self.logger.error(e)


    #     for client in disconnected_clients:
    #         self.rpc_clients.remove(client)

    def update_ws_clients_topology(self, nodes, links):
        '''
        '''

        #Update Links
        for l in links:
            self._event_link_delete_handler(l)

        #Updates nodes
        for n in nodes:
            self._event_switch_leave_handler(n)

        return True

    ###################################################################





    ##################################################################
    #### EXPERIMENTAL SACAR
    @set_ev_cls(ofp_event.EventOFPTableStatsReply, MAIN_DISPATCHER)
    def table_stats_reply_handler(self, ev):
        tables = []
        for stat in ev.msg.body:
            tables.append('table_id=%d active_count=%d lookup_count=%d '
                          ' matched_count=%d' %
                          (stat.table_id, stat.active_count,
                           stat.lookup_count, stat.matched_count))

        print 'TableStats: ' 
        #print str(tables)
        print str(ev.msg.body)

    @set_ev_cls(ofp_event.EventOFPTableFeaturesStatsReply, MAIN_DISPATCHER)
    def table_features_stats_reply_handler(self, ev):
        tables = []

        print 'TableStatsF: ' 
        #print str(tables)
        print str(ev.msg.body)


    @set_ev_cls(ofp_event.EventOFPStatsReply, MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        ofp = msg.datapath.ofproto
        body = ev.msg.body

        str(body)

     ##################################################################

#######################################################################################
################# WEB SERVICES API REST ###############################################
##### 
##### Description: api rest interfaces for differents components of 
##### application
#######################################################################################
class GUIServerController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(GUIServerController, self).__init__(req, link, data, **config)
        
        #Get reference to Web app to redirect
        path = "%s/html/" % PATH
        self.static_app = DirectoryApp(path)

        #Get reference to Proxy instance
        self.proxy = data['Proxy']

        self.mainapp = data['app']
         
    #Redirect to Home web app
    @route('topology', '/{filename:.*}')
    def static_handler(self, req, **kwargs):
        print str(kwargs['filename'])
        if kwargs['filename']:
            req.path_info = kwargs['filename']
        return self.static_app(req)

    ##########################################################################
    ########## TOPOLOGY API REST
    ########################################################################## 
    @route('ws_topology', URI_API_REST_TOPOLOGY, methods=['GET'])
    def get_topology(self, req, **kwargs):
          
        print 'REST Service: GET Topology'

        proxy = self.proxy
        topology = proxy.get_topology()
        if topology is None:
            return Response(status=404)

        try:    
            body = listOfNodesToJSON(topology)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology', URI_API_REST_TOPOLOGY, methods=['PUT'])
    def actualizar_topology(self, req, **kwargs):
          
        print 'REST Service: PUT Topology'

        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        print 'TOPOLOGIA JSON RECIVIDO'

        #Get topology data from JSON format data
        topo = JSONToListOfNodes(data) 

        proxy = self.proxy
        #resul = proxy.update_ls_topology(topo)
        nodes,links = proxy.update_ls_topology(topo)

        #Actualiza los caminos de los servicios
        proxy.update_services_lsps()

        #Actualiza las topologias en todos los cliente sweb socket POR AHORA LO SACAMOS
        #self.mainapp.update_ws_clients_topology(nodes, links)

        result = True
        if not result:
            return Response(status=404)

        try:    
            body = 'Update complete succefully'
            return Response(content_type='application/json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology_node', URI_API_REST_TOPOLOGY_NODE + '/{rid}', methods=['GET'], requirements={'rid':''})
    def get_topology_node(self, req, **kwargs):
        
        router_id = kwargs['rid']   
        print 'REST Service: GET Node by router_id ('+router_id+')'

        proxy = self.proxy
        node = proxy.get_topology_node(router_id)
        if node is None:
            return Response(status=404)

        try:    
            body = node.to_JSON()
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology_node', URI_API_REST_TOPOLOGY_NODE + '/{rid}', methods=['POST'], requirements={'rid':''})
    def modify_topology_node(self, req, **kwargs):
        
        router_id = kwargs['rid']   
        print 'REST Service: POST Node extra data for router_id ('+router_id+')'

        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        node_data = JSONToDTNodeReduced(data)

        proxy = self.proxy
        result = proxy.modify_topology_node(router_id, node_data)
        if result is None or result is False:
            return Response(status=404)

        try:    
            body = json.dumps({'Result': 'OK'}, 2)
            return Response(content_type='json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology_node', URI_API_REST_TOPOLOGY_DATAPATHS, methods=['GET'])
    def get_topology_nodes_dpid(self, req, **kwargs):
         
        print 'REST Service: GET Nodes datapath_id' 

        proxy = self.proxy
        datapath_ids = proxy.get_topology_nodes_datapaths()
        if datapath_ids is None:
            return Response(status=404)
        try:    
            body = json.dumps(datapath_ids, indent=2)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology_node_by_datapath_interfaces', URI_API_REST_TOPOLOGY_NODE_INTERFACE + '/{rid}', methods=['GET'],  requirements={'rid':''})
    def get_topology_node_interfaces_get(self, req, **kwargs):
         
        print 'REST Service: GET Nodes interfaces by datapath_id' 

        rid = kwargs['rid']   
        proxy = self.proxy
        interfaces = proxy.get_topology_nodes_interfaces(rid)
        if interfaces is None:
            return Response(status=404)
        try:    
            body = json.dumps(interfaces, indent=2)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology_node_by_datapath_interfaces', URI_API_REST_TOPOLOGY_NODE_INTERFACE + '/{rid}', methods=['POST'],  requirements={'rid':''})
    def get_topology_node_interfaces(self, req, **kwargs):
         
        print 'REST Service: POST Nodes interfaces extra data' 

        rid = kwargs['rid']   

        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        interface_data = JSONToDTInterfaceReduced(data)

        proxy = self.proxy
        result = proxy.modify_topology_node_interface(rid, interface_data)
        if result is None or result is False:
            return Response(status=404)

        try:    
            body = json.dumps({'Result': 'OK'}, 2)
            return Response(content_type='json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    ##########################################################################
    ########## MPLS API REST
    ########################################################################## 
    @route('ws_mpls_services', URI_API_REST_SERVICES, methods=['GET'])
    def get_services(self, req, **kwargs):
          
        print 'REST Service: GET Services'

        proxy = self.proxy
        servcs = proxy.get_services()
        if servcs is None:
            return Response(status=404)

        try:    
            body = listOfServicesToJSON(servcs)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)


    @route('ws_mpls_services', URI_API_REST_SERVICES, methods=['POST'])
    def add_service(self, req, **kwargs):
          
        print 'REST Service: POST Services'

        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        print data

        #Get topology data from JSON format data
        service = JSONToDTService(data) 

        proxy = self.proxy
        
        result = proxy.add_service(service)
        if result is None or not result:
            return Response(status=500)

        try:    
            body = json.dumps({'Result': 'OK'}, 2)
            return Response(content_type='json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_services', URI_API_REST_SERVICES, methods=['PUT'])
    def actualizar_service(self, req, **kwargs):
          
        print 'REST Service: PUT Service'

        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        print data

        #Get topology data from JSON format data
        service = JSONToDTService(data) 

        proxy = self.proxy
        
        result = proxy.update_service(service)
        if result is None or not result:
            return Response(status=500)

        try:    
            body = json.dumps({'Result': 'OK'}, 2)
            return Response(content_type='json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_services', URI_API_REST_SERVICE + '/{sid}', methods=['GET'], requirements={'sid':''})
    def get_service(self, req, **kwargs):
          
        print 'REST Service: GET Service Complete Data'

        sid = kwargs['sid']   
        proxy = self.proxy
        servcs = proxy.get_services()
        if servcs is None:
            return Response(status=404)

        try:    
            body = listOfServicesToJSON(servcs)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_services', URI_API_REST_SERVICE + '/{sid}', methods=['DELETE'], requirements={'sid':''})
    def delete_service(self, req, **kwargs):
        
        print 'REST Service: DELETE Service'

        sid = kwargs['sid']   
        proxy = self.proxy
        result = proxy.delete_service(sid)
        if result is None or result is False:
            return Response(status=404)

        try:    
            body = json.dumps({'Result': 'OK'}, 2)
            return Response(content_type='json', body=body, status=200)
        except Exception as e:
            return Response(status=500)

    

    @route('ws_mpls_services', URI_API_REST_SERVICES_LSPS, methods=['GET'])
    def get_services_lsps(self, req, **kwargs):
          
        print 'REST Service: GET Servicess lsps: '

        proxy = self.proxy
        servs_lsps = proxy.get_services_lsps()
        
        if servs_lsps is None:
            return Response(status=404)

        try:    
            body = listOfServicesLSPsToJSON(servs_lsps)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    #ACTUALIZAR ESTOS SERVICIOS DE ACA PARA ABAJO
    @route('ws_mpls_services', URI_API_REST_SERVICES_LSPS + '/{ID}', methods=['GET'], requirements={'ID':''})
    def get_service_lsps(self, req, **kwargs):
          
        service_ID = kwargs['ID']   
        print 'REST Service: GET Services lsps: ' + service_ID

        proxy = self.proxy
        lsps = proxy.get_service_lsps(service_ID)
        
        if lsps is None:
            return Response(status=404)

        try:    
            body = body= listOfServicesLSPsToJSON2(lsps)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', URI_API_REST_TOPOLOGY_NODE_MPLS_NHLFE + '/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_nhlfe(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables NHLFE'

        router_id = kwargs['ID']

        proxy = self.proxy
        nhlfe = proxy.get_node_mpls_tables_nhlfe(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfNHLEToJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', URI_API_REST_TOPOLOGY_NODE_MPLS_FTN + '/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_ftn(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables FTN'

        router_id = kwargs['ID']

        proxy = self.proxy
        nhlfe = proxy.get_node_mpls_tables_ftn(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfFTNJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', URI_API_REST_TOPOLOGY_NODE_MPLS_ILM + '/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_ilm(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables ILM'

        router_id = kwargs['ID']

        proxy = self.proxy
        nhlfe = proxy.get_node_mpls_tables_ilm(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfILMJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)


    @route('ws_mpls_node', URI_API_REST_TOPOLOGY_NODE_OF + '/{dpid}', methods=['GET'], requirements={'dpid':''})
    def get_topology_node_of(self, req, **kwargs):
          
        print 'REST Service: GET OF node table'

        dpid = kwargs['dpid']

        proxy = self.proxy
        of_table = proxy.get_topology_node_of_table(dpid)

        if of_table is None:
            return Response(status=404)

        try:    
            body= listOfILMJSON(of_table)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)


app_manager.require_app('ryu.app.rest_topology')
app_manager.require_app('ryu.app.ws_topology')
app_manager.require_app('ryu.app.ofctl_rest')

  