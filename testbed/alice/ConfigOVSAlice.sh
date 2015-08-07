####################################
# Configuracion de OVS para Alice  #
####################################
#
# Declara bridge, interfaces
ovs-vsctl add-br bral
ovs-vsctl set bridge bral datapath_type=netdev
ovs-vsctl set bridge bral protocols=OpenFlow13
ovs-vsctl set bridge bral other-config:datapath-id=000000000000000E
ovs-vsctl add-port bral eth1
ovs-vsctl add-port bral nf0
ovs-vsctl add-port bral nf1
ovs-vsctl add-port bral nf2
#
#Setea por defecto el fail mode
ovs-vsctl set-fail-mode bral secure
#
#Interfaces virtuales
ovs-vsctl add-port bral veth1 -- set interface veth1 type=internal
ovs-vsctl add-port bral vnf0 -- set interface vnf0 type=internal
ovs-vsctl add-port bral vnf1 -- set interface vnf1 type=internal
ovs-vsctl add-port bral vnf2 -- set interface vnf2 type=internal
#
#Controlador
ovs-vsctl set-controller bral tcp:192.168.1.10:6633
