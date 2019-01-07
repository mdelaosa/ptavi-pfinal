#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import time
import os
import hashlib


'''def file(self):
    with open(CONFIG, 'w') as log:
        json.dump(self.dicxml, log, indent=3)'''


class Logging():
    def log(operacion):
        time_actual = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        logfile = open(opt['log path'], 'w')
        logfile.write(time_actual + ' ' + operacion)
        logfile.close()


class DocumentXML(ContentHandler):

    def __init__(self):
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path'],
                    'server': ['name', 'ip', 'port'],
                    'database': ['path', 'password_path']}
        self.opt = []

    def startElement(self, tag, attrs):
        if tag in self.dic.keys():
            print(tag)
            for parameters in self.dic[tag]:
                self.opt[tag + ' ' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.opt


if __name__ == '__main__':

    parser = make_parser()
    Handler = DocumentXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    opt = Handler.get_tags()
    print(opt)

    try:
        CONFIG = sys.argv[1]  # Fichero XML.
        METHOD = sys.argv[2]  # Método SIP.
        OPTION = sys.argv[3]  # Parámetro opcional.

        USERNAME = opt['account username']
        PASSWORD = opt['account passwd']
        SERVER = opt['uaserver ip']
        PORT = opt['uaserver puerto']
        AUDIOPORT = opt['rtpaudio puerto']
        PROXY = opt['regproxy ip']
        PROXYPORT = opt['regproxy puerto']
        LOGFILE = opt['log path']
        AUDIOFILE = opt['audio path']

        USER = ''

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((PROXY, int(PROXYPORT)))

            if METHOD == 'REGISTER':
                USER = (METHOD + ' sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n' +
                        'Expires:' + OPTION + '\r\n')
                print(USER)
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' + ' '.join(USER.split()))
                Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': ' + str(data)) #data.decode(?)
                print('Received: ', data.decode('utf-8'))
                if '401 Unauthorized' in data.decode('utf-8'):
                    nonce = data.decode('utf-8').split('=')[-1]
                    checking = hashlib.md5()
                    checking.update(bytes(PASSWORD, 'utf-8'))
                    checking.update(bytes(nonce, 'utf-8'))
                    print('SIP/2.0 401 Unaunthorized')
                    NEW_USER = (USER + 'Authorizatin: Digest response= ' + checking.hexdigest() + '\r\n')
                    print(data.decode('utf-8'))
                    my_socket.send(bytes(NEW_USER, 'utf-8'))
                    data = my_socket.recv(1024)
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' + ' '.join(NEW_USER.split()))
                    Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': ' + str(data)) #data.decode(?)
                    print('Received: ', data.decode('utf-8'))

            if METHOD == 'INVITE' and data.decode('utf-8').split()[-2] == '200':

                USER = (METHOD + 'sip:' + OPTION + ' SIP/2.0 \r\n Content-Type:'
                        'application/sdp \r\n\r\n v=0 \r\n o=' + USERNAME + SERVER
                        + '\r\n s=misesion \r\n t=0 \r\n m=audio ' + AUDIOPORT +
                        'RTP \r\n')
                print(USER)
                Logging.log('Sent to ' + SERVER + ':' + PORT + ': ' + ' '.join(USER.split()))
                my_socket.send(bytes(USER, 'utf-8'))
                socket_data = my_socket.recv(1024)
                Logging.log('Received from' + SERVER + ':' + PORT + ': ' + str(data)) #data.decode(?) # Modificar con proxy(?)
                print(socket_data.decode('utf-8'))
                if '200' in data.decode('utf-8'):
                    my_socket.send(bytes('ACK sip:' + USERNAME + ' SIP/2.0\r\n\r\n',
                                         'utf-8'))
                    aEjecutar = "./mp3rtp -i" + SERVER + " -p " + PORT + " < " + AUDIOFILE #proxy(?)
                    os.system(aEjecutar)
                    Logging.log('Sent to ' + SERVER + ':' + PORT + ': ' + 'ACK' + ' '.join(aEjecutar.split()))

            if METHOD == 'BYE':
                print('FINISHING CONNECTION.')
                USER = (METHOD + 'sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n\r\n'
                        + 'Expires:' + OPTION + '\r\n')
                print(USER)
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Finishing.')
                # (?) log('Received from' + PROXY + ':' + PROXYPORT + ': ' + str(data))  #data.decode(?)
                print(data.decode('utf-8'))

            if METHOD != ('REGISTER' or 'INVITE' or 'BYE'):
                print('Wrong method, try REGISTER, INVITE or BYE')

    except ConnectionRefusedError:
        print("Server not found")

    except (IndexError or ValueError):
        print("Usage: python3 uaclient.py config method option")
