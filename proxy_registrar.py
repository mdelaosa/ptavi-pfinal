#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socket
import sys
import time
import random
import json
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
        '''for usuario in self.clientes.keys():
            time_actual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
            time_exp = int(expires + time_actual)
            IP = self.usuarios_registrados[usuario][0]
            puerto = self.usuarios_registrados[usuario][1]
            hora_actual = self.usuarios_registrados[usuario][2]
            hora_exp = self.usuarios_registrados[usuario][3]
            jsonfile.write(SERVER + '\t' + IP + '\t' + str(PORT)
                        + '\t' + time_actual + '\t'
                        + str(hora_exp) + '\r\n')'''

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

    '''def deletinguser(self):
        del_client = []
        time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(int(time.time())))
        for client in self.clients:
                if'''

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        CLIENT = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8')
            if not line:
                break
            METHOD = line.split(" ")[0]
            # Si no hay más líneas salimos del bucle.
            if not line:
                break

            print("El cliente nos manda: \r\n" + line.decode('utf-8'))
            data = line.decode('utf-8').split("\r\n")

            if METHOD != ('INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
                Logging.log('Sent to ' + CLIENT + ':' + ''' ''' +
                            ': 405 METHOD NOT ALLOWED')
                break

            elif METHOD == 'REGISTER':
                info = line.decode('utf-8').split(" ")
                USER = info[1].split(':')[1]
                EXP = int(info[-1])
                C_PORT = info[1].split(':')[2]
                Logging.log('Received from' + CLIENT + ':' + C_PORT + ': '
                            + " ".join(info) + '\r\n')

                if USER in self.passwords:
                    if USER in self.clientes:
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

                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
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
