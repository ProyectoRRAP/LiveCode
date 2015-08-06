'''
Created on Feb 26, 2015

@author: efviodo
'''

import json
import logging

from ryu.base import app_manager

from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
#from rrap_app import RRAPapp
#from lsdb import LSDBSyncronizer
#from util import ManagementApp
#from controllers import TopologyController

proxy_instance_name = 'RyuApp'
url_node = '/topology/{rid}'

class RyuApp(app_manager.RyuApp):
    '''
    classdocs
    '''

    _CONTEXTS = { 
	   'wsgi': WSGIApplication
	#'rrap': RRAPapp,
	#'lsdb': LSDBSyncronizer,
	#'mng_app': ManagementApp 
    }
        
    def __init__(self, *args, **kwargs):
        super(RyuApp, self).__init__(*args, **kwargs)
        
        wsgi = kwargs['wsgi']
        wsgi.register(WSController, {proxy_instance_name : self})
	#self.rrap = kwargs['rrap']
	#self.lsdb = kwargs['lsdb']
	#self.mngapp = kwargs['mng_app']
	

	#self.topoc = TopologyController(self.mngapp)

	#topo_update = self.lsdb.update_ls_topology()
	#self.topoc.update_ls_topology(topo_update)

	print 'Init de Proxy'

    #ef get_topology_node(self, router_id):
	#eturn self.topoc.get_topology_node(router_id)


class WSController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(WSController, self).__init__(req, link, data, **config)
        self.proxy_spp = data[proxy_instance_name]

    @route('ws_topology_node', url_node, methods=['GET'], requirements={'rid':''})
    def get_topology_node(self, req, **kwargs):
	

	   router_id = kwargs['rid']
	   print router_id
    #    proxy = self.proxy_spp
	#node = proxy.get_topology_node(router_id)

 	#if node is None:
     #       return Response(status=404)

      #  try:	
       #     
	   # body = node.to_JSON()
       #     return Response(content_type='application/json', body=body)
       # except Exception as e:
        #    return Response(status=500)

