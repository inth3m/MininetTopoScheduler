from topo import NetManager
from mininet.net import Mininet
from mininet.cli import CLI
import os
class Scheduler():    
    
    # TODO 判断 srcNOde 是否存在
    # 自定义 Nodename
    # 自定义 IP
    # 接口名字
    def deployHost(self, netManager, srcNode,name = None, ip = None):
        if name == "":
            name = 'h' + str(netManager.count['hosts'] + 1)
        if ip == "":
            ip = netManager.nextIP()
        netManager.addHost(name,ip)
        netManager.addLink(name,srcNode)
        src = netManager.net.getNodeByName(srcNode)
        intfs = src.intfNames()
        num = intfs[-1][-1]  
        intName = srcNode + '-eth' + str(int (num))
        src.attach(intName)
        #print(name)
        node = netManager.net.getNodeByName(name)
        node.setIP(ip)
        #node.cmd('ifconfig h3-eth0 10.3')
        #netManager.net.build()
        #netManager.net.start()
        #CLI(netManager.net)
    
    def deploySwitch(self, netManager, srcNode,name = None):
        if name == "":
            name = 's' + str(netManager.count['switches'] + 1)
        netManager.addSwitch(name)
        netManager.addLink(srcNode,name)
        src = netManager.net.getNodeByName(srcNode)
        intfs = src.intfNames()
        num = intfs[-1][-1]  
        intName = srcNode + '-eth' + str(int (num))
        src.attach(intName)
        #CLI(netManager.net)
        netManager.startSwitch()