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
from mininet.topo import Topo, SingleSwitchTopo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel,output,info,debug
from topo import Nets

class DataManager:
  def __init__(self,nets):
        self.nets = nets
  
  def getNet(self,fileName):
    # load data from file
    if not(os.path.exists(fileName) and os.path.isfile(fileName)):
        return False
    file = open(fileName,'r')
    fileData = file.read()
    file.close()
    data = yaml.load(fileData,Loader=yaml.FullLoader)
    
    # get net name
    netName = data['net']['name']
    net = self.nets.addNet(netName)
    
    # get hosts
    nodes = data['hosts']
    for n in nodes:
          print(n['ip'])
          self.nets.addHost(n['name'],netName,n['ip'])
    
    #get switchs
    nodes = data['switches']
    for n in nodes:
          self.nets.addSwitch(n['name'],netName)
    
    #get links
    links = data['link']
    for l in links:
          self.nets.addLink(l['source'],l['destination'],netName)
    net.start()
    CLI(net)
          
          

  def writeNet(self,fileName,netname):
    # 一个 yaml 文件只写一个 topology
    # if os.path.exists(fileName):
    #     return False
    types = ['hosts','switches','controllers']
    data = {}
    data['net'] = {'name': netname}

    #get net from nets
    net = self.nets.nets.get(netname)
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
    curpath = os.path.dirname(os.path.realpath(__file__))
    yamlpath = os.path.join(curpath, fileName)
    with open(yamlpath, "w") as f:
        yaml.dump(data, f)
    

    

    
if __name__ == "__main__":
    setLogLevel('info')
    nets = Nets()
    #topo = SingleSwitchTopo()
    #net = Mininet(topo)
    #nets.addNet("singleTopo",net)
    #data = Data(nets)
    #data.writeNet("singleTopo.yml","singleTopo")
    #data.getNet("singleTopo.yml")