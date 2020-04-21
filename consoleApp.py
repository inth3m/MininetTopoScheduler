# -*- coding: utf-8 -*-
"""@ package user interfac
"""
import re

import tkinter
from tkinter import filedialog, messagebox,ttk
from tkinter import *
import os
from mininet.log import setLogLevel,debug,info
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from mininet.term import makeTerms, cleanUpScreens
from mininet.util import quietRun
from mininet.cli import CLI

from topo import NetManager
from data import DataManager
from scheduler import Scheduler
from console import Console


class Graph( Frame ):

    "Graph that we can add bars to over time."

    def __init__( self, parent=None, bg = 'white', gheight=200, gwidth=500,
                  barwidth=10, ymax=3.5,):

        Frame.__init__( self, parent )

        self.bg = bg
        self.gheight = gheight
        self.gwidth = gwidth
        self.barwidth = barwidth
        self.ymax = float( ymax )
        self.xpos = 0

        # Create everything
        self.title, self.scale, self.graph = self.createWidgets()
        self.updateScrollRegions()
        self.yview( 'moveto', '1.0' )

    def createScale( self ):
        "Create a and return a new canvas with scale markers."
        height = float( self.gheight )
        width = 25
        ymax = self.ymax
        scale = Canvas( self, width=width, height=height,
                        background=self.bg )
        opts = { 'fill': 'red' }
        # Draw scale line
        scale.create_line( width - 1, height, width - 1, 0, **opts )
        # Draw ticks and numbers
        for y in range( 0, int( ymax + 1 ) ):
            ypos = height * (1 - float( y ) / ymax )
            scale.create_line( width, ypos, width - 10, ypos, **opts )
            scale.create_text( 10, ypos, text=str( y ), **opts )
        return scale

    def updateScrollRegions( self ):
        "Update graph and scale scroll regions."
        ofs = 20
        height = self.gheight + ofs
        self.graph.configure( scrollregion=( 0, -ofs,
                              self.xpos * self.barwidth, height ) )
        self.scale.configure( scrollregion=( 0, -ofs, 0, height ) )

    def yview( self, *args ):
        "Scroll both scale and graph."
        self.graph.yview( *args )
        self.scale.yview( *args )

    def createWidgets( self ):
        "Create initial widget set."

        # Objects
        title = Label( self, text='Bandwidth (Gb/s)', bg=self.bg )
        width = self.gwidth
        height = self.gheight
        scale = self.createScale()
        graph = Canvas( self, width=width, height=height, background=self.bg)
        xbar = Scrollbar( self, orient='horizontal', command=graph.xview )
        ybar = Scrollbar( self, orient='vertical', command=self.yview )
        graph.configure( xscrollcommand=xbar.set, yscrollcommand=ybar.set,
                         scrollregion=(0, 0, width, height ) )
        scale.configure( yscrollcommand=ybar.set )

        # Layout
        title.grid( row=0, columnspan=3, sticky='new')
        scale.grid( row=1, column=0, sticky='nsew' )
        graph.grid( row=1, column=1, sticky='nsew' )
        ybar.grid( row=1, column=2, sticky='ns' )
        xbar.grid( row=2, column=0, columnspan=2, sticky='ew' )
        self.rowconfigure( 1, weight=1 )
        self.columnconfigure( 1, weight=1 )
        return title, scale, graph

    def addBar( self, yval ):
        "Add a new bar to our graph."
        percent = yval / self.ymax
        c = self.graph
        x0 = self.xpos * self.barwidth
        x1 = x0 + self.barwidth
        y0 = self.gheight
        y1 = ( 1 - percent ) * self.gheight
        c.create_rectangle( x0, y0, x1, y1, fill='green' )
        self.xpos += 1
        self.updateScrollRegions()
        self.graph.xview( 'moveto', '1.0' )

    def clear( self ):
        "Clear graph contents."
        self.graph.delete( 'all' )
        self.xpos = 0

    def test( self ):
        "Add a bar for testing purposes."
        ms = 1000
        if self.xpos < 10:
            self.addBar( self.xpos / 10 * self.ymax  )
            self.after( ms, self.test )

    def setTitle( self, text ):
        "Set graph title"
        self.title.configure( text=text, font='Helvetica 9 bold' )


