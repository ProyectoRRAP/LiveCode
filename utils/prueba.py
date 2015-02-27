import telnetlib
import re



class Nodo(object):
    
    def __init__(self, id=None, listAdy=None):
        self.id = id
        self.listAdy = listAdy
        


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
arregloNodos = []


arregloTemporalRouters = salida.split('ID')

counterInfo = 0
for infoRouter in arregloTemporalRouters:
    counterInfo = counterInfo +1 
    if counterInfo >2:    
        indexParentesis =  infoRouter.find("(");
        routerId = infoRouter[2:indexParentesis]
        
        
        arregloRoutersConectados = re.split("/\d*", infoRouter)
        if (len(arregloRoutersConectados) > 1):                        
                routers = arregloRoutersConectados[1].split("Attached Router:")
                counterConectedRouters = 0
                listConectedNodes = []
                for Router in routers:
                    counterConectedRouters = counterConectedRouters+1
                    if counterConectedRouters >1:                      
                        ip = re.compile(".*")
                        result = ip.match(Router)
                        conectedRouter = result.group()                    
                        if conectedRouter:
                            listConectedNodes.append(conectedRouter)
        r = Nodo(id=routerId, listAdy= listConectedNodes)
        arregloNodos.append(r)
                                    
for rouObject in arregloNodos:
    print "--------------\n"
    print "Router id:"
    print rouObject.id    
    print "Adyacencias"
    for con in rouObject.listAdy:
        print "\t" + con
    

print "Se encontraron " + str(len(arregloTemporalRouters) -2) + " nodos en la red"















