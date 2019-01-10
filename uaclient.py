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
    """Creamos la clase del Log."""

    def log(operacion):
        """Función log."""
        time_actual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        logfile = open(LOGFILE, 'a')
        logfile.write(time_actual + ' ' + str(operacion))
        logfile.close()


class DocumentXML(ContentHandler):
    """Creamos la clase del documento XML."""

    def __init__(self):
        """Función principal."""
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}
        self.dicopt = {}

    def startElement(self, tag, attrs):
        """Función atributos."""
        if tag in self.dic.keys():
            for parameters in self.dic[tag]:
                self.dicopt[tag + '_' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        """Función etiquetas."""
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
        # También se puede añadir un parámetro opcional.

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



        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((PROXY, int(PROXYPORT)))

            if METHOD not in ['REGISTER', 'INVITE', 'ACK', 'BYE']:
                print('Wrong method, try REGISTER, INVITE or BYE')
                Logging.log('405 METHOD NOT ALLOWED. \r\n')

            if METHOD == 'REGISTER':
                USER = (METHOD + ' sip:' + USERNAME + ':' + PORT +
                        ' SIP/2.0\r\n' + ' Expires:' + sys.argv[3] + ' \r\n')
                print(USER)
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            ' '.join(USER.split()) + '\r\n')
                Logging.log('Received from' + PROXY + ':' + PROXYPORT +
                            ': ' + str(data) + '\r\n')
                print('Received: ', data.decode('utf-8'))
                if '401' in data.decode('utf-8'):
                    nonce = data.decode('utf-8').split('=')[-1]
                    checking = hashlib.md5()
                    checking.update(bytes(PASSWORD, 'utf-8'))
                    checking.update(bytes(nonce, 'utf-8'))
                    NEW_USER = (USER + ' Authorization: Digest response=' +
                                checking.hexdigest())
                    my_socket.send(bytes(NEW_USER + '\r\n', 'utf-8'))
                    data = my_socket.recv(1024)
                    print(NEW_USER)
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                                ': ' + ' '.join(NEW_USER.split()) + '\r\n')
                    Logging.log('Received from' + PROXY + ':' + PROXYPORT +
                                ': ' + str(data) + '\r\n')
                    print('Received: ', data.decode('utf-8'))

            if METHOD == 'INVITE':
                USER = (METHOD + ' sip:' + sys.argv[3] + ' SIP/2.0 \r\n' +
                        'Content-Type: application/sdp \r\n\r\n v=0' +
                        '\r\n o=' + USERNAME + ' ' + SERVER + '\r\n' +
                        's=misesion \r\n t=0 \r\n m=audio ' + AUDIOPORT +
                        ' RTP \r\n')
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            ' '.join(USER.split()) + '\r\n')
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024).decode('utf-8')
                Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': '
                            + str(data) + '\r\n')
                print(data)
                CLIENT = data.split('o=')[1].split(' ')[1].split('\r')[0]
                AUDIOCLIENT = data.split('audio ')[1].split(' ')[0]
                print(AUDIOCLIENT)
                if '200' in data:
                    my_socket.send(bytes('ACK sip:' + sys.argv[3] +
                                         ' SIP/2.0\r\n', 'utf-8'))
                    Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                                ' ACK sip:' + USERNAME + ' SIP/2.0\r\n')
                    print(data)
                    aEjecutar = "./mp32rtp -i " + CLIENT + " -p " +\
                                AUDIOCLIENT + " < " + AUDIOFILE
                    print('SONG SENT: ', aEjecutar)
                    os.system(aEjecutar)
                    Logging.log('Sent to ' + CLIENT + ':' + AUDIOCLIENT + ': '
                                + aEjecutar + '\r\n')

            if METHOD == 'BYE':
                USER = (METHOD + ' sip:' + USERNAME + ':' + PROXYPORT +
                        'SIP/2.0\r\n\r\n')
                my_socket.send(bytes(USER, 'utf-8'))
                data = my_socket.recv(1024).decode('utf-8')
                print(data)
                Logging.log('Received from' + PROXY + ':' + PROXYPORT + ': ' +
                            str(data))
                Logging.log('Finishing connection. \r\n')

    except ConnectionRefusedError:
        print("400 Connection Refused: Server not found")
        Logging.log('400 CONNECTION REFUSED. \r\n')
    except (IndexError or ValueError):
        print("400 BAD REQUEST.")
        Logging.log('400 BAD REQUEST. \r\n')
