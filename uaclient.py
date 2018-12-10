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
    #METHOD = sys.argv[2]  # Método SIP.
    #OPTION = sys.argv[3]  # Parámetro opcional.


    def __init__(self):
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}
        self.dicxml = {}
        print('USER:' + USERNAME + 'IP:' + IP + 'PORT:' + PORT)
        print(self.dicxml)

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
except IndexError:
    print("Usage: python3 uaclient.py config method option")

def datetime():
    time_actual = int(time.time())
    time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time_actual))