class ConsoleApp( Frame ):

    #UI
    def __init__( self, nets=None, parent=None, width=3 ):
        Frame.__init__( self, parent )

        #data structure
        self.netManager = NetManager()
        self.dataManager = DataManager()
        self.scheduler = Scheduler()
        self.hosts = []
        # UI
        self.top = self.winfo_toplevel()
        self.top.title( 'Mininet节点调度子系统' )
        self.createMenuBar()
        self.menubar = self.createFramBar()
        self.createCfram()
        cleanUpScreens()
        self.pack( expand=True, fill='both' )

    def createCfram(self,width=4):
        cframe = self.cframe = Frame( self )
        self.consoles = {}
        titles = {
            'hosts': 'Host',
            'switches': 'Switch',
            'controllers': 'Controller'
        }
        for name in titles:
            nodes = getattr( self.netManager.getNet(), name)
            frame, consoles = self.createConsoles(cframe, nodes, width, titles[ name ] )
            if name == 'hosts':
                self.hosts = consoles
            self.consoles[ name ] = Object( frame=frame, consoles=consoles )
        self.selected = None
        self.select( 'hosts' )
        self.cframe.pack( expand=True, fill='both' )
        cleanUpScreens()
        # Close window gracefully
        Wm.wm_protocol( self.top, name='WM_DELETE_WINDOW', func=self.quit )
        # Initialize graph
        graph = Graph( cframe )
        self.consoles[ 'graph' ] = Object( frame=graph, consoles=[ graph ] )
        self.graph = graph
        self.graphVisible = False
        self.updates = 0
        self.hostCount = len( self.consoles[ 'hosts' ].consoles )
        self.bw = 0

    def setOutputHook( self, fn=None, consoles=None ):
        "Register fn as output hook [on specific consoles.]"
        if consoles is None:
            consoles = self.consoles[ 'hosts' ].consoles
        for console in consoles:
            console.outputHook = fn

    def createConsoles( self, parent, nodes, width, title ):
        "Create a grid of consoles in a frame."
        f = Frame( parent )
        # Create consoles
        consoles = []
        index = 0
        for node in nodes:
            console = Console( f, self.netManager.net, node, title=title )
            consoles.append( console )
            row = int(index / width)
            column = int(index % width)
            console.grid( row=row, column=column, sticky='nsew' )
            index += 1
            f.rowconfigure( row, weight=1 )
            f.columnconfigure( column, weight=1 )
        return f, consoles

    def select( self, groupName ):
        "Select a group of consoles to display."
        if self.selected is not None:
            self.selected.frame.pack_forget()
        self.selected = self.consoles[ groupName ]
        self.selected.frame.pack( expand=True, fill='both' )

    def createMenuBar(self):
        menubar = Menu(self)
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label='打开', command=lambda: self.getNet(tkinter.filedialog.askopenfilename()))
        fileMenu.add_command(label='保存', command=self.writeNet)
        fileMenu.add_separator()
        fileMenu.add_command(label='退出', command=self.quit)
        menubar.add_cascade(label='文件', menu=fileMenu)
        
        # 部署是自动部署
        scheduleMenu = Menu(menubar, tearoff=0)
        scheduleMenu.add_command(label='部署主机',command = self.deployHost)
        scheduleMenu.add_command(label='部署服务',command = self.deployServer)
        menubar.add_cascade(label='部署', menu=scheduleMenu)
        
        # # 服务控制
        # serverMenu = Menu(menubar, tearoff=0)
        # menubar.add_cascade(label='服务', menu=serverMenu)
        # serverMenu.add_command(label='服务部署',command = self.deployServer)

        #拓扑管理
        topoMenu = Menu(menubar,tearoff = 0)
        topoMenu.add_command(label = '添加主机',command = lambda: self.addNode('host'))
        topoMenu.add_command(label = '添加交换机',command = lambda: self.addNode('switch'))
        topoMenu.add_command(label = '添加连接',command = self.addLink)
        topoMenu.add_separator()
        topoMenu.add_command(label = '删除节点',command = self.delNode)
        topoMenu.add_command(label = '删除连接',command = self.delLink)

        menubar.add_cascade(label= '拓扑管理', menu=topoMenu)

        
        self.top.config(menu=menubar)        

    def createFramBar( self ):
        "Create and return a menu (really button) bar."
        f = Frame( self )
        buttons = [
            ( '主机', lambda: self.select( 'hosts' ) ),
            ( '交换机', lambda: self.select( 'switches' ) ),
            ( '控制器', lambda: self.select( 'controllers' ) ),
            ( 'Graph', lambda: self.select( 'graph' ) ),
            ( 'Ping', self.ping ),
            ( 'Iperf', self.iperf ),
            ( 'Interrupt', self.stop ),
            ( 'Clear', self.clear ),
            ( 'Quit', self.quit )
        ]
        for name, cmd in buttons:
            if name == 'Graph':
                Label(f, text='   测试:    ').pack(side = 'left')
            b = Button( f, text=name, command=cmd)
            b.pack( side='left' )
        f.pack( padx=4, pady=4, fill='x' )
        return f

    #function
    def clear( self ):
        "Clear selection."
        for console in self.selected.consoles:
            console.clear()

    def waiting( self, consoles=None ):
        "Are any of our hosts waiting for output?"
        if consoles is None:
            consoles = self.consoles[ 'hosts' ].consoles
        for console in consoles:
            if console.waiting():
                return True
        return False

    def ping( self ):
        "Tell each host to ping the next one."
        consoles = self.consoles[ 'hosts' ].consoles
        if self.waiting( consoles ):
            return
        count = len( consoles )
        i = 0
        for console in consoles:
            i = ( i + 1 ) % count
            try:
                ip = consoles[ i ].node.IP()
            except:
                return
            console.sendCmd( 'ping ' + ip )

    def iperf( self ):
        "Tell each host to iperf to the next one."
        consoles = self.consoles[ 'hosts' ].consoles
        if self.waiting( consoles ):
            return
        count = len( consoles )
        #self.setOutputHook( self.updateGraph )
        for console in consoles:
            # Sometimes iperf -sD doesn't return,
            # so we run it in the background instead
           console.node.cmd( 'iperf -s &' )
        i = 0
        for console in consoles:
            i = ( i + 1 ) % count
            ip = consoles[ i ].node.IP()
            console.sendCmd( 'iperf -t 99999 -i 1 -c ' + ip )

    def updateGraph( self, _console, output ):
        "Update our graph."
        m = re.search( r'(\d+.?\d*) ([KMG]?bits)/sec', output )
        if not m:
            return
        val, units = float( m.group( 1 ) ), m.group( 2 )
        #convert to Gbps
        if units[0] == 'M':
            val *= 10 ** -3
        elif units[0] == 'K':
            val *= 10 ** -6
        elif units[0] == 'b':
            val *= 10 ** -9
        self.updates += 1
        self.bw += val
        if self.updates >= self.hostCount:
            self.graph.addBar( self.bw )
            self.bw = 0
            self.updates = 0
    
    def stop( self, wait=True ):
        "Interrupt all hosts."
        consoles = self.consoles[ 'hosts' ].consoles
        for console in consoles:
            console.handleInt()
        if wait:
            for console in consoles:
                console.waitOutput()
        self.setOutputHook( None )
        # Shut down any iperfs that might still be running
        quietRun( 'killall -9 iperf' )

    def quit( self ):
        "Stop everything and quit."
        self.stop( wait=False)
        os.system("sudo mn -c")
        Frame.quit( self )

    # data model
    def getNet(self,fileName):
        #os.system("sudo mn -c")
        self.netManager.net.stop()
        net = self.dataManager.getNet(fileName)
        if net == None:
            tkinter.messagebox.showinfo(title='提示', message='拓扑文件导入失败！')
            return
        self.netManager.net = net
        self.netManager.net.start()
        self.cframe.destroy()
        self.createCfram()
        tkinter.messagebox.showinfo(title='提示', message='拓扑文件导入成功！')

    def writeNet(self):
        def comfirm():
            self.dataManager.writeNet(fileName.get(),self.netManager.net)
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='拓扑文件保存成功！')

        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x100')
        inputWindow.title("请输入文件名")
        tkinter.Label(inputWindow,text='请输入文件名: ').place(x=10, y=10)
        fileName = tkinter.StringVar()
        entry_new_name = Entry(inputWindow, textvariable=fileName) 
        entry_new_name.place(x=130, y=10)  
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=50)

    # scheduler model
    def deployHost(self):
        def comfirm():
            if ddl.get() == '带宽优先':
                self.scheduler.bandwidth(self.netManager)
            #update window
            self.cframe.destroy()
            self.createCfram()
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='节点部署成功！')

        
        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x90')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text='调度模式: ').place(x=10, y=10)
        ddl = ttk.Combobox(inputWindow)
        ddl['value'] = ('带宽优先', '时延优先')
        ddl.current(0)
        ddl.place(x=100,y=10)  
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=50)
    
    # def deploySwitch(self):
    #     def comfirm():
    #         flag = self.scheduler.deploySwitch(self.netManager,srcNode.get(),name.get())
    #         if flag == False:
    #             tkinter.messagebox.showinfo(title='提示', message='源节点不存在！')
    #             return
    #         self.cframe.destroy()
    #         self.createCfram()
    #         inputWindow.destroy()
    #         tkinter.messagebox.showinfo(title='提示', message='节点部署成功！')

    #     inputWindow = tkinter.Toplevel(self)
    #     inputWindow.geometry('300x150')
    #     inputWindow.title("输入")
    #     tkinter.Label(inputWindow,text='节点源: ').place(x=10, y=10)
    #     srcNode = tkinter.StringVar()
    #     Entry(inputWindow, textvariable=srcNode).place(x=130, y=10)
    #     tkinter.Label(inputWindow,text='节点名字: ').place(x=10, y=50)
    #     name = tkinter.StringVar()
    #     Entry(inputWindow, textvariable=name).place(x=130, y=50) 
    #     Button(inputWindow,text='确定', command=comfirm).place(x=180,y=100)
    
    def deployServer(self):
        def comfirm():
            self.scheduler.deployServer(name.get(),self.hosts)
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='服务部署成功！')
        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x100')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text='服务名称: ').place(x=10, y=10)
        name = tkinter.StringVar()
        Entry(inputWindow, textvariable=name).place(x=130, y=10)
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=50)
        
    # topo model
    def addNode(self,type):
        def comfirm():
            if type == 'host':
                flag = self.netManager.addHost(name.get(),ip.get())
            else:
                flag = self.netManager.addSwitch(name.get())
            if flag == False:
                tkinter.messagebox.showinfo(title='提示', message= s + '名字已经存在！')
                return
            self.cframe.destroy()
            self.createCfram()
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message= s + '添加成功！')

        if type == 'host':
            s = '主机'
        else:
            s = '交换机'
        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x150')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text= s + '名字: ').place(x=10, y=10)
        name = tkinter.StringVar()
        Entry(inputWindow, textvariable=name).place(x=130, y=10)
        if type == 'host':
            tkinter.Label(inputWindow,text='主机IP: ').place(x=10, y=50)
            ip = tkinter.StringVar()
            Entry(inputWindow, textvariable=ip).place(x=130, y=50) 
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=100)

    def addLink(self):
        def comfirm():
            var = {
                'bw':bandwith.get(),
                'max_queue_size':queueSize.get(),
                'delay': delay.get(),
                'loss':loss.get(),
                'jitter': jitter.get()
            }
            params = {}
            f = False
            for k,v in var:
                if v:
                    params[k] = v
                    f = True
                else:
                    params[k] = None
            if f == False:
                params = None
            flag = self.netManager.addLink(src.get(),dest.get(),params)
            if flag == False:
                tkinter.messagebox.showinfo(title='提示', message='节点不存在！')
                return
            self.cframe.destroy()
            self.createCfram()
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='添加连接成功！')

        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x350')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text='源节点: ').place(x=10, y=10)
        src = tkinter.StringVar()
        Entry(inputWindow, textvariable=src).place(x=130, y=10)
        
        tkinter.Label(inputWindow,text='目标节点: ').place(x=10, y=50)
        dest = tkinter.StringVar()
        Entry(inputWindow, textvariable=dest).place(x=130, y=50) 
        
        tkinter.Label(inputWindow,text='带宽（Mbit）: ').place(x=10, y=90)
        bandwith = tkinter.StringVar()
        Entry(inputWindow, textvariable=bandwith).place(x=130, y=90) 
        
        tkinter.Label(inputWindow,text='时延（ms）: ').place(x=10, y=130)
        delay = tkinter.StringVar()
        Entry(inputWindow, textvariable=delay).place(x=130, y=130) 
        
        tkinter.Label(inputWindow,text='丢包率%: ').place(x=10, y=170)
        loss = tkinter.StringVar()
        Entry(inputWindow, textvariable=loss).place(x=130, y=170) 
        
        tkinter.Label(inputWindow,text='最大队列长度: ').place(x=10, y=210)
        queueSize = tkinter.StringVar()
        Entry(inputWindow, textvariable=queueSize).place(x=130, y=210)

        tkinter.Label(inputWindow,text='抖动: ').place(x=10, y=250)
        jitter = tkinter.StringVar()
        Entry(inputWindow, textvariable=jitter).place(x=130, y=250)
        
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=300)

    def delNode(self):
        def comfirm():
            flag = self.netManager.delNode(name.get())
            if flag == False:
                tkinter.messagebox.showinfo(title='提示', message='主机不存在！')
                return
            self.cframe.destroy()
            self.createCfram()
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='主机删除成功！')
        
        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x100')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text='主机名字: ').place(x=10, y=10)
        name = tkinter.StringVar()
        Entry(inputWindow, textvariable=name).place(x=130, y=10)
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=70)

    def delLink(self):
        def comfirm():
            flag = self.netManager.delLink(src.get(),dest.get())
            if flag == False:
                tkinter.messagebox.showinfo(title='提示', message='节点不存在！')
                return
            self.cframe.destroy()
            self.createCfram()
            inputWindow.destroy()
            tkinter.messagebox.showinfo(title='提示', message='连接删除成功！')

        inputWindow = tkinter.Toplevel(self)
        inputWindow.geometry('300x150')
        inputWindow.title("输入")
        tkinter.Label(inputWindow,text='源节点: ').place(x=10, y=10)
        src = tkinter.StringVar()
        Entry(inputWindow, textvariable=src).place(x=130, y=10)
        tkinter.Label(inputWindow,text='目标节点: ').place(x=10, y=50)
        dest = tkinter.StringVar()
        Entry(inputWindow, textvariable=dest).place(x=130, y=50) 
        Button(inputWindow,text='确定', command=comfirm).place(x=180,y=100)
# Make it easier to construct and assign objects

def assign( obj, **kwargs ):
    "Set a bunch of fields in an object."
    obj.__dict__.update( kwargs )

class Object( object ):
    "Generic object you can stuff junk into."
    def __init__( self, **kwargs ):
        assign( self, **kwargs )


if __name__ == '__main__':
    setLogLevel( 'info' )
    app = ConsoleApp(width=4 )
    app.mainloop()
