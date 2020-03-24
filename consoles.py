"""@ package user interfac
"""

from tkinter import Frame,Button,Label
import data
from topo import Topologies,Topo

class Console(Frame):
    def __init__(self, parent, topo, node, height=10, width=32, title='Node' ):
        Frame.__init__(self, parent)
        self.topo = topo
        self.node = node
        self.height, self.width, self.title = height, width, title

class ConsoleApp(Frame):
    def __init__(self, topo, parent=None, width=4 ):
        Frame.__init__( self, parent )
        self.top = self.winfo_toplevel()
        self.top.title("Mininet虚拟节点调度系统")
        self.topo = topo
        self.menubar = self.createMenuBar()
        cframe = self.cframe = Frame( self )
        self.consoles = {}
        titles = {
            'hosts': 'host',
            'switches': 'switch',
            'controllers': 'controller',
            'scheduler':'scheduler'
        }
        for name in titles:
            nodes = self.topo.nodes
            frame, consoles = self.createConsoles(
                cframe, nodes, width, titles[ name ] )
            self.consoles[ name ] = Object( frame=frame, consoles=consoles )
        self.selected = None
        self.select( 'hosts' )
        self.cframe.pack( expand=True, fill='both' )
        self.pack( expand=True, fill='both' )
    
    def createConsoles(self, parent, nodes, width, title):
        f = Frame(parent)
        consoles = []
        index = 0
        for node in nodes.values():
            if node.type != title:
                continue
            console = Console(f, self.topo, node, title = title)
            consoles.append(console)
            row = int(index / width)
            column = int(index % width)
            # create node consoles
            if title == 'host':
                self.createHostLable(console,node)
            console.grid( row=row, column=column, sticky='nsew' )
            index += 1
            f.rowconfigure( row, weight=1 )
            f.columnconfigure( column, weight=1 )
        return f, consoles

    def createHostLable(self, parent, node):
            label_node_name = Label(parent,text="节点名称:")
            label_node_name.grid(row=0,column = 0)
            label_node_name = Label(parent,text=node.name)
            label_node_name.grid(row=0,column = 1)
            label_node_ip = Label(parent,text="节点IP:")
            label_node_ip.grid(row=1,column = 0)
            label_node_ip = Label(parent,text=node.ip)
            label_node_ip.grid(row=1,column = 1)
            l = Label(parent,text="服务状态:")
            l.grid(row = 2, column = 0)
            b = Button(parent,text="启动服务",cmd = None)
            b.grid(row = 3, column = 0)
            b = Button(parent,text="停止服务",cmd=None)
            b.grid(row = 3,column = 1)

    def select( self, groupName ):
        "Select a group of consoles to display."
        if self.selected is not None:
            self.selected.frame.pack_forget()
        self.selected = self.consoles[ groupName ]
        self.selected.frame.pack( expand=True, fill='both' )

    def createMenuBar( self ):
        "Create and return a menu (really button) bar."
        f = Frame( self )
        buttons = [
            ('文件', None),
            ('拓扑调度',lambda:self.select('scheduler')),
            ( '主机', lambda: self.select( 'hosts' ) ),
            ( '交换机', lambda: self.select( 'switches' ) ),
            ( '控制器', lambda: self.select( 'controllers' ) ),
            ( '退出', self.quit )
        ]
        for name, cmd in buttons:
            b = Button( f, text=name, command=cmd)
            b.pack( side='left' )
        f.pack( padx=4, pady=4, fill='x' )
        return f

def assign( obj, **kwargs ):
    "Set a bunch of fields in an object."
    obj.__dict__.update( kwargs )

class Object( object ):
    "Generic object you can stuff junk into."
    def __init__( self, **kwargs ):
        assign( self, **kwargs )

if __name__ == '__main__':
    topo = Topo("single")
    topo.addNode(type = "host",ip="127.0.0.1")
    topo.addNode(type = "host",ip = "127.0.0.2")
    topo.addNode(type = "host",ip="127.0.0.3")
    topo.addNode(type = "host",ip = "127.0.0.4")
    topo.addNode(type = "host",ip="127.0.0.5")
    topo.addNode(type = "host",ip = "127.0.0.6")
    app = ConsoleApp(topo,width=4 )
    app.mainloop()