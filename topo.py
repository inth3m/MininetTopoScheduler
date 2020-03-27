# -*- coding: utf-8 -*-
"""@ package topo
This package includes code to represent network topologies.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel,output,info,debug
from mininet.cli import CLI
from mininet.node import Controller, RemoteController, Node

import os
 
class Nets(object):
    ""
    def __init__(self):
        self.nets = {}
        self.netNum = 0
        # ruing net
        self.netName = ""
        self.net = None

    def addNet(self, netName, net=None):
        if net != None:
            self.nets[netName] = net
            return net
        
        if netName == "":
            netName = "net" + str(self.netNum)
        net = Mininet(topo=None, autoSetMacs=True,autoStaticArp=False)
        # Add a default controller
        info('*** Adding controller\n' )
        classes = net.controller
        if not isinstance( classes, list ):
            classes = [ classes ]
        for i, cls in enumerate( classes ):
            # Allow Controller objects because nobody understands partial()
            if isinstance( cls, Controller ):
                net.addController( cls )
            else:
                net.addController( 'c%d' % i, cls )
        self.nets[netName] = net
        return net

    def runingNet(self, netName):
        if netName == self.netName:
            debug("该网络正在运行\n")
            return False
        net = self.nets.get(netName)
        if net == None:
            debug("net 不存在")
            return False
        if self.net != None:
            debug("停止正在运行的网络:",self.netName)
            self.net.stop()
        net.start()
        self.netName = netName
        self.net = net
    
    def addHost(self,nodeName,netName=None,IP=None):
        if netName == None:
            netName = self.netName
        net = self.nets.get(netName)
        if net == None:
            debug("net 不存在")
            return False
        net.addHost(nodeName,ip=IP)

    def addSwitch(self,nodeName,netName=None,):
        if netName == None:
            netName = self.netName
        net = self.nets.get(netName)
        if net == None:
            debug("net 不存在")
            return False
        net.addSwitch(nodeName)
    
    def addLink(self,node1,node2,netName=None):
        if netName == None:
            netName = self.netName
        net = self.nets.get(netName)
        if net == None:
            debug("net 不存在")
            return False
        net.addLink(node1,node2)

    def getHostInfo(self,hostName):
        host = self.net.getNodeByName(hostName)
        info(host.name,host.intfs,host.params)
        return host.params

        

  
if __name__ == "__main__":
    setLogLevel('info')
    net = Nets()
    net.addNet("net0")
    net.addHost("h1","net0",IP = "10.0.0.1")
    net.addHost("h2","net0",IP = "10.0.0.2")
    net.addSwitch("s1","net0")
    net.addLink("s1","h1","net0")
    net.addLink("s1","h2","net0")
    net.runingNet("net0")
    CLI(net.nets["net0"])