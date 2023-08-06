# Copyright (c) Jeroen Van Steirteghem
# See LICENSE

from twisted.internet import interfaces, protocol, reactor, tcp
from zope.interface import implements
import socket
import struct
import twunnel.logger

class SOCKS4InputProtocol(protocol.Protocol):
    implements(interfaces.IPushProducer)
    
    def __init__(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.__init__")
        
        self.configuration = None
        self.outputProtocolConnectionManager = None
        self.outputProtocol = None
        self.remoteAddress = ""
        self.remotePort = 0
        self.connectionState = 0
        self.data = ""
        self.dataState = 0
    
    def connectionMade(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.connectionMade")
        
        self.connectionState = 1
    
    def connectionLost(self, reason):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.connectionLost")
        
        self.connectionState = 2
        
        if self.outputProtocol is not None:
            self.outputProtocol.inputProtocol_connectionLost(reason)
    
    def dataReceived(self, data):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.dataReceived")
        
        self.data = self.data + data
        if self.dataState == 0:
            if self.processDataState0():
                return
        if self.dataState == 1:
            if self.processDataState1():
                return
        
    def processDataState0(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.processDataState0")
        
        data = self.data
        
        if len(data) < 8:
            return True
        
        version, method, port, address = struct.unpack("!BBHI", data[:8])
        
        data = data[8:]
        
        addressType = 0x01
        if address >= 1 and address <= 255:
            addressType = 0x03
        
        self.remotePort = port
        
        if addressType == 0x01:
            address = struct.pack("!I", address)
            address = socket.inet_ntop(socket.AF_INET, address)
            
            self.remoteAddress = address
        
        if "\x00" not in data:
            return True
        
        name, data = data.split("\x00", 1)
        
        if addressType == 0x03:
            if "\x00" not in data:
                return True
            
            address, data = data.split("\x00", 1)
            
            self.remoteAddress = address
        
        self.data = data
        
        twunnel.logger.log(2, "remoteAddress: " + self.remoteAddress)
        twunnel.logger.log(2, "remotePort: " + str(self.remotePort))
        
        if method == 0x01:
            self.outputProtocolConnectionManager.connect(self.remoteAddress, self.remotePort, self)
            
            return True
        else:
            response = struct.pack("!BBHI", 0x00, 0x5b, 0, 0)
            
            self.transport.write(response)
            self.transport.loseConnection()
            
            return True
        
    def processDataState1(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.processDataState1")
        
        self.outputProtocol.inputProtocol_dataReceived(self.data)
        
        self.data = ""
        
        return True
        
    def outputProtocol_connectionMade(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.outputProtocol_connectionMade")
        
        if self.connectionState == 1:
            self.transport.registerProducer(self.outputProtocol, True)
            
            response = struct.pack("!BBHI", 0x00, 0x5a, 0, 0)
            
            self.transport.write(response)
            
            self.outputProtocol.inputProtocol_connectionMade()
            if len(self.data) > 0:
                self.outputProtocol.inputProtocol_dataReceived(self.data)
            
            self.data = ""
            self.dataState = 1
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_connectionFailed(self, reason):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.outputProtocol_connectionFailed")
        
        if self.connectionState == 1:
            response = struct.pack("!BBHI", 0x00, 0x5b, 0, 0)
            
            self.transport.write(response)
            self.transport.loseConnection()
        
    def outputProtocol_connectionLost(self, reason):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.outputProtocol_connectionLost")
        
        if self.connectionState == 1:
            self.transport.unregisterProducer()
            self.transport.loseConnection()
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
        
    def outputProtocol_dataReceived(self, data):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.outputProtocol_dataReceived")
        
        if self.connectionState == 1:
            self.transport.write(data)
        else:
            if self.connectionState == 2:
                self.outputProtocol.inputProtocol_connectionLost(None)
    
    def pauseProducing(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.pauseProducing")
        
        if self.connectionState == 1:
            self.transport.pauseProducing()
    
    def resumeProducing(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.resumeProducing")
        
        if self.connectionState == 1:
            self.transport.resumeProducing()
    
    def stopProducing(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocol.stopProducing")
        
        if self.connectionState == 1:
            self.transport.stopProducing()

class SOCKS4InputProtocolFactory(protocol.ClientFactory):
    protocol = SOCKS4InputProtocol
    
    def __init__(self, configuration, outputProtocolConnectionManager):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocolFactory.__init__")
        
        self.configuration = configuration
        self.outputProtocolConnectionManager = outputProtocolConnectionManager
    
    def buildProtocol(self, *args, **kwargs):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocolFactory.buildProtocol")
        
        inputProtocol = protocol.ClientFactory.buildProtocol(self, *args, **kwargs)
        inputProtocol.configuration = self.configuration
        inputProtocol.outputProtocolConnectionManager = self.outputProtocolConnectionManager
        return inputProtocol
    
    def startFactory(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocolFactory.startFactory")
        
        self.outputProtocolConnectionManager.startConnectionManager()
    
    def stopFactory(self):
        twunnel.logger.log(3, "trace: SOCKS4InputProtocolFactory.stopFactory")
        
        self.outputProtocolConnectionManager.stopConnectionManager()

def createSOCKS4Port(configuration, outputProtocolConnectionManager):
    factory = SOCKS4InputProtocolFactory(configuration, outputProtocolConnectionManager)
    
    return tcp.Port(configuration["LOCAL_PROXY_SERVER"]["PORT"], factory, 50, configuration["LOCAL_PROXY_SERVER"]["ADDRESS"], reactor)