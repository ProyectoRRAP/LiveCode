#!/usr/bin/python  

import telnetlib
import re

from datatypes import *





HOST = "localhost"
password = "zebra"
port = 2604



'''
telnetlib.TELNET_PORT = port

tn = telnetlib.Telnet(HOST)

if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("show ip ospf database router\n")
tn.write("exit\n")
salida = tn.read_all()
'''
salida = "ospfd> show ip ospf database router OSPF Router with ID (192.168.1.10) Router Link States (Area 0.0.0.0) LS age: 844 Options: 0x2 : *|-|-|-|-|-|E|* LS Flags: 0x3 Flags: 0x2 : ASBR LS Type: router-LSA Link State ID: 192.168.1.10 Advertising Router: 192.168.1.10 LS Seq Number: 80000006 Checksum: 0xe587 Length: 36 Number of Links: 1 Link connected to: a Transit Network (Link ID) Designated Router address: 192.168.1.14 (Link Data) Router Interface address: 192.168.1.10 Number of TOS metrics: 0 TOS 0 Metric: 10 LS age: 813 Options: 0x2 : *|-|-|-|-|-|E|* LS Flags: 0x6 Flags: 0x0 LS Type: router-LSA Link State ID: 192.168.1.12 Advertising Router: 192.168.1.12 LS Seq Number: 80000013 Checksum: 0x197d Length: 72 Number of Links: 4 Link connected to: a Transit Network (Link ID) Designated Router address: 192.168.1.14 (Link Data) Router Interface address: 192.168.1.12 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: a Transit Network (Link ID) Designated Router address: 10.10.1.2 (Link Data) Router Interface address: 10.10.1.2 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: Stub Network (Link ID) Net: 10.10.6.0 (Link Data) Network Mask: 255.255.255.0 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: a Transit Network (Link ID) Designated Router address: 10.10.3.2 (Link Data) Router Interface address: 10.10.3.1 Number of TOS metrics: 0 TOS 0 Metric: 10 LS age: 252 Options: 0x2 : *|-|-|-|-|-|E|* LS Flags: 0x6 Flags: 0x0 LS Type: router-LSA Link State ID: 192.168.1.14 Advertising Router: 192.168.1.14 LS Seq Number: 8000001c Checksum: 0xf2ab Length: 72 Number of Links: 4 Link connected to: a Transit Network (Link ID) Designated Router address: 192.168.1.14 (Link Data) Router Interface address: 192.168.1.14 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: Stub Network (Link ID) Net: 10.10.2.0 (Link Data) Network Mask: 255.255.255.0 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: Stub Network (Link ID) Net: 10.10.5.0 (Link Data) Network Mask: 255.255.255.0 Number of TOS metrics: 0 TOS 0 Metric: 10 Link connected to: a Transit Network (Link ID) Designated Router address: 10.10.3.2 (Link Data) Router Interface address: 10.10.3.2 Number of TOS metrics: 0 TOS 0 Metric: 10 "

arregloNodos = salida.split("LS age")

contador = 0

resultado = []

for nodo in arregloNodos:
    contador = contador +1;
    if contador>1 :        
        nodoTemp = nodo.split("Link State ID")
        indexFIN =  nodoTemp[1].index("Advertising")
        routerID = nodoTemp[1][2:indexFIN]
        print routerID
        nodo = DTLSNode(router_id = routerID)
                
        #print nodoTemp[1]
        interfacesTemp = nodoTemp[1].split("Link connected to")
        interfaces = []
        for inter in interfacesTemp:
            if "Transit Network" in inter:                
                interTemp = inter.split("Designated Router address")[1]
                
                ipRegexp = re.compile(".*")
                result = ipRegexp.match(interTemp)
                ip1 = result.group()   
                
                interTemp =   interTemp.split("Router Interface address")[1]
                result = ipRegexp.match(interTemp)
                ip2 = result.group()
                #interfaz = Interfaz(ip2,ip1)
                interfaz = DTLSInterface( node=nodo, ip_address = ip2 )                
                interfaces.append(interfaz)
                print ip1
                print '------------'
        #nodo = Nodo(routerID,interfaces)
        nodo.interfaces =interfaces 
        resultado.append(nodo)
        
        
for n in resultado:
    print "Router id: " + n.router_id
    for interfaz in n.interfaces:
        print "\tInterfaz: " + interfaz.ip_address
