#!/usr/bin/python
from flask import Flask
import commands



app = Flask(__name__)

@app.route('/snmp/atp/<address>')
def getInfo(address):
    print address
    tempArray = commands.getstatusoutput('snmpget -v2c -c public '+ address +' .1.3.6.1.4.1.8888')
    temp =tempArray[1]
    resultArray = temp.split('STRING:')
    result = resultArray[1].strip()
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0')
	#default port: 5000
