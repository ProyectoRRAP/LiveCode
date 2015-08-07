ovsdb-server /usr/local/etc/openvswitch/conf.db \
--remote=punix:/usr/local/var/run/openvswitch/db.sock \
--remote=db:Open_vSwitch,Open_vSwitch,manager_options \
--private-key=db:Open_vSwitch,SSL,private_key \
--certificate=db:Open_vSwitch,SSL,certificate \
--bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
--pidfile --detach --log-file=/var/log/openvswitch/openvswitch.log

ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach --log-file=/var/log/openvswitch/vswitch.log
ovs-vsctl show

