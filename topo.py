"""@ package topo
This package includes code to represent network topologies.
"""

"return False 错误提示写在用户界面"

class Topologies(object):
    def __init__(self):
        self.topos = {}
        self.topoNum = 0

    def addTopo(self, topo=None,topoName=None):
        if topo:
            self.topos[topo.name] = topo
            self.topoNum += 1
            return True
        if topoName:
            topo = Topo(topoName)
            self.topos[topoName] = topo
            self.topoNum += 1
            return True
        return False
    
    def deleteTopo(self,name):
        if name == None:
            return False
        if not name in self.topos:
            return False
        del self.topos[name]
        self.topoNum -= 1
        return True


"TODO: 添加 Mininet API"
class Topo(object):
        def __init__(self,topoName):
            self.topoName = topoName
            self.nodes = {}
            self.link = {}
            self.count = {}
            self.count.setdefault("host",0)
            self.count.setdefault("switch",0)
            self.count.setdefault("controller",0)
        
        def addNode(self,node=None,type=None,name=None,ip=None):
            if node == None:
                node = Node(type,name,ip)
            if node.type == None:
                node.type = "host"
            # default name
            if node.name == None:
                node.name = node.type + str(self.count[node.type])
            self.count[node.type] += 1
            self.nodes[node.name] = node
            self.link.setdefault(node,[])
        
        def deleteNode(self,name):
            if name == None:
                return False
            if not name in self.nodes:
                return False
            node = self.nodes[name]
            self.count[node.type] -= 1
            del self.nodes[name]
            return True
        
        "TODO: 区分失败的类型"
        def addLink(self,srcName,destName):
            if(srcName == None) or (destName == None):
                return False
            if not(srcName in self.nodes) or not(destName in self.nodes):
                return False
            "sorted by node name"
            srcName,destName = sorted([srcName,destName])
            srcNode = self.nodes[srcName]
            destNode = self.nodes[destName]
            if self.link[srcNode].count(destNode):
                print("link already exists")
                return False
            self.link[srcNode].append(destNode)
            return True

        def deleteLink(self, srcName, destName):
            if(srcName == None) or (destName == None):
                    return False
            if not(srcName in self.nodes) or not(destName in self.nodes):
                return False
            "sorted by node name"
            srcName,destName = sorted([srcName,destName])
            srcNode = self.nodes[srcName]
            destNode = self.nodes[destName]
            if self.link[srcNode].count(destNode) == 0:
                print("link does not exist")
                return False
            self.link[srcNode].remove(destNode)
        
        # topo 转成字典，方便写入文件
        def topoToDict(self):
            data = {}
            data.setdefault('topo',[])
            data.setdefault('host',[])
            data.setdefault('switch',[])
            data.setdefault('controller',[])
            data.setdefault('link',[])
            topoName = {}
            topoName['name'] = self.topoName
            topoList = []
            topoList.append(topoName)
            nodeList = {}
            nodeList.setdefault('host',[])
            nodeList.setdefault('switch',[])
            nodeList.setdefault('controller',[])
            #key: node name, value: node
            for name,node in self.nodes.items():
                n = {}
                n['name'] = name
                n['ip'] = node.ip
                nodeList[node.type].append(n)
            # key: srcNode, value： desNode list
            linkList = []
            for src,dest in self.link.items():
                for d in dest:
                    linkDic = {}
                    linkDic.setdefault('source',src.name)
                    linkDic.setdefault('destination',d.name)
                    linkList.append(linkDic)
            data['topo'] = topoList
            data['host'] = nodeList['host']
            data['switch'] = nodeList['switch']
            data['controller'] = nodeList['controller']
            data['link'] = linkList
            return data

            

        def printTopo(self):
            topo = self
            print("topo name:",topo.topoName)
            print("node list:",end="")
            for key in topo.nodes:
                print(topo.nodes[key].name,end=" ")
            print("\nlink list:")
            for key in topo.link:
                print("src：",key.name,end=" link ")
                for n in topo.link[key]:
                    print(n.name,end=" ")
                print("")
            

        
class Node(object):
    def __init__(self, type=None,name=None, ip=None):
        self.name = name
        self.type = type
        self.ip = ip

if __name__ == "__main__":
    topos = Topologies()
    topos.addTopo(topoName="simpleTopo")
    topo = topos.topos["simpleTopo"]
    topo.addNode(type="host",ip="127.0.0.1")
    topo.addNode(type="host",ip="127.0.0.1")
    topo.addLink("host0","host1")
    topo.topoToDict()

    
