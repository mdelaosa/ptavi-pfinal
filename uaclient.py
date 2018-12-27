#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import time


'''def file(self):
    with open(CONFIG, 'w') as log:
        json.dump(self.dicxml, log, indent=3)'''

def log(operacion):
    time_actual = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
    logfile = open(LOGFILE, 'w')
    logfile.write(time_actual + ' ' + operacion)
    logfile.close()


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

    try:
        CONFIG = sys.argv[1]  # Fichero XML.
        METHOD = sys.argv[2]  # Método SIP.
        OPTION = sys.argv[3]  # Parámetro opcional.

        USERNAME = data['account username']
        PASSWORD = data['account passwd']
        SERVER = data['uaserver ip']
        PORT = data['uaserver puerto']
        AUDIOPORT = data['rtpaudio puerto']
        PROXY = data['regproxy ip']
        PROXYPORT = data['regproxy puerto']
        LOGFILE = data['log path']
        AUDIOFILE = data['audio path']

        USER = ''

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((SERVER, int(PORT))) # Modificar con proxy
            my_socket.send(bytes(USER, 'utf-8'))
            socket_data = my_socket.recv(1024)

            if METHOD == 'REGISTER':
                USER = (METHOD + ' sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n' +
                        'Expires:' + OPTION + '\r\n')
                print(USER)
                if PASSWORD == ' ' or PASSWORD != PASSWORD.nonce: # (?)
                    print('SIP/2.0 401 Unaunthorized')
                    print('WWW Authenticate: Digest nonce="898989898798989898989')
                else:
                    print(USERNAME + 'Authorizarion:Digest response="123123212312321212123')
                    log('Sent to ' + SERVER + ':' + PORT + ': ' + ' '.join(USER.split())) #Modificar con proxy(?)
                    my_socket.send(bytes(USER, 'utf-8'))
                    socket_data = my_socket.recv(1024)
                    log('Received from' + SERVER + ':' + PORT + ': ' + str(socket_data)) #Modificar con proxy(?)
                    print(socket_data.decode('utf-8'))

            if METHOD == 'INVITE' and socket_data.decode('utf-8').split()[-2] == '200':
                my_socket.send(bytes('ACK sip:' + USERNAME + ' SIP/2.0\r\n\r\n',
                                     'utf-8'))
                USER = (METHOD + 'sip:' + OPTION + ' SIP/2.0 \r\n Content-Type:'
                        'application/sdp \r\n\r\n v=0 \r\n o=' + USERNAME + SERVER
                        + '\r\n s=misesion \r\n t=0 \r\n m=audio ' + AUDIOPORT +
                        'RTP \r\n')
                print(USER)
                log('Sent to ' + SERVER + ':' + PORT + ': ' + ' '.join(USER.split()))
                my_socket.send(bytes(USER, 'utf-8'))
                socket_data = my_socket.recv(1024)
                log('Received from' + SERVER + ':' + PORT + ': ' + str(socket_data))  # Modificar con proxy(?)
                print(socket_data.decode('utf-8'))

            if METHOD == 'BYE':
                print('FINISHING CONNECTION.')
                USER = (METHOD + 'sip:' + USERNAME + ':' + PORT + 'SIP/2.0\r\n\r\n'
                        + 'Expires:' + OPTION + '\r\n')
                print(USER)
                log('Finishing.')
                my_socket.send(bytes(USER, 'utf-8'))
                socket_data = my_socket.recv(1024)
                # log('Received from' + SERVER + ':' + PORT + ': ' + str(socket_data))  #Modificar con proxy(?)
                # print(socket_data.decode('utf-8'))

                '''if:
                    print('SIP/2.0 401 Unaunthorized')
                    print('WWW Authenticate: Digest nonce="898989898798989898989')
                else:
                    print(user + 'Authorizarion:Digest response="123123212312321212123')'''

            if METHOD != ('REGISTER' or 'INVITE' or 'BYE'):
                print('Wrong method, try REGISTER, INVITE or BYE')

    except IndexError:
        print("Usage: python3 uaclient.py config method option")

