#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
import json
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import time
import os


def log(self):
    with open(CONFIG, 'w') as log:
        json.dump(self.dicxml, log, indent=3)


try:
    CONFIG = sys.argv[1]  # Fichero XML.
    METHOD = sys.argv[2]  # Método SIP.
    OPTION = sys.argv[3]  # Parámetro opcional.

except IndexError:
    print("Usage: python3 uaclient.py config method option")


def log(operacion):
    time_actual= time.strftime('%Y-%m-%d %H:%M:%S',
                               time.gmtime(time.time()))
    file.write(time_actual + ' ' + operacion)


class DocumentXML(ContentHandler):

    def __init__(self):
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}
        self.data = {}

    def startElement(self, tag, attrs):
        if tag in self.dic.keys():
            print(tag)
            for parameters in self.dic[tag]:
                self.data[tag + ' ' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.data

    if __name__ == '__main__':
        parser = make_parser()
        Handler = DocumentXML()
        parser.setContentHandler(Handler)
        parser.parse(open(sys.argv[1]))
        data = Handler.get_tags()
        print(data)

        USER = data['account username']
        PASSWORD = data['account passwd']
        SERVER = data['uaserver ip']
        PORT = data['uaserver puerto']
        AUDIOPORT = data['rtpaudio puerto']
        PROXY = data['regproxy ip']
        PROXYPORT = data['regproxy puerto']
        LOGFILE = data['log path']
        AUDIOFILE = data['audio path']

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((SERVER, int(PORT)))
            #code = (METHOD + ' sip:' + USER + ' SIP/2.0\r\n\r\n')
            #print(code)
            my_socket.send(bytes(code, 'utf-8'))
            data = my_socket.recv(1024)
            if METHOD == 'INVITE' and data.decode('utf-8').split()[-2] == '200':
                my_socket.send(bytes('ACK sip:' + USER + ' SIP/2.0\r\n\r\n',
                                     'utf-8'))
                print(data.decode('utf-8'))
            if METHOD == 'BYE':
                print('FINISHING CONNECTION.')
            if METHOD == 'REGISTER':
                # password = line[4].split('="')[2].split('"')
                USER = ('REGISTER sip:' + USER + ':' + PORT + 'SIP/2.0\r\n' + 'Expires:' + OPTION + '\r\n')
                print(USER)
                if:
                    print('SIP/2.0 401 Unaunthorized')
                    print('WWW Authenticate: Digest nonce="898989898798989898989')
                else:
                    print(user + 'Authorizarion:Digest response="123123212312321212123')

        '''with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect(PORT)
    
            if METHOD == 'REGISTER':
                #password = line[4].split('="')[2].split('"')
                USER = ('REGISTER sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n' + 'Expires:' + OPTION + '\r\n')
                print(USER)
                if  :
                    print('SIP/2.0 401 Unaunthorized')
                    print('WWW Authenticate: Digest nonce="898989898798989898989')
                else:
                    print(user + 'Authorizarion:Digest response="123123212312321212123')
        
            if METHOD == 'INVITE':
        
            if METHOD == 'BYE':
       
        file.close() '''



