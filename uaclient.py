#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
import time
import os


def log(self, fichlog):
    with open(fichlog, 'w') as log:
        fichlog.dump(self.data, log, indent=3)

try:
    config = sys.argv[1]  # Fichero XML.
    method = sys.argv[2]  # Método SIP.
    option = sys.argv[3]  # Parámetro opcional.

    file = open(config, 'r')
    line = file.readlines()

    file.close()

    if method == 'REGISTER':
        username = line[4].split('="')[1].split('"')
        #password = line[4].split('="')[2].split('"')
        expires = option
        if  :
            print('SIP/2.0 401 Unaunthorized')
            print('WWW Authenticate: Digest nonce="898989898798989898989')
    if method == 'INVITE':
        
    if method == 'BYE':


except IndexError:
    print("Usage: python3 uaclient.py config method option")

def datetime():
    time_actual = int(time.time())
    time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time_actual))



if __name__ == "__main__":

