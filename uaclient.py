#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
import socket
import time
import os


def log(self, fichlog):
    with open(fichlog, 'w') as log:
        json.dump(self.data, log, indent=3)


try:
    CONFIG = sys.argv[1]  # Fichero XML.
    METHOD = sys.argv[2]  # Método SIP.
    OPTION = sys.argv[3]  # Parámetro opcional.

    file = open(CONFIG, 'r')
    line = file.readlines()

    USERNAME = str(line[4].split('="')[1].split('"'))
    IP = str(line[5].split('="')[1].split('"'))
    PORT = str(line[5].split('="')[2].split('"'))
    print('USER:' + USERNAME + 'IP:' + IP + 'PORT:' + PORT)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((server, PORT))

        if METHOD == 'REGISTER':
            #password = line[4].split('="')[2].split('"')
            USER = ('REGISTER sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n' + 'Expires:' + OPTION + '\r\n')
            print(USER)
            '''if  :
                print('SIP/2.0 401 Unaunthorized')
                print('WWW Authenticate: Digest nonce="898989898798989898989')
            else:
                print(user + 'Authorizarion:Digest response="123123212312321212123')
    
        if METHOD == 'INVITE':
    
        if METHOD == 'BYE':
    '''
    file.close()
except IndexError:
    print("Usage: python3 uaclient.py config method option")

def datetime():
    time_actual = int(time.time())
    time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time_actual))


