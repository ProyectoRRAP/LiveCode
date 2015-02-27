#funciona todo, faltan checkeos de emptys. Faltan agregar a estructura

import telnetlib
import re

HOST = "localhost"
password = "zebra"
port = 2604



telnetlib.TELNET_PORT = port

tn = telnetlib.Telnet(HOST)

if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

tn.write("show ip ospf database network\n")
tn.write("exit\n")
salida = tn.read_all()


arregloTemporalRouters = salida.split('ID')

counterInfo = 0
for infoRouter in arregloTemporalRouters:
    counterInfo = counterInfo +1 
    if counterInfo >2:    
        indexParentesis =  infoRouter.find("(");
        print "Router id: " + infoRouter[2:indexParentesis]
        print "****"
        arregloRoutersConectados = re.split("/\d*", infoRouter)
        if (len(arregloRoutersConectados) > 1):                        
                routers = arregloRoutersConectados[1].split("Attached Router:")
                counterConectedRouters = 0
                for router in routers:
                    counterConectedRouters = counterConectedRouters+1
                    if counterConectedRouters >1:   
                        print "\trouter conectado:"
                        ip = re.compile(".*")
                        result = ip.match(router)
                        conectedRouter = result.group()                    
                        if  conectedRouter:
                            print "\t" +conectedRouter 
                print '-------------------------------------------------------------------------'
   
print "Se encontraron " + str(len(arregloTemporalRouters) -2) + " nodos en la red"















