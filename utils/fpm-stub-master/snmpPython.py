#!/usr/bin/python
import os
import commands
import re
import json


class Router:
	
	def __init__(self, dpid, routerId ,puertos,bridgeName):
         self.dpid = dpid
         self.routerId = routerId
         self.puertos = puertos
	 self.bridgeName = bridgeName
         

	def to_JSON(self):
		puertos_json=[]
		for i in self.puertos.values():
			if not i.nombreInterfaz.startswith('v'):			
				puertos_json.append({'numeroOVS':i.numeroOVS, 'mac': i.mac,'nombreInterfaz': i.nombreInterfaz, 'ip': i.ip })

		return json.dumps({'dpid': self.dpid, 'routerId' : self.routerId, 'puertos': puertos_json, 'bridge':bridgeName},separators=(',',':'))     


class Puerto:
     def __init__(self, numeroOVS, mac ,nombreInterfaz, ip=None):
         self.mac = mac
         self.numeroOVS = numeroOVS
         self.nombreInterfaz = nombreInterfaz
         self.ip = ip

     def printme(self):
     	print 'Puerto ' + self.numeroOVS + ' mac: ' + self.mac + ' nombreINterfaz: ' + self.nombreInterfaz

tempBridgeName = commands.getstatusoutput('/usr/local/bin/ovs-vsctl show')

tempBridgeArray = tempBridgeName[1].split('\n')
bridgeNameTemp = tempBridgeArray[1]
bridgeNameArray = bridgeNameTemp.split('Bridge')
bridgeName = bridgeNameArray[1].strip()


salidaOVS = commands.getstatusoutput('/usr/local/bin/ovs-ofctl -O openflow13 show ' + bridgeName)[1]
dpidTemp = salidaOVS.split('dpid:')
dpid = dpidTemp[1][0:16]


ipRegexp = re.compile('\d\(.*\).*')
result = ipRegexp.findall(salidaOVS)


puertos = {}
for portString in result:
	temp1 = portString.split('(')
	numeroPuerto = temp1[0]
	temp2 = temp1[1].split(')')
	nombreInterfaz = temp2[0]	
	temp3 = temp2[1].split('addr:')
	mac = temp3[1]
	port = Puerto(numeroPuerto,mac,nombreInterfaz)
	puertos[nombreInterfaz] = port

router = Router(dpid,"", puertos,bridgeName)



salidaifconfig = commands.getstatusoutput('ifconfig')[1]
test = salidaifconfig.split('\n\n')
for t in test:
	splitted = t.split('Link encap')
	name = splitted[0].strip()
	#print "name " + name


	ipRegexp = re.compile('inet addr:\d*\.\d*\.\d*\.\d*')
	result = ipRegexp.findall(splitted[1])
	if result:
		ip = result[0].split(':')[1]		
		if name in puertos.keys():			
			puertos[name].ip= ip

#mergear info de las int virtuales con las fisicas
for puertoV in puertos:
	if puertoV.startswith('v') :
		puertos[puertoV[1:]].ip = puertos[puertoV].ip


sacar = []
for puertoV in puertos:
        if not puertos[puertoV].ip:
                sacar.append(puertoV)

for aSacar in sacar:
        puertos.pop(aSacar,None)


print ".1.3.6.1.4.1.8888"
print "string"
print router.to_JSON()







