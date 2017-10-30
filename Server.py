import socket
import sys
import threading
from os import listdir
from os.path import isfile, join, isdir, exists, abspath
from optparse import OptionParser
import magic as magic

def parseArg():
    parser = OptionParser()

    parser.add_option("-p", "--port", dest="Port", help="Port Number to Listen Up", metavar="PORT_NUM",type="int")
    parser.add_option("-a", "--address", dest="addr", help="Address number to Listen Up");
    parser.add_option("-d", "--directory", dest="directory", help="Directory to share")

    (options, args) = parser.parse_args()

    if options.Port == None:
        raise RuntimeError("Parameter -p problem")
    elif options.directory == None: 
        raise RuntimeError("Parameter -d problem")
    elif options.addr == None: 
        options.addr = "127.0.0.1"
    elif not(exists(options.directory)):
        raise RuntimeError("Directory doenst exist")
    return (options, args)

def sendFile(clientsocket,url):
    test = url[:-1]
    if isfile(test):
        global mime
        url = test
        print mime.from_file(url)
        responseOK(clientsocket,"HTTP/1.1 200 OK\nContent-Type: "+mime.from_file(url)+"\n\n")
        f = open(url,'r')
        l = f.read(1024)
        while l:
            clientsocket.send(l)
            l = f.read(1024)
    elif isdir(test):
        responseOK(clientsocket,"HTTP/1.1 200 OK\nContent-Type: Directory\n\n")
        onlyfiles = []
        for f in listdir(url):
            arq = [f]
            if isfile(url+f):
                onlyfiles = onlyfiles + arq
            else:
                arq[0] = arq[0] + '/'
                onlyfiles = onlyfiles + arq
        stringFiles = ''
        for fi in onlyfiles:
            stringFiles = ''.join(stringFiles+fi+'\n')
        #print stringFiles
        clientsocket.send(stringFiles)
    else:
        response(clientsocket,"HTTP/1.1 404 Bad Request\n\n")
def responseOK(clientsocket,string):
    clientsocket.send(string)

def response(clientsocket,string):
    clientsocket.send(string)
    clientsocket.close()

def getItemUrl(item):
    tokensItem = item.split('/')
    tokensItem.pop(0)
    global Directory
    if tokensItem[0] == '' and len(tokensItem) == 1:
        return Directory+'/'
    
    else:
        msg = Directory+'/'
        if len(tokensItem) > 0:
            for token in tokensItem:
                if token == '':
                    msg = ''.join(msg+'/')
                    continue
                tokenConverted = token.replace('%20',' ')
                msg = ''.join(msg+tokenConverted)
                msg = ''.join(msg+'/')

        return msg  

def stringClean(rec):
    tokens = rec.replace('\r','')
    tokens = rec.split('\n')
    lineInstruction = tokens[0].replace('\r','')
    
    lineInstruction = lineInstruction.split(' ')
    return lineInstruction

def threadWork(clientsocket,address):
    rec = clientsocket.recv(1024)
    instru = stringClean(rec)
    if len(instru) >= 2:
        if(instru[0] == 'GET'):
            archive = getItemUrl(instru[1])
            sendFile(clientsocket,archive)
            clientsocket.close()
        else:
            response(clientsocket,"HTTP/1.1 501 Not Implemented\n\n")
    else:
        response(clientsocket,"HTTP/1.1 404 Bad Request\n\n")



(options, args) = parseArg()
mime = magic.Magic(mime=True)

#Get the port
PORT = options.Port
Directory = abspath(options.directory)
print Directory
socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

dest = (options.addr, PORT)

socketTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketTCP.bind(dest)

socketTCP.listen(5);

while True:
    (clientsocket, address) = socketTCP.accept()
    t = threading.Thread(target=threadWork, args=(clientsocket, address),)   
    t.run()   

if rec == '':
    raise RuntimeError("socket connection broker")

