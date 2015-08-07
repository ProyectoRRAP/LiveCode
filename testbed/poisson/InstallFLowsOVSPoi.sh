#Flujos para brdigear interfaces fisicas y virtuales
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=1,dl_type=0x0806,actions=output:5
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=5,dl_type=0x0806,actions=output:1
#
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=2,actions=output:6
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=6,actions=output:2
#
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=3,actions=output:7
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=7,actions=output:3
#
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=4,actions=output:8
ovs-ofctl -O openflow13 add-flow brpoi table=0,priority=0,hard_timeout=0,idle_timeout=0,in_port=8,actions=output:4




