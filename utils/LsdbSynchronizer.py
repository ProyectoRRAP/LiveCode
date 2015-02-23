import telnetlib

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


print salida

print '-------------------------------------------------------------------------'

print salida.split('ID')[0];















