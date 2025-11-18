#!/usr/bin/python3

from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.cli import CLI

# Linux Router Class
class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on routers
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super(LinuxRouter, self).terminate()


def exp1():
    net = Mininet(link=TCLink)

    # routers
    info("*** Creating routers\n")
    r1 = net.addHost('r1', cls=LinuxRouter, ip='10.0.0.3/24')
    r2 = net.addHost('r2', cls=LinuxRouter, ip='10.0.1.2/24')

    # hosts
    info("*** Creating hosts\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.3.2/24')
    h3 = net.addHost('h3', ip='10.0.2.2/24')

    # create links for topology
    info("*** Creating links\n")
    # h1 <-> r1
    net.addLink(h1, r1, intfName2='r1-eth0')

    # r1 <-> r2; forwarding both ways
    net.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth0')

    # r2 <-> h3
    net.addLink(r2, h3, intfName1='r2-eth1')

    # r1 <-> h2
    net.addLink(r1, h2, intfName1='r1-eth2')


    info("*** Starting network\n")
    net.start()

    info("*** Configuring router interfaces\n")
    # router interfaces
    r1.cmd("ip addr add 10.0.1.1/24 dev r1-eth1")
    r1.cmd("ip addr add 10.0.3.4/24 dev r1-eth2")
    r2.cmd("ip addr add 10.0.2.1/24 dev r2-eth1")

    info("*** Setting up host routes\n")
    # h1 → r1
    h1.cmd("ip route add default via 10.0.0.3") # we can use default route since only one route for h1, h2, h3

    # h2 -> r1
    h2.cmd("ip route add default via 10.0.3.4")

    # h3 -> r2
    h3.cmd("ip route add default via 10.0.2.1")

    # add subnet towards h3 via r2
    r1.cmd("ip route add 10.0.2.0/24 via 10.0.1.2")

    # subnets towards h1/h2 via r1
    r2.cmd("ip route add 10.0.0.0/24 via 10.0.1.1")
    r2.cmd("ip route add 10.0.3.0/24 via 10.0.1.1")



    info("*** Running ping tests and recording results\n")
    results = []
    def testPing(src, dst): # source to destination ping
        output = net.get(src).cmd(f"ping -c 1 {dst}")
        results.append(f"==== {src} → {dst} ====\n{output}\n")



    # default ping tests
    testPing('h1', '10.0.2.2') # h1 → h3
    testPing('h2', '10.0.2.2') # h2 → h3
    testPing('h3', '10.0.0.1') # h3 → h1
    testPing('h3', '10.0.3.2') # h3 → h2

    with open("result1.txt", "w") as f:
        f.writelines(results)

    info("*** Results saved to result1.txt\n")

    CLI(net) # Start CLI for manual ping testing
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    exp1()