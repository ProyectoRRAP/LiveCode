########################################################
# Configuración de interfaces de Red para Host Poisson #
########################################################
#
#Interfaz para la lan de gestion
ifconfig eth0 192.168.1.13 netmask 255.255.255.0 up
#
#las interfaces de la topo no llevan IP
ifconfig eth1 0.0.0.0 up
ifconfig nf0 0.0.0.0 up
ifconfig nf1 0.0.0.0 up
ifconfig nf2 0.0.0.0 up

