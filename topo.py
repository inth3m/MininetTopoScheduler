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
            self.count.setdefault("contorller",0)
        
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
            srcName,destName = sorted(srcName,destName)
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
            srcName,destName = sorted(srcName,destName)
            srcNode = self.nodes[srcName]
            destNode = self.nodes[destName]
            if self.link[srcNode].count(destNode) == 0:
                print("link does not exist")
                return False
            self.link[srcNode].remove(destNode)
            

        
class Node(object):
    def __init__(self, type=None,name=None, ip=None):
        self.name = name
        self.type = type
        self.ip = ip
    