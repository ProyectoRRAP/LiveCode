#####################################
# Configuracion de OVS para Poisson #
#####################################
#
# Declara bridge, interfaces
ovs-vsctl add-br brpoi
ovs-vsctl set bridge brpoi datapath_type=netdev
ovs-vsctl set bridge brpoi protocols=OpenFlow13
ovs-vsctl set bridge brpoi other-config:datapath-id=000000000000000D
ovs-vsctl add-port brpoi eth1
ovs-vsctl add-port brpoi nf0
ovs-vsctl add-port brpoi nf1
ovs-vsctl add-port brpoi nf2
ovs-vsctl set-fail-mode brpoi secure
#
#Interfaces virtuales
ovs-vsctl add-port brpoi veth1 -- set interface veth1 type=internal
ovs-vsctl add-port brpoi vnf0 -- set interface vnf0 type=internal
ovs-vsctl add-port brpoi vnf1 -- set interface vnf1 type=internal
ovs-vsctl add-port brpoi vnf2 -- set interface vnf2 type=internal
#
#Controlador
ovs-vsctl set-controller brpoi tcp:192.168.1.10:6633
