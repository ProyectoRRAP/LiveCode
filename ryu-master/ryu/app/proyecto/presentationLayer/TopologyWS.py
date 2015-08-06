'''
Created on Feb 26, 2015

@author: efviodo
'''

import json
import logging

from ryu.base import app_manager

from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route

from ryu.app.proyecto.businessLogic.controllers import TopologyController

proxy_instance_name = 'Proxy'
url_node = '/topology/{rid}'

class Proxy(app_manager.RyuApp):
    '''
    classdocs
    '''

    _CONTEXTS = { 'wsgi': WSGIApplication }
        
    def __init__(self, *args, **kwargs):
 	super(Proxy, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(WSController, {proxy_instance_name : self})
	print 'Init de Proxy'

    def get_topology_node(router_id):
	print 'hola'
	


class WSController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(WSController, self).__init__(req, link, data, **config)
        self.proxy_spp = data[proxy_instance_name]

    @route('ws_topology_node', url_node, methods=['GET'], requirements={'rid':''})
    def get_topology_node(self, req, **kwargs):

        proxy = self.proxy_spp

        body = json.dumps('Hola')
        return Response(content_type='application/json', body=body)
