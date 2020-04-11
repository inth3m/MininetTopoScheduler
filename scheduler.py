from topo import NetManager
from mininet.net import Mininet
from mininet.cli import CLI
from console import Console
import os
class Scheduler():    
    
    def deployHost(self, netManager, srcNode,name = None, ip = None, mac = None):
        nodeType = ''

        # 判断源节点是否在网络里
        if netManager.isHost(srcNode):
            nodeType = 'host'
        if netManager.isSwitch(srcNode):
            nodeType = 'swicth'
        if nodeType == '':
            return False

        # 生成节点参数
        if name == '':
            name = 'h' + str(netManager.count['hosts'] + 1)
        if ip == '':
            ip = netManager.nextIP()
        
        netManager.addHost(name,ip)
        netManager.addLink(name,srcNode)
        
        if type == 'host':
            netManager.configHost(srcNode)
            netManager.configHost(name,ip)
        else:
            netManager.startSwitch()
            netManager.configHost(name,ip)
        
        #CLI(netManager.net)


    def deploySwitch(self, netManager, srcNode,name = None):
        nodeType = ''

        # 判断源节点是否在网络里
        if netManager.isHost(srcNode):
            nodeType = 'host'
        if netManager.isSwitch(srcNode):
            nodeType = 'swicth'
        if nodeType == '':
            return False
        
        # 生成参数
        if name == "":
            name = 's' + str(netManager.count['switches'] + 1)
        
        netManager.addSwitch(name)
        netManager.addLink(srcNode,name)

        if type == 'host':
            netManager.configHost(name)
        
        netManager.startSwitch()
        # src = netManager.net.getNodeByName(srcNode)
        # intfs = src.intfNames()
        # num = intfs[-1][-1]  
        # intName = srcNode + '-eth' + str(int (num))
        # src.attach(intName)
        # #CLI(netManager.net)
        # netManager.startSwitch()

    def deployServer(self, name, consoles):
        for host in consoles:
            if host.waiting() == False:
                host.sendCmd('python ' + name)
                break
