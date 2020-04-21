from topo import NetManager
from mininet.net import Mininet
from mininet.cli import CLI
from console import Console
from mininet.log import setLogLevel,info,debug
from mininet.topolib import TreeTopo
from mininet.topo import Topo, LinearTopo,SingleSwitchTopo
import os
class Scheduler():    
    
    # 带宽优先
    # host < 4 单拓扑
    # 4 < host <16 线性拓扑，一个交换机连4个主机
    # host > 16 树状拓扑，一个交换机连 4 个节点
    def bandwidth(self,netManager):
        # 生成节点参数
        h = len(getattr( netManager.getNet(), 'hosts'))
        s = len(getattr( netManager.getNet(), 'switches'))
        name = 'h' + str(h + 1)
        ip = netManager.nextIP()

        if h == 4 and s == 1:
            self.singleToLinear(netManager,name,ip)
            return
        
        if h == 16 and s == 4:
            self.linearToTree(netManager,name,ip)
            return
        
        if h < 4 and s == 1:
            self.single(netManager,name,ip)
            return
        
        if h > 4 and h < 16:
            self.linear(netManager,name,ip)
        
        if h > 16:
            self.tree(netManager,name,ip)

    #host 1 ~ 4
    def single(self,netManager,name,ip):
        netManager.addHost(name,ip)
        swicths = getattr( netManager.getNet(), 'switches')
        # 确保只有一个 switch
        netManager.addLink(name,swicths[0].name)

    # host5 ~ host15
    def linear(self,netManager,name,ip):
        netManager.addHost(name,ip)
        # 找到netx switch，preSwitch
        nextSwitch = None
        preSwitch = None
        swicths = getattr( netManager.getNet(), 'switches')
        for s in swicths:
            cnt = netManager.linkCount(s)
            if cnt['host'] < 4:
                nextSwitch = s.name
            if cnt['host'] == 4 and cnt['switch'] == 1:
                preSwitch = s.name

        if nextSwitch != None:
            netManager.addLink(name,nextSwitch)
        else:
            swicthName =  's' + str(len(getattr( netManager.getNet(), 'switches')) + 1)
            netManager.addSwitch(swicthName)
            netManager.addLink(preSwitch,swicthName)
            netManager.addLink(name,swicthName)

    def tree(self,netManager,name,ip):
        netManager.addHost(name,ip)
        swicths = getattr( netManager.getNet(), 'switches')
        nextSwitch = None
        preSwitch = None
        key = None
        for s in swicths:
            cnt = netManager.linkCount(s)
            # 叶子节点
            if cnt['host'] >= 1 and cnt['host'] < 4:
                nextSwitch = s.name
                continue
            if cnt['switch'] < 4 and cnt['host'] == 0:
                preSwitch = s.name
            if cnt['switch'] == 4 and cnt['host'] == 0:
                key = s.name

        if nextSwitch != None:
            netManager.addLink(name,nextSwitch)
        else:
            swicthName =  's' + str(len(getattr( netManager.getNet(), 'switches')) + 1)
            netManager.addSwitch(swicthName)
            netManager.addLink(name,swicthName)
            if preSwitch != None:
                netManager.addLink(preSwitch,swicthName)
            else:
                root =  's' + str(len(getattr( netManager.getNet(), 'switches')) + 1)
                netManager.addSwitch(root)
                netManager.addLink(root,swicthName)
                netManager.addLink(root,key)
    # host = 16 变成 host = 17
    # 操作： 将所有switch 连接断开，添加1个新switch
    def linearToTree(self,netManager,name,ip):
        # 删除旧switch 连接
        # 作弊
        netManager.net.stop()
        netManager.net = Mininet(topo=TreeTopo(2,4))
        netManager.net.start()
        # swicths = getattr( netManager.getNet(), 'switches')
        # cnt = 0
        # for s in swicths:
        #     cnt = cnt + 1
        #     if cnt == len(swicths):
        #         break
        #     netManager.delLink(s.name,swicths[cnt].name)
        # # 添加1个 switch
        # switchName = 's' + str(len(getattr( netManager.getNet(), 'switches')))
        # netManager.addSwitch(switchName)
        # for s in swicths:
        #     netManager.addLink(s.name, switchName)

        self.tree(netManager,name,ip)        


    # host = 4 变成 host = 5
    # 操作： 添加一个 switch，新主机连到新 switch 上
    def singleToLinear(self,netManager,name,ip):
        swicths = getattr( netManager.getNet(), 'switches')
        swicthName =  's' + str(len(swicths) + 1)
        netManager.addSwitch(swicthName)
        netManager.addHost(name,ip)
        # 参数为空
        netManager.addLink(swicthName,swicths[0].name)
        netManager.addLink(name,swicthName)
        netManager.nextSwitch = swicthName

    def deployServer(self, name, consoles):
        for host in consoles:
            if host.waiting() == False:
                host.sendCmd('python ' + name)
                return True
        return False
