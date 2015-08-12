#!/usr/bin/python  

import telnetlib
import re

from datatypes import *
import requests
import json



CONTROLLER = "http://192.168.1.10:8080/"
HOST = "localhost"
password = "zebra"
port = 2604


telnetlib.TELNET_PORT = port

tn = telnetlib.Telnet(HOST)

if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("show ip ospf database router\n")
tn.write("exit\n")
salida = tn.read_all()

arregloNodos = salida.split("LS age")

contador = 0

resultado = []

linksDictionary = {}
countAgregados = 0		
countRevisados = 0
for nodo in arregloNodos:
   
    contador = contador +1;
    if contador>1 :        
        nodoTemp = nodo.split("Link State ID")
        indexFIN =  nodoTemp[1].index("Advertising")
        routerID = nodoTemp[1][2:indexFIN].strip()        
        nodo = DTLSNode(router_id = routerID)
                
        #print nodoTemp[1]
        interfacesTemp = nodoTemp[1].split("Link connected to")
        interfaces = []
	print routerID
        freeInterfaces = 0
        for inter in interfacesTemp:
            if "Transit Network" in inter:                
                interTemp = inter.split("Designated Router address")[1]                
                ipRegexp = re.compile("\d*\.\d*\.\d*\.\d*")
                metricRegExp = re.compile("TOS \d* Metric: \d*")
                result = ipRegexp.findall(interTemp)
		metricTemp = metricRegExp.findall(interTemp)[0]
		metric = metricTemp.split(":")[1].strip()
		linkIdIP = result[0]
  		ipInterfaz = result[1]

                interfaz = DTLSInterface( node=nodo, ip_address = ipInterfaz)
                if (linksDictionary.has_key(linkIdIP)):			
                    linkGuardado = linksDictionary[linkIdIP]	
	            countRevisados+=1			
                    linkGuardado.to_node_int = interfaz	            
                    linkGuardado.to_node_router_id = routerID						
		    link = DTLSLink(linkIdIP, from_node_int=interfaz, to_node_int= linkGuardado.from_node_int, weight = metric)

                else:	
		    link = DTLSLink(linkIdIP, from_node_int=interfaz, weight = metric)
		    linksDictionary[linkIdIP] = link  
                interfaz.append_link(link)                
                interfaces.append(interfaz)
            if "Stub Network" in inter:
            	freeInterfaces+=1
		
        #nodo = Nodo(routerID,interfaces)
        nodo.interfaces =interfaces
	nodo.freeInterfaces = freeInterfaces 
        resultado.append(nodo)


res= '['    
for n in resultado:
	res += n.to_JSON() + ","
res = res[:-1]	
res+= ']'    
print res


resp = requests.put(CONTROLLER+'topology',data=res)

