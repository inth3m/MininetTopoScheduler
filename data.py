# -*- coding: utf-8 -*-
"""@ package data
YAML description:
host:
- name: h101
  ip: 10.0.1.1
- name: h102
  ip: 10.0.1.2
switch:
  - name: s1
controller:
  - name : c0
    ip : 198.163.211
link:
  - source: h1
    destination: s1
  - source: h2
    destination: s1
  - source: c0
    destination: s1
"""


import yaml
import os
from mininet.topo import Topo, SingleSwitchTopo,LinearTopo
from mininet.net import Mininet, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel,output,info,debug
from topo import NetManager
from mininet.link import TCLink
import tkinter

class DataManager:

    def getNet(self,fileName):
    # load data from file
        if not(os.path.exists(fileName) and os.path.isfile(fileName)):
            return None
        file = open(fileName,'r')
        fileData = file.read()
        file.close()
        try:
            data = yaml.load(fileData,Loader = yaml.SafeLoader)
        except yaml.YAMLError as exc:
            print(exc)
            return None
  
        net = Mininet( controller=Controller, link = TCLink)
        #get controller
        nodes = data['controllers']
        for n in nodes:
            net.addController(n['name'])

        # get hosts
        nodes = data['hosts']
        for n in nodes:
            net.addHost(n['name'],ip=n['ip'])

        #get switchs
        nodes = data['switches']
        for n in nodes:
            net.addSwitch(n['name'])

        #get links
        links = data['link']
        for l in links:
            net.addLink(l['source'],l['destination'])
        #net.start()
        #CLI(net)
        return net



    def writeNet(self,fileName,net):
    # 一个 yaml 文件只写一个 topology
    # if os.path.exists(fileName):
    #     return False
        types = ['hosts','switches','controllers']
        data = {}
        if net == None:
            return False

        for t in types:
            node_list = []
            nodes = getattr( net, t)
            for n in nodes:
                dic = {}
                dic['name'] = n.name
                if n.params.get('mac') != None:
                    dic['mac'] = n.params.get('mac')
                if n.params.get('ip') != None:
                    dic['ip'] = n.params.get('ip')
                node_list.append(dic)
            data[t] = node_list
        
        link = getattr(net,'links')
        link_list = []
        for l in link:
            node_dic = {}
            node_dic['source'] = l.intf1.node.name
            node_dic['destination'] = l.intf2.node.name
            link_list.append(node_dic)
        data['link'] = link_list
    #curpath = os.path.dirname(os.path.realpath(__file__))
        with open(fileName, 'w') as nf:
            yaml.dump(data, nf)



if __name__ == "__main__":
    setLogLevel('info')
    data = DataManager()
    data.getNet("test.yml")
    #data.writeNet("test.yml",net)
    #data.getNet("singleTopo.yml")