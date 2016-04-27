'''A class to create a socket that communicates to LabView to control Pressure Pain device'''

# Written by Vaida Rimeikyte 12/10/2015

import socket #for UDP communication
import threading #create the class as thread sub-class, to not stop experiment while running
import time #for sleep function
import sys #for error



class PressPainCtrl(threading.Thread):
    '''Initialize PressPainCtrl with rPort = 61556, tPort=61557, to communicate with labview via socket'''
    def __init__(self, host = 'localhost', rPort = 61556, tPort=61557):
            self.rSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.rPort = rPort
            self.tPort = tPort
            self.host = host

            self.buffer = 4096
            
            self.rSock.bind((self.host,self.rPort))
            try:
                self.tSock.sendto('0005,0010,o', (self.host, self.tPort))
            except:
                raise sys.error("Could not open remote channel. Socket connection broken.")
            
            #create self as a thread
            threading.Thread.__init__(self)
            
            
            
            

    def deliver(self, inten=0, dur=0):
        
        '''Assign deliver to variable pressDat e.g., pressDat = myPressPain.deliver(inten=3,dur=10)'''
        
        if inten== 0 or dur == 0:
            print 'you must specify duration and intenesity that are above 0 \n e.g, pressDat = myPressPain.deliver(inten=3, dur=5)'
            
        #deliver the pressure of specified intensity and duration
        
        if inten<=10 and inten*dur<=80: 
            try: 
                self.tSock.sendto('%04d,%04d,t'%(inten,dur), (self.host, self.tPort))
            except:
                raise RuntimeError("Could not deliver pressure. Make sure your intensity and duration are integers")
            
        else:  raise RuntimeError("you must specify intesity < 10 and int x dur cannot be > 80")
        
    def rec(self):   
        #Get any data that has been received or wait until some is received.
        #if there is no data waiting, it will block until some is received
        #Returns pressdat 
        self.rSock.setblocking(1)
        
        msg1, addr = self.rSock.recvfrom(self.buffer) 
        if msg1.rstrip(' \r\n').endswith('.dat'): # checks if msg1 is a filename, if not there must be an error
            pressdat = msg1.rstrip(' \r\n')
        else: raise RuntimeError(msg1)
        
        msg2, addr = self.rSock.recvfrom(self.buffer) 
        if msg2.rstrip(' \r\n') != 's':
            raise RuntimeError(msg2)
            
        return pressdat
        
    def close(self, exit = False):
        """ close finishes socket sessions. Best used after each run. exit=True, shuts down labview; Not recommended"""
        

        # close the remote channel through labview
        try:
            self.tSock.sendto('0005,0010,r', (self.host, self.tPort))
        except:
            raise sys.error("Could not close remote channel. Socket connection broken.")

        if exit: 
            try:
                self.tSock.sendto('0005,0010,x', (self.host, self.tPort))
            except:
                raise sys.error("Could not exit LabVIEW. Socket connection broken.")
          
        
        #end socket sessions
        self.rSock.shutdown(1)
        self.tSock.shutdown(1)
        
        #close sockets
        
        self.rSock.close()
        self.tSock.close()
        
        
            