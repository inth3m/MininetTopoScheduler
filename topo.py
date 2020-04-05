# -*- coding: utf-8 -*-
"""@ package topo
This package includes code to represent network topologies.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel,output,info,debug
from mininet.cli import CLI
from mininet.node import Controller, RemoteController, Node
from itertools import chain, groupby
import os
 
class NetManager(object):
    def __init__(self):
        self.net = Mininet( controller=Controller,autoSetMacs=True)
        self.count = {}
        self.count.setdefault('hosts',0)
        self.count.setdefault('switches',0)
        self.count.setdefault('controllers',0)


    def update(self):
        titles = ['hosts','switches','controllers']
        for name in titles:
            nodes = getattr(self.net,name)
            if nodes == None:
                continue
            for n in nodes:
                self.count[name] += 1
        #print(self.count)

    def getNet(self):
        return self.net
    
    def setNet(self,net):
        self.net = net

    def addController(self,name):
        self.addController(name)
        self.count['controllers'] += 1

    def addHost(self,name,IP=None):
        self.net.addHost(name,ip=IP)
        self.count['hosts'] += 1

    def addSwitch(self,name):
        self.net.addSwitch(name)
        self.count['switches'] += 1
    
    def addLink(self,node1,node2):
        self.net.addLink(node1,node2)

    def getHostInfo(self,hostName):
        host = self.net.getNodeByName(hostName)
        info(host.name,host.intfs,host.params)
        return host.params
    
    def nextIP(self):
        return self.ipAdd( self.net.nextIP,ipBaseNum=self.net.ipBaseNum,prefixLen=self.net.prefixLen ) +'/%s' % self.net.prefixLen
                             
    def ipAdd(self, i, prefixLen=8, ipBaseNum=0x0a000000 ):
        imax = 0xffffffff >> prefixLen
        assert i <= imax, 'Not enough IP addresses in the subnet'
        mask = 0xffffffff ^ imax
        ipnum = ( ipBaseNum & mask ) + i
        return self.ipStr( ipnum )
    
    def ipStr(self, ip ):
        w = ( ip >> 24 ) & 0xff
        x = ( ip >> 16 ) & 0xff
        y = ( ip >> 8 ) & 0xff
        z = ip & 0xff
        return "%i.%i.%i.%i" % ( w, x, y, z )
    
    def startSwitch(self):
        net = self.net
        for switch in net.switches:
            info( switch.name + ' ')
            switch.start( net.controllers )
        started = {}
        for swclass, switches in groupby(
                sorted( net.switches,
                        key=lambda s: str( type( s ) ) ), type ):
            switches = tuple( switches )
            if hasattr( swclass, 'batchStartup' ):
                success = swclass.batchStartup( switches )
                started.update( { s: s for s in success } )
        if net.waitConn:
            net.waitConnected()