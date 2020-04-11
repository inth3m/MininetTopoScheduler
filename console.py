import re

import tkinter
from tkinter import *

from mininet.log import setLogLevel,debug,info
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from mininet.term import makeTerms, cleanUpScreens
from mininet.util import quietRun
from mininet.cli import CLI

from topo import NetManager
from data import DataManager

class Console( Frame ):
    "A simple console on a host."

    def __init__( self, parent, net, node, height=10, width=32, title='Node' ):
        Frame.__init__( self, parent )

        self.net = net
        self.node = node
        self.prompt = node.name + '# '
        self.height, self.width, self.title = height, width, title
        # Set up widgets
        self.text = self.makeWidgets( )
        self.bindEvents()
        self.sendCmd( 'export TERM=dumb' )
    
        self.outputHook = None

    def makeWidgets( self ):
        "Make a label, a text area, and a scroll bar."

        def newTerm( net=self.net, node=self.node, title=self.title ):
            "Pop up a new terminal window for a node."
            net.terms += makeTerms( [ node ], title )
        label = Button( self, text=self.node.name, command=newTerm)
        label.pack( side='top', fill='x' )
        text = Text( self, wrap='word')
        ybar = Scrollbar( self, orient='vertical', width=7,
                          command=text.yview )
        text.configure( yscrollcommand=ybar.set )
        ip = self.node.params.get('ip')
        if ip != None:
            label_ip = Label(self, text = "节点IP:" + str(ip))
            label_ip.pack(side = 'top')
        mac = self.node.params.get('mac')
        if mac != None:
            label_mac = Label(self, text = "节点MAC地址:" + str(mac))
            label_mac.pack(side = 'top')
        
        srcNode = "links："
        for intf in self.node.intfList():
            link = intf.link
            if link:
                node1, node2 = link.intf1.node, link.intf2.node
                if node1 == self.node:
                    srcNode +=" " + node2.name
                else:
                    srcNode +=" " + node1.name
        Label(self, text = srcNode).pack(side = 'top')
        #self.serverLable.pack(side = 'top')
        
        text.pack( side='left', expand=True, fill='both' )
        ybar.pack( side='right', fill='y' )
        return text

    def bindEvents( self ):
        "Bind keyboard and file events."
        # The text widget handles regular key presses, but we
        # use special handlers for the following:
        self.text.bind( '<Return>', self.handleReturn )
        self.text.bind( '<Control-c>', self.handleInt )
        self.text.bind( '<KeyPress>', self.handleKey )
        # This is not well-documented, but it is the correct
        # way to trigger a file event handler from Tk's
        # event loop!
        self.tk.createfilehandler( self.node.stdout, READABLE,
                                   self.handleReadable )

    # We're not a terminal (yet?), so we ignore the following
    # control characters other than [\b\n\r]
    ignoreChars = re.compile( r'[\x00-\x07\x09\x0b\x0c\x0e-\x1f]+' )

    def append( self, text ):
        "Append something to our text frame."
        text = self.ignoreChars.sub( '', text )
        self.text.insert( 'end', text )
        self.text.mark_set( 'insert', 'end' )
        self.text.see( 'insert' )
        outputHook = lambda x, y: True  # make pylint happier
        if self.outputHook:
            outputHook = self.outputHook
        outputHook( self, text )

    def handleKey( self, event ):
        "If it's an interactive command, send it to the node."
        char = event.char
        if self.node.waiting:
            self.node.write( char )

    def handleReturn( self, event ):
        "Handle a carriage return."
        cmd = self.text.get( 'insert linestart', 'insert lineend' )
        # Send it immediately, if "interactive" command
        if self.node.waiting:
            self.node.write( event.char )
            return
        # Otherwise send the whole line to the shell
        pos = cmd.find( self.prompt )
        if pos >= 0:
            cmd = cmd[ pos + len( self.prompt ): ]
        self.sendCmd( cmd )

    # Callback ignores event
    def handleInt( self, _event=None ):
        "Handle control-c."
        self.node.sendInt()


    def sendCmd( self, cmd ):
        "Send a command to our node."
        if not self.node.waiting:
            self.node.sendCmd( cmd )


    def handleReadable( self, _fds, timeoutms=None ):
        "Handle file readable event."
        data = self.node.monitor( timeoutms )
        self.append( data )
        if not self.node.waiting:
            # Print prompt
            self.append( self.prompt )

    def waiting( self ):
        "Are we waiting for output?"
        return self.node.waiting

    def waitOutput( self ):
        "Wait for any remaining output."
        while self.node.waiting:
            # A bit of a trade-off here...
            self.handleReadable( self, timeoutms=1000)
            self.update()

    def clear( self ):
        "Clear all of our text."
        self.text.delete( '1.0', 'end' )
