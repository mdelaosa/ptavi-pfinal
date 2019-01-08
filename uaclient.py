#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import time
import hashlib
import os


'''def file(self):
    with open(CONFIG, 'w') as log:
        json.dump(self.dicxml, log, indent=3)'''


class Logging:
    def log(operacion):
        time_actual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        logfile = open(LOGFILE, 'a')
        logfile.write(time_actual + ' ' + str(operacion))
        logfile.close()


class DocumentXML(ContentHandler):

    def __init__(self):
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}
        self.dicopt = {}

    def startElement(self, tag, attrs):
        if tag in self.dic.keys():
            print(tag)
            for parameters in self.dic[tag]:
                self.dicopt[tag + '_' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.dicopt


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

        USERNAME = opt['account_username']
        PASSWORD = opt['account_passwd']
        if opt['uaserver_ip'] == '':
            opt['uaserver_ip'] = '127.0.0.1'
            SERVER = opt['uaserver_ip']
        else:
            SERVER = opt['uaserver_ip']
        PORT = opt['uaserver_puerto']
        AUDIOPORT = opt['rtpaudio_puerto']
        PROXY = opt['regproxy_ip']
        PROXYPORT = opt['regproxy_puerto']
        LOGFILE = opt['log_path']
        AUDIOFILE = opt['audio_path']

        USER = ''

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((PROXY, int(PROXYPORT)))

            if METHOD == 'REGISTER':
                USER = (METHOD + ' sip:' + USERNAME + ':' + PORT +
                        'SIP/2.0\r\n' + 'Expires:' + OPTION + '\r\n')
                print(USER)
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            ' '.join(USER.split()) + '\r\n')
                Logging.log('Received from' + PROXY + ':' + PROXYPORT +
                            ': ' + str(data) + '\r\n') #data.decode(?)
                print('Received: ', data.decode('utf-8'))
                if '401' in data.decode('utf-8'):
                    nonce = data.decode('utf-8').split('=')[-1]
                    checking = hashlib.md5()
                    checking.update(bytes(PASSWORD, 'utf-8'))
                    checking.update(bytes(nonce, 'utf-8'))
                    print('SIP/2.0 401 Unaunthorized')
                    NEW_USER = (USER + 'Authorizatin: Digest response= ' +
                                checking.hexdigest() + '\r\n')
                    print(data.decode('utf-8'))
                    my_socket.send(bytes(NEW_USER, 'utf-8'))
                    data = my_socket.recv(1024)
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                                ': ' + ' '.join(NEW_USER.split()) + '\r\n')
                    Logging.log('Received from' + PROXY + ':' + PROXYPORT +
                                ': ' + str(data) + '\r\n') #data.decode(?)
                    print('Received: ', data.decode('utf-8'))

            if METHOD == 'INVITE':
                USER = (METHOD + 'sip:' + OPTION + ' SIP/2.0 \r\n' +
                        'Content-Type: application/sdp \r\n\r\n v=0' +
                        '\r\n o=' + USERNAME + SERVER + '\r\n' +
                        's=misesion \r\n t=0 \r\n m=audio ' + AUDIOPORT +
                        'RTP \r\n')
                print(USER)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            ' '.join(USER.split()) + '\r\n')
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': '
                            + str(data) + '\r\n') #data.decode(?)
                print(data.decode('utf-8'))
                if '200' in data.decode('utf-8'):
                    my_socket.send(bytes('ACK sip:' + USERNAME +
                                         ' SIP/2.0\r\n\r\n', 'utf-8'))
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                                'ACK sip:' + USERNAME + ' SIP/2.0\r\n')
                    '''aEjecutar = "./mp3rtp -i" + SERVER + " -p " + PORT + " < "\
                                + AUDIOFILE
                    print('SONG: ', aEjecutar)
                    os.system(aEjecutar)
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': '
                                + aEjecutar + '\r\n')'''

            if METHOD == 'BYE':
                print('FINISHING CONNECTION.')
                USER = (METHOD + 'sip:' + USERNAME + ':' + PROXYPORT +
                        'SIP/2.0\r\n\r\n' + 'Expires:' + OPTION + '\r\n')
                print(USER)
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Finishing connection. \r\n')
                # (?) Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': ' + str(data))  #data.decode(?)
                print(data.decode('utf-8'))

            if METHOD != ('REGISTER' or 'INVITE' or 'BYE'):
                print('Wrong method, try REGISTER, INVITE or BYE')
                Logging.log('405 ERROR: METHOD NOT ALLOWED. \r\n')

    except ConnectionRefusedError:
        print("Connection Refused: Server not found")
        Logging.log('400 ERROR: CONNECTION REFUSED. \r\n')
    except (IndexError or ValueError):
        print("Usage: python3 uaclient.py config method option")
        Logging.log('400 ERROR: BAD REQUEST. \r\n')
