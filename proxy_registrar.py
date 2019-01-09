#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socket
import sys
import time
import random
import json
import hashlib
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import Logging


class ProxyHandleXML(ContentHandler):

    def __init__(self):
        self.dictags = {'server': ['name', 'ip', 'port'], 'database': ['path',
                        'password_path'], 'log': ['path']}
        self.dataproxy = {}

    def startElement(self, tag, attrs):
        if tag in self.dictags.keys():
            print(tag)
            for parameters in self.dic[tag]:
                self.dproxy[tag + '_' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.dataproxy


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Clase Proxy"""

    def json2register(self):
        # Avanzado.
        try:
            with open(DATABASE, 'r') as jsonfile:
                self.clientes = json.load(jsonfile)
        except (FileNotFoundError, ValueError):
            self.clientes = {}


    def register2json(self):
        # Database.
        with open(DATABASE, 'w') as archivo_json:
            json.dump(self.clientes, archivo_json, sort_keys=True,
                      indent=4)

    def passwords(self):
        # Contraseñas.
        with open(DATAPASS, 'w') as PASSWORDS:
            json.dump(self.passwords, PASSWORDS, sort_keys=True,
                      indent=4)

    def abrirsocket(MESSAGE):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IP, int(PORT)))
            my_socket.send(bytes(MESSAGE, 'utf-8'))
            data = my_socket.recv(1024).decode('utf-8')
            Logging.log('Sent to ' + IP + ':' + PORT + ': ' +
                        ' '.join(MESSAGE.split()) + '\r\n')
            Logging.log('Sent to ' + IP + ':' + PORT + ': ' +
                        ' '.join(data.split()) + '\r\n')
            return data

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        self.json2register()
        self.register2json()
        self.passwords()

        CLIENT = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8')
            if not line:
                break
            info = line.split(" ")
            METHOD = info[0]
            USER1 = info[1].split(':')[1]
            # Si no hay más líneas salimos del bucle.
            if not line:
                break

            print("El cliente nos manda: \r\n" + line.decode('utf-8'))

            if METHOD != ('REGISTER', 'INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
                Logging.log('Sent to ' + CLIENT + ':' + ''' ''' +
                            ': 405 METHOD NOT ALLOWED')
                break

            if METHOD == 'REGISTER':
                C_PORT = info[1].split(':')[2]
                EXP = int(info[-1])
                TIME = int(time.time())
                Logging.log('Received from' + CLIENT + ':' + C_PORT + ': '
                            + " ".join(info) + '\r\n')

                if USER1 in self.passwords:
                    if USER1 in self.clientes:
                        if EXP == 0:
                            # Borrar un usuario.
                            del self.clientes[USER]
                            self.wfile.write(bytes('SIP/2.0 200 OK. Deleting' +
                                                   '\r\n', 'utf-8'))
                            Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
                                        ': SIP/2.0 200 OK. Deleting user.\r\n')
                        if EXP < 0:
                            self.wfile.write(bytes('400 BAD REQUEST.\r\n',
                                                   'utf-8'))
                            print('400 BAD REQUEST.')
                            Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
                                        ': 400 BAD REQUEST.\r\n')
                        else:
                            self.wfile.write(bytes('SIP/2.0 200 OK.\r\n',
                                                   'utf-8'))
                            Logging.log('Sent to' + CLIENT + ':' + C_PORT +
                                        ': SIP/2.0 200 OK.\r\n')
                    else:
                        errormens = ('401 USER NOT FOUND.\r\n WWW' +
                                     'Authenticate: Digest nonce=' +
                                     random.randint(0, 999999999999))
                        self.wfile.write(bytes(errormens, 'utf-8'))
                        nonce = data.split('=')[-1]
                        checking = hashlib.md5()
                        checking.update(bytes(self.password[USER]['password'], 'utf-8'))
                        checking.update(bytes(nonce, 'utf-8'))
                        if nonce == checking.hexdigest():
                            self.wfile.write(bytes('SIP/2.0 200 OK. Registered.' +
                                                   '\r\n', 'utf-8'))
                            Logging.log('Sent to' + CLIENT + ':' + C_PORT +
                                        ': SIP/2.0 200 OK. Registered.\r\n')
                            self.clientes[USER1] = {'IP': CLIENT, 'PORT': C_PORT,
                                                   'TIME': TIME,
                                                   'EXPIRES': (EXP + TIME)}

                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
                                ': 404 USER NOT FOUND.\r\n')

            if METHOD == 'INVITE':
                USER2 = info.split('o=')[1].split(' ')[0]
                if USER1 in self.clientes:
                    if USER2 in self.clientes:
                        Logging.log('Sent to' + IP + ':' + PORT + ':' +
                                    info + '\r\n')
                        recibo = self.abrirsocket(info)
                        self.wfile.write(bytes(recibo + '\r\n', 'utf-8'))
                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    Logging.log('Sent to:' + CLIENT + ':' + self.clientes[USER2]['PORT'] +
                                ': 404 USER NOT FOUND.\r\n')



if __name__ == '__main__':

    parser = make_parser()
    Handler = ProxyHandleXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    opt = Handler.get_tags()
    print(opt)

    SERVER = opt['server_name']
    if opt['server_ip'] == '':
        opt['server_ip'] = '127.0.0.1'
        IP = opt['server_ip']
    else:
        IP = opt['server_ip']
    PORT = opt['server_port']
    DATABASE = opt['database_path']
    DATAPASS = opt['database_password_path']
    LOGFILE = opt['log_path']

    USER = ''

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP, int(PORT)))
        my_socket.send(bytes(USER, 'utf-8'))
        data = my_socket.recv(1024)
