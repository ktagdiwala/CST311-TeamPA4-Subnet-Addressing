#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.term import makeTerm
from subprocess import call
from time import sleep
"""Team Programming Assignment 4 (Subnet Addressing)
__author__ = "[Stack Otterflow]"
__credits__ = [
    "Krishna Tagdiwala",
    "Jorge Vazquez",
    "Walid Elgammal",
    "Jesus Martinez Miranda"
]
"""
def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/24')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)
# Assigning IP addresses and default routes to routers
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)                          # Open vSwitch L2 (no IP addresses assigned)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)                          # Open vSwitch L2 (no IP addresses assigned)
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24', defaultRoute='via 10.0.2.1')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')
    r4 = net.addHost('r4', cls=Node, ip='192.168.50.2/30')                  # Adjacent Router with Peer r3
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
    r3 = net.addHost('r3', cls=Node, ip='10.0.0.1/24', defaultRoute='via 10.0.0.1')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.3/24', defaultRoute='via 10.0.0.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.4/24', defaultRoute='via 10.0.0.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.2.3/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.2.4/24', defaultRoute='via 10.0.2.1')

# Link routers (r3, r4) and (r4, r5) in order
    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)
    net.addLink(s2, r5, intfName2='r5-eth0', params2={  'ip'  :  '10.0.2.1/24' } )   # Explicit router/switch link
    net.addLink(s1, r3, intfName2='r3-eth0', params2={  'ip'  :  '10.0.0.1/24' } )   # Explicit router/switch link
    net.addLink(r3, r4, intfName1='r3-eth1', params1={  'ip'  : '192.168.50.1/30'},
                        intfName2='r4-eth0', params2={  'ip'  : '192.168.50.2/30'} )
    net.addLink(r4, r5, intfName1='r4-eth1', params1={  'ip'  : '192.168.60.1/30'},   # New network introduced
                        intfName2='r5-eth1', params2={  'ip'  : '192.168.60.2/30'} )

    info( '*** Starting network\n')
    net.build()

    # 6 static routes - map to each network by forwarding network traffic to a specific destination.
    net['r5'].cmd('ip route add 10.0.0.0/24 via 192.168.60.1 dev r5-eth1')
    net['r3'].cmd('ip route add 192.168.60.0/30 via 192.168.50.2 dev r3-eth1')

    net['r3'].cmd('ip route add 10.0.2.0/24 via 192.168.50.2 dev r3-eth1')
    net['r4'].cmd('ip route add 10.0.0.0/24 via 192.168.50.1 dev r4-eth0')

    net['r4'].cmd('ip route add 10.0.2.0/24 via 192.168.60.2 dev r4-eth1')
    net['r5'].cmd('ip route add 192.168.50.0/30 via 192.168.60.1 dev r5-eth1')
  
    
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info( '*** Post configure switches and hosts\n')

    # using makeTerm API to start server program in Xterm terminal of host h4
    # and to start client program in xterm terminal of hosts h1 h2 h3
    makeTerm(h4, title='Host', term='xterm', display=None, cmd='python3 tpa4_chat_server.py; bash')
    sleep(1)
    makeTerm(h1, title='Client 1', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')
    makeTerm(h2, title='Client 2', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')
    makeTerm(h3, title='Client 3', term='xterm', display=None, cmd='python3 tpa4_chat_client.py; bash')

    CLI(net)
    net.stop()
    net.stopXterms()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()