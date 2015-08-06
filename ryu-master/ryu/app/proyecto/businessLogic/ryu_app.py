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
from util import ManagementApp
from util import listOfNodesToJSON, listOfServicesToJSON, listOfServicesLSPsToJSON, listOfNHLEToJSON
from util import listOfFTNJSON, listOfILMJSON, JSONToListOfNodes, getHTTPBody
from controllers import TopologyController

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

PATH = os.path.dirname(__file__)


main_app_instance_name = 'RyuApp'

#API REST config
url_node = '/topology/{rid}'
url_topo = '/topology/'
url_mpls = '/mpls/'
url_services = '/services/'

class RyuApp(app_manager.RyuApp):
    '''
    classdocs
    '''

    _CONTEXTS = { 
	   'wsgi': WSGIApplication,
       'dpset': dpset.DPSet
	#'rrap': RRAPapp,
	#'lsdb': LSDBSyncronizer,
	#'mng_app': ManagementApp 
    }
        
    def __init__(self, *args, **kwargs):
        super(RyuApp, self).__init__(*args, **kwargs)

        wsgi = kwargs['wsgi']
        wsgi.register(GUIServerController)
        
        #wsgi.register(WSController, {main_app_instance_name : self})
	   
        self.dpset = kwargs['dpset']

        print 'Initialize main app'

        self.management_app = ManagementApp()
        ### ELIMINAR: Temporal mientras no esta implementada la management_app
        self.initialize_management_app()
        ## ELIMINAR

        #Creates topology controller with reference to management app
        self.topo_controller = TopologyController(self.management_app)

        #Creates mpls/ldp controller
        #self.mpls_controller = MPLSController()

        ### ELIMINAR: Temporal mientras no esta implementada LSDBSyncronizer
        self.lsdb = {}
        self.initialize_lsdb()
        ## ELIMINAR

        ## ELIMINAR: Temporal mientras la actualizacion de la LSDB no se hace via ws
        self.topo_controller.update_ls_topology(self.lsdb)
        #self.topo_controller.redistribute_mpls_labels()
        ## ELIMINAR

        ## ATENCION!: Esto aun no se si va y en caso de ir donde ponerlo
        #topology = self.topo_controller.get_topology()
        self.topo_controller.initialize_services()
        ## ATENCION!

        ## ELIMINAR: Lo pongo aca pero en toeoria se deberia hacer despues de redestribuir etiquetas
        #self.topo_controller.update_lsps()
        ## ELIMINAR

	#self.topoc = TopologyController(self.mngapp)

	#topo_update = self.lsdb.update_ls_topology()
	#self.topoc.update_ls_topology(topo_update)


    #ef get_topology_node(self, router_id):
	#eturn self.topoc.get_topology_node(router_id)



    ##########################################################################
    ########## Logic functionalities
    ########################################################################## 

    ########## TOPOLOGY ######################################################

    ########## MPLS ##########################################################

    ########## QoS ###########################################################
    def add_service(self, service, src_node, dst_node):
        '''
        doc
        '''
        self.topo_controller.add_service(service)

    def get_service(self):
        '''
        doc
        '''
        return self.topo_controller.add_service(service)        

    ################## COSAS TEMPORALES ELIMINAR
    ################## ELIMINAR
    def initialize_management_app(self):
        #Carga en la variable de topologia de la aplicacion de gestion toda la informacion extra de la
        # topologia
        nodes = {}
        n = DTNode(router_id='192.168.1.10', datapath_id='10', net_type=0, top_type=1)
        interfaces = {}
        interfaces['192.168.1.10']=DTInterface(ip_address='192.168.1.10', mac_address='mac', ovs_port=0, i_type=1)
        n.interfaces =  interfaces
        nodes['192.168.1.10'] = n
      

        n = DTNode(router_id='192.168.1.11', datapath_id='11', net_type=1, top_type=1)
        interfaces = {}
        interfaces['192.168.1.11']=DTInterface(ip_address='192.168.1.11', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['10.10.1.1']=DTInterface(ip_address='10.10.1.1', mac_address='mac', ovs_port=1, i_type=0)
        interfaces['10.10.5.1']=DTInterface(ip_address='10.10.5.1', mac_address='mac', ovs_port=2, i_type=0)
        interfaces['10.10.4.1']=DTInterface(ip_address='10.10.4.1', mac_address='mac', ovs_port=3, i_type=0)
        n.interfaces =  interfaces
        nodes['192.168.1.11'] = n
        
        n = DTNode(router_id='192.168.1.12', datapath_id='12', net_type=1, top_type=1)
        interfaces = {}
        interfaces['192.168.1.12']=DTInterface(ip_address='192.168.1.12', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['10.10.1.2']=DTInterface(ip_address='10.10.1.2', mac_address='mac', ovs_port=1, i_type=0)
        interfaces['10.10.6.2']=DTInterface(ip_address='10.10.6.2', mac_address='mac', ovs_port=2, i_type=0)
        interfaces['10.10.3.1']=DTInterface(ip_address='10.10.3.1', mac_address='mac', ovs_port=3, i_type=0)
        n.interfaces =  interfaces
        nodes['192.168.1.12'] = n
        
        n = DTNode(router_id='192.168.1.13', datapath_id='13', net_type=1, top_type=1)
        interfaces = {}
        interfaces['192.168.1.13']=DTInterface(ip_address='192.168.1.13', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['10.10.4.2']=DTInterface(ip_address='10.10.4.2', mac_address='mac', ovs_port=3, i_type=0)
        interfaces['10.10.2.1']=DTInterface(ip_address='10.10.2.1', mac_address='mac', ovs_port=1, i_type=0)
        interfaces['10.10.6.1']=DTInterface(ip_address='10.10.6.1', mac_address='mac', ovs_port=2, i_type=0)
        n.interfaces =  interfaces
        nodes['192.168.1.13'] = n
                
        n = DTNode(router_id='192.168.1.14', datapath_id='14', net_type=1, top_type=1)
        interfaces = {}
        interfaces['192.168.1.14']=DTInterface(ip_address='192.168.1.14', mac_address='mac', ovs_port=0, i_type=1)
        interfaces['10.10.3.2']=DTInterface(ip_address='10.10.3.2', mac_address='mac', ovs_port=3, i_type=0)
        interfaces['10.10.2.2']=DTInterface(ip_address='10.10.2.2', mac_address='mac', ovs_port=1, i_type=0)
        interfaces['10.10.5.2']=DTInterface(ip_address='10.10.5.2', mac_address='mac', ovs_port=2, i_type=0)
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
        self.topo_controller.register_of_node(str(datapath.id), datapath)

        # install table-miss flow entry

    # OROIGINALMENTE LO PROGRAME PARA DETECTAR LA SALIDA DE UN SWITCH DESDE ACA PERO NO FUNCIONA
    # Y PARECE SER UN BUG DE RYU ASI QUE USAMOS dpSET y la funcion de ABAJO POR AHORA
    @set_ev_cls(ofp_event.EventOFPEchoRequest, DEAD_DISPATCHER)
    def _echo_rep_dead(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        print str(datapath.id) + ' se ha desconectado'
        
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

            self.topo_controller.unregister_of_node(str(datapath.id), datapath)
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
                
       

class GUIServerController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(GUIServerController, self).__init__(req, link, data, **config)
        path = "%s/html/" % PATH
        self.static_app = DirectoryApp(path)

#######################################################################################
################# WEB SERVICES API REST ###############################################
##### 
##### Description: api rest interfaces for differents components of 
##### application
#######################################################################################
class WSController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(WSController, self).__init__(req, link, data, **config)
        self.main_app = data[main_app_instance_name]

        path = "%s/html/" % PATH
        self.static_app = DirectoryApp(path)

    @route('topology', '/{filename:.*}')
    def static_handler(self, req, **kwargs):
        if kwargs['filename']:
            req.path_info = kwargs['filename']
        return self.static_app(req)

    ##########################################################################
    ########## TOPOLOGY API REST
    ########################################################################## 
    @route('ws_topology_node', url_node + 'node/', methods=['GET'], requirements={'rid':''})
    def get_topology_node(self, req, **kwargs):
        
        router_id = kwargs['rid']	
        print 'REST Service: GET Node by router_id ('+router_id+')'

        node = self.main_app.topo_controller.get_topology_node(router_id)
        if node is None:
            return Response(status=404)

        try:    
            body = node.to_JSON()
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology', url_topo + '/get', methods=['GET'])
    def get_topology(self, req, **kwargs):
          
        print 'REST Service: GET Topology'

        topology = self.main_app.topo_controller.get_topology()
        if topology is None:
            return Response(status=404)

        try:    
            body = listOfNodesToJSON(topology)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_topology', url_topo + 'update', methods=['POST'])
    def update_topology(self, req, **kwargs):
          
        print 'REST Service: PUT Topology'
       
        #Separetes HTTP header from HTTP body
        data = getHTTPBody(req)

        #Get topology data from JSON format data
        topo = JSONToListOfNodes(data) 

        #result = self.main_app.topo_controller.update_ls_topology(topo)
        result = True
        if not result:
            return Response(status=404)

        try:    
            body = 'Update complete succefully'
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)


    @route('ws_topology_node', url_topo + 'datapath_ids', methods=['GET'])
    def get_topology_nodes_dpid(self, req, **kwargs):
         
        print 'REST Service: GET Nodes datapath_id' 

        datapath_ids = self.main_app.topo_controller.get_topology_nodes_datapaths()
        if datapath_ids is None:
            return Response(status=404)

        try:    
            body = json.dumps(datapath_ids, indent=2)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    ##########################################################################
    ########## MPLS API REST
    ########################################################################## 

    @route('ws_mpls_services', url_services, methods=['GET'])
    def get_services(self, req, **kwargs):
          
        print 'REST Service: GET Services'

        servcs = self.main_app.topo_controller.get_services()
        if servcs is None:
            return Response(status=404)

        try:    
            body = body= listOfServicesToJSON(servcs)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)


    @route('ws_mpls_services', url_services, methods=['PUT'])
    def add_service(self, req, **kwargs):
          
        print 'REST Service: PUT Services'

        #Asignar!!!!!
        service = None
        src_node = -1
        dst_node = -1

        self.main_app.add_service(service)
        #fecs = self.main_app.mpls_controller.get_fecs()
        #if fecs is None:
        #    return Response(status=404)

        #try:    
         #   body = body= listOfFecsToJSON(fecs)
          #  return Response(content_type='application/json', body=body)
        #except Exception as e:
         #   return Response(status=500)

    @route('ws_mpls_services', url_services + 'lsps/{ID}', methods=['GET'], requirements={'ID':''})
    def get_service_lsps(self, req, **kwargs):
          
        service_ID = kwargs['ID']   
        print 'REST Service: GET Services lsps: ' + service_ID

        lsps = self.main_app.topo_controller.get_service_lsps(service_ID=service_ID)
        
        if lsps is None:
            return Response(status=404)

        try:    
            body = body= listOfServicesLSPsToJSON(lsps)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', url_mpls + 'tables/nhlfe/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_nhlfe(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables NHLFE'

        router_id = kwargs['ID']

        nhlfe = self.main_app.topo_controller.get_node_mpls_tables_nhlfe(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfNHLEToJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', url_mpls + 'tables/ftn/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_ftn(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables FTN'

        router_id = kwargs['ID']

        nhlfe = self.main_app.topo_controller.get_node_mpls_tables_ftn(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfFTNJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

    @route('ws_mpls_node', url_mpls + 'tables/ilm/{ID}', methods=['GET'], requirements={'ID':''})
    def get_mpls_tables_ilm(self, req, **kwargs):
          
        print 'REST Service: GET MPLS node tables ILM'

        router_id = kwargs['ID']

        nhlfe = self.main_app.topo_controller.get_node_mpls_tables_ilm(router_id)

        if nhlfe is None:
            return Response(status=404)

        try:    
            body = body= listOfILMJSON(nhlfe)
            return Response(content_type='application/json', body=body)
        except Exception as e:
            return Response(status=500)

class GUIServerController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(GUIServerController, self).__init__(req, link, data, **config)
        path = "%s/html/" % PATH
        self.static_app = DirectoryApp(path)

    @route('topology', '/{filename:.*}')
    def static_handler(self, req, **kwargs):
        if kwargs['filename']:
            req.path_info = kwargs['filename']
        return self.static_app(req)


app_manager.require_app('ryu.app.rest_topology')
app_manager.require_app('ryu.app.ws_topology')
app_manager.require_app('ryu.app.ofctl_rest')
