####################################
# Configuracion de OVS para Galois #
####################################

# Declara bridge, interfaces
ovs-vsctl add-br brgal
ovs-vsctl set bridge brgal datapath_type=netdev
ovs-vsctl set bridge brgal protocols=OpenFlow13
ovs-vsctl set bridge brgal other-config:datapath-id=000000000000000B
ovs-vsctl add-port brgal eth1
ovs-vsctl add-port brgal nf0
ovs-vsctl add-port brgal nf1
ovs-vsctl add-port brgal nf2

#Setea por defecto el fail mode
ovs-vsctl set-fail-mode brgal secure

#Interfaces virtuales
ovs-vsctl add-port brgal veth1 -- set interface veth1 type=internal
ovs-vsctl add-port brgal vnf0 -- set interface vnf0 type=internal
ovs-vsctl add-port brgal vnf1 -- set interface vnf1 type=internal
ovs-vsctl add-port brgal vnf2 -- set interface vnf2 type=internal

#Controlador
ovs-vsctl set-controller brgal tcp:192.168.1.10:6633

