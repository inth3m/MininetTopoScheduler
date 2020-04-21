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

    def getNet(self):
        return self.net
    
    def setNet(self,net):
        self.net = net

    def addController(self,name):
        self.addController(name)

    def addHost(self,name,IP=None):
        if self.isHost(name):
            return False
        self.net.addHost(name,ip=IP)
        return True

    def addSwitch(self,name):
        if self.isSwitch(name):
            return False
        self.net.addSwitch(name)
        return True
    
    def addLink(self,node1,node2,params = None):
        if not self.isSwitch(node1) and not self.isHost(node1):
            return False
        if not self.isSwitch(node2) and not self.isHost(node2):
            return False
     
        # 设置默认值
        if params == None:
            self.net.addLink(node1,node2)
            #return True
        else:
            # 设置link 参数
            bw = 10000 if params.get('bw') is None else int(params.get('bw'))
            delay = 5 if params.get('delay') is None else int(params.get('bw'))
            loss = 0 if params.get('loss') is None else int(params.get('loss'))
            max_queue_size = 1000 if params.get('max_queue_size') is None else int(params.get('max_queue_size'))
            jitter = params.get('max_queue_size')
            self.net.addLink(node1,node2,bw = bw, loss = loss, delay = delay, max_queue_size = max_queue_size,jitter = jitter)
        
        # node 可能是 switch，configHost 会判断
        self.configHost(node1)
        self.configHost(node2)
        self.startSwitch()

    def delHost(self,name):
        if self.isHost(name) == False:
            return False
        node = self.net.get(name)
        #node.terminate()
        self.net.hosts.remove( node )
        del self.net.nameToNode[ node.name ]
        #self.net.delHost(node)

        return True
   
    def delSwitch(self,name):
        if self.isSwitch(name) == False:
            return False
        node = self.net.get(name)
        #self.net.delSwitch(node)
        self.net.switches.remove(node)
        del self.net.nameToNode[ node.name ]

    def delNode(self, name):
        if self.isHost(name) == False and self.isSwitch(name) == False:
            return False
        node = self.net.get(name)
        nodes = (self.net.hosts if node in self.net.hosts else 
                    (self.net.switches if node in self.net.switches else
                        []))
        self.delNodeLink(node)
        #node.stop( deleteIntfs=True )
        nodes.remove(node)
        del self.net.nameToNode[ node.name ]

    def delNodeLink(self,node):
        for intf in node.intfList():
            link = intf.link
            if link:
                self.delLink(link.intf1.node.name, link.intf2.node.name)

    def delLink(self,node1,node2):
        srcnode = self.net.get(node1)
        destnode = self.net.get(node2)
        if node1 == None or node2 == None:
            return False
        self.net.delLinkBetween(srcnode,destnode)

    def linkCount(self,node):
        cnt = {
            'host':0,
            'switch':0
        }
        for intf in node.intfList():
            link = intf.link
            if not link:
                continue
            node1, node2 = link.intf1.node, link.intf2.node
            if node1 == node:
                if self.isHost(node2.name):
                    cnt['host'] += 1
                if self.isSwitch(node2.name):
                    cnt['switch'] += 1
            else:
                if self.isHost(node1.name):
                    cnt['host'] += 1
                if self.isSwitch(node1.name):
                    cnt['switch'] += 1               
        return cnt

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
    
    def configHost(self,name,ip = None,mac = None):
        node = self.net.getNodeByName(name)
        info('config' + name)
        if node == None:
            return 
        intf = node.defaultIntf()
        if intf:
            node.configDefault()
        else:
            node.configDefault( ip=None, mac=None )           
        if ip != None:
            node.setIP(ip)
        if mac != None:
            node.setMac(mac)
    
    # 判断 name 是否在网络里
    def isHost(self, name):
        nodes = getattr(self.net,'hosts')
        for n in nodes:
            if name == n.name:
                return True
        return False
    
    def isSwitch(self, name):
        nodes = getattr(self.net,'switches')
        for n in nodes:
            if name == n.name:
                return True

        return False
    