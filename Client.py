import socket
import sys
import tokenize
from optparse import OptionParser

def parseArg():
    parser = OptionParser()

    parser.add_option("-p", "--port", dest="Port", help="Port Number to Listen Up", metavar="PORT_NUM",type="int")
    parser.add_option("-u", "--url", dest="url", help="Url to access")

    (options, args) = parser.parse_args()

    if options.Port == None:
        options.Port = 80
    elif options.url == None: 
        raise RuntimeError("Parameter -u problem")
    return (options, args)

def getIP(d):
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        # fail gracefully!
        return False

def tokenString(url):
    tokens = url.split('/')
    a = getIP(tokens[0])
    if len(tokens) == 1:
        tokens.append("") 
    if a:
        url = tokens[0]
        tokens[0] = a
        return tokens,url
    else:
        raise RuntimeError("Not an Valid Address")

def msgCreator(tokens,host):
    msg = "GET /"
    tokens.pop(0)
    if len(tokens) > 0:
        for token in tokens:
            if token == '':
                msg = ''.join(msg+'/')
                continue
            msg = ''.join(msg+token)
            msg = ''.join(msg+'/')

    msg = msg[:-1]
    msg = ''.join(msg+' HTTP/1.1\n')
    msg = ''.join(msg+'Host: www.'+host+'\n')
    msg = ''.join(msg+'Connection: close\n')
    msg = ''.join(msg+'User-agent: Mozilla/5.0\n\n')
    return msg

def getFile(socketTCP):
    rec = socketTCP.recv(1024)
    msg = rec    
    while rec:
        #f.write(rec)
        rec = socketTCP.recv(1024)
        msg = msg + rec    
    index = msg.find('\n')
    response = msg[:index+1]
    msg = msg[index+1:]
    response = response[:-1]
    response = response.split(' ')
    if(response[1] == "200"):
        while True:
            index = msg.find('\n')
            msg = msg[index+1:]
            if(index == 0) or (index == 1):
                break

        f = open("saida",'w')
        f.write(msg)
        f.close()
    else:
        print "Got a " + response[1]        

(options, args) = parseArg()

#tokenize url
tokens,url = tokenString(options.url)

#Get the port
PORT = options.Port

socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = tokens[0].replace("\"","")
HOST = HOST.replace("'","")

dest = (HOST, PORT)

if url != 'not-site':
    msg = msgCreator(tokens,url)

socketTCP.connect(dest)

socketTCP.send(msg)

getFile(socketTCP)

