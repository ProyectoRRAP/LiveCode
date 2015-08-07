ovs-vsctl add-br broz
ovs-vsctl set bridge broz datapath_type=netdev
ovs-vsctl set bridge broz protocols=OpenFlow13
ovs-vsctl set bridge broz other-config:datapath-id=000000000000000C
ovs-vsctl add-port broz nf0
ovs-vsctl add-port broz nf1
ovs-vsctl add-port broz nf2
ovs-vsctl set-controller broz tcp:192.168.1.10:6633

####################################
# Configuracion de OVS para Oz     #
####################################

# Declara bridge, interfaces
ovs-vsctl add-br broz
ovs-vsctl set bridge broz datapath_type=netdev
ovs-vsctl set bridge broz protocols=OpenFlow13
ovs-vsctl set bridge broz other-config:datapath-id=000000000000000C
ovs-vsctl add-port broz eth1
ovs-vsctl add-port broz nf0
ovs-vsctl add-port broz nf1
ovs-vsctl add-port broz nf2
#
#Interfaces virtuales
ovs-vsctl add-port broz veth1 -- set interface veth1 type=internal
ovs-vsctl add-port broz vnf0 -- set interface vnf0 type=internal
ovs-vsctl add-port broz vnf1 -- set interface vnf1 type=internal
ovs-vsctl add-port broz vnf2 -- set interface vnf2 type=internal



