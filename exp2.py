#!/usr/bin/python3

from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

def exp2():
    net = Mininet(switch=OVSKernelSwitch, link=TCLink)

    #hosts
    info("*** Creating hosts\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    #switches
    info("*** Creating switches\n")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info("*** Creating links\n")
    # h1 -> s1
    net.addLink(h1, s1, intfName2='s1-eth1')

    # h2 -> s1
    net.addLink(h2, s1, intfName2='s1-eth2')

    # s1 -> s2
    net.addLink(s1, s2, intfName1='s1-eth3', intfName2='s2-eth1')

    # h3 -> s2
    net.addLink(h3, s2, intfName2='s2-eth2')

    info("*** Starting network\n")
    net.start()

    # switch fail mode to standalone because default "secure" creates unintended connection issues otherwise
    info("*** Setting fail mode to standalone\n")
    s1.cmd("ovs-vsctl set-fail-mode s1 standalone")
    s2.cmd("ovs-vsctl set-fail-mode s2 standalone")


    info("*** Running ping tests and recording results\n")
    results = []
    def testPing(src, dst): # source to destination ping
        output = net.get(src).cmd(f"ping -c 1 {dst}")
        results.append(f"==== {src} → {dst} ====\n{output}\n")

    # Required tests
    testPing('h1', '10.0.0.3') # h1 → h3
    testPing('h2', '10.0.0.3') # h2 → h3

    with open("result2.txt", "w") as f:
        f.writelines(results)

    info("*** Results saved to result2.txt\n")

    CLI(net) # where you do the ovs commands to drop/reroute flow
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    exp2()
