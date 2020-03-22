"""@ package data
YAML description:

topo:
  - name: singleTopo
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

from topo import Topo,Node
import yaml
import os

def getTopo(fileName):
    if not(os.path.exists(fileName) and os.path.isfile(fileName)):
        return False
    file = open(fileName,'r',encoding="utf-8")
    fileData = file.read()
    file.close()
    data = yaml.load(fileData,Loader=yaml.FullLoader)
    # get topo
    #TODO： 一个 yaml 文件应该只有一个topo
    topoName = data.get('topo')
    if topoName == None:
        print("Topology does not exist")
        return False
    topo = Topo(topoName[0].get('name'))

    # get node
    type=['switch','host','controller']
    for t in type:
        nodes = data.get(t)
        if nodes != None:
            for node in nodes:
                topo.addNode(type=t,name=node.get('name'),ip=node.get('ip'))
    
    # get link
    links = data.get('link')
    if links != None:
        for l in links:
            topo.addLink(l.get('source'),l.get('destination'))

    topo.printTopo()
    return topo

def writeTopo(fileName,topo):
    if topo == None:
        return False
    # 一个 yaml 文件只写一个 topology
    if os.path.exists(fileName):
        return False
    #file = open(fileName,'w',encoding="utf-8")
    data = topo.topoToDict()
    print(data)
    curpath = os.path.dirname(os.path.realpath(__file__))
    yamlpath = os.path.join(curpath, fileName)
    with open(yamlpath, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
    

    

    


if __name__ == "__main__":
    topo = getTopo("test.yml")
    writeTopo("writeTest.yml",topo)