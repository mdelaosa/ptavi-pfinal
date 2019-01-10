#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socketserver
import socket
import sys
import time
import random
import json
import hashlib
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class Logging:
    """Creamos la clase del Log."""

    def log(operacion):
        """Función log."""
        time_actual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        logfile = open(LOGFILE, 'a')
        logfile.write(time_actual + ' ' + str(operacion))
        logfile.close()


class ProxyHandleXML(ContentHandler):
    """Creamos la clase del documento XML."""

    def __init__(self):
        """Función principal."""
        self.dictags = {'server': ['name', 'ip', 'puerto'],
                        'database': ['path', 'passwdpath'],
                        'log': ['path']}
        self.dproxy = {}

    def startElement(self, tag, attrs):
        """Función atributos."""
        if tag in self.dictags.keys():
            for parameters in self.dictags[tag]:
                self.dproxy[tag + '_' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        """Función etiquetas."""
        return self.dproxy


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Clase Proxy."""

    nonce = {}

    def json2register(self):
        """Avanzado. Cogemos lo guardado anteriormetne."""
        try:
            with open(DATABASE, 'r') as clientsfile:
                self.clientes = json.load(clientsfile)
        except (FileNotFoundError or ValueError):
            self.clientes = {}

    def register2json(self):
        """Database."""
        with open(DATABASE, 'w') as archivo_json:
            json.dump(self.clientes, archivo_json, sort_keys=True,
                      indent=4)

    def passwords(self):
        """Contraseñas."""
        try:
            with open(DATAPASS, 'r') as PASSWORDS:
                self.passwds = json.load(PASSWORDS)
        except (FileNotFoundError or ValueError):
            pass

    def abrirsocket(self, mensaje, IPS, PORTS):
        """Creación del socket."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IPS, int(PORTS)))
            my_socket.send(bytes(mensaje, 'utf-8'))
            data = my_socket.recv(1024).decode('utf-8')
            Logging.log('Sent to: ' + IPS + ':' + PORTS + ': ' +
                        ' '.join(mensaje.split()) + '\r\n')
            Logging.log('Received from: ' + IPS + ':' + PORTS + ': ' +
                        ' '.join(data.split()) + '\r\n')
            return data

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        self.json2register()
        self.passwords()

        CLIENT = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8')
            if not line:
                break
            info = line.split(' ')
            METHOD = info[0]
            U1 = info[1].split(':')[1]
            # Si no hay más líneas salimos del bucle.
            if not line:
                break

            print("El cliente nos manda: \r\n" + line)

            if METHOD == 'REGISTER':
                C_PORT = info[1].split(':')[2].split('SIP')[0]
                EXP = int(info[3].split(':')[1].split('\r')[0])
                TIME = int(time.time())
                Logging.log('Received from' + CLIENT + ':' + C_PORT + ': '
                            + " ".join(info) + '\r\n')
                if len(info) == 5:
                    if U1 in self.passwds:
                        if U1 in self.clientes:
                            # Avanzada: Refuerzo de errores.
                            if EXP == 0:
                                # Borrar un usuario.
                                del self.clientes[U1]
                                self.wfile.write(bytes('SIP/2.0 200 OK. '
                                                       'Deleting.\r\n',
                                                       'utf-8'))
                                Logging.log('Sent: ' + CLIENT + ':' + C_PORT +
                                            ': SIP/2.0 200 OK. Deleting.\r\n')
                                print('Deleting user.')
                            if EXP < 0:
                                self.wfile.write(bytes('400 BAD REQUEST.\r\n',
                                                       'utf-8'))
                                print('400 BAD REQUEST.')
                                Logging.log('Sent: ' + CLIENT + ':' + C_PORT +
                                            ': 400 BAD REQUEST.\r\n')
                            if EXP > 0:
                                self.wfile.write(bytes('SIP/2.0 200 OK.\r\n',
                                                       'utf-8'))
                                Logging.log('Sent to' + CLIENT + ':' + C_PORT +
                                            ': SIP/2.0 200 OK.\r\n')
                        else:
                            self.nonce[U1] = str(random.randint(0, 9999999999))
                            error = ('401 USER NOT FOUND.\r\n WWW' +
                                     'Authenticate: Digest nonce=' +
                                     self.nonce[U1])
                            self.wfile.write(bytes(error, 'utf-8'))

                if len(info) == 8:
                    nonce_recv = info[7].split('=')[1].split('\r')[0]
                    checking = hashlib.md5()
                    checking.update(bytes(self.passwds[U1]['passwd'], 'utf-8'))
                    checking.update(bytes(self.nonce[U1], 'utf-8'))
                    if nonce_recv == checking.hexdigest() and EXP > 0:
                        self.wfile.write(bytes('SIP/2.0 200 OK. Registered.' +
                                               '\r\n', 'utf-8'))
                        Logging.log('Sent to' + CLIENT + ':' + C_PORT +
                                    ': SIP/2.0 200 OK. Registered.\r\n')
                        self.clientes[U1] = {'IP': CLIENT, 'PORT': C_PORT,
                                             'TIME': TIME,
                                             'EXPIRES': (EXP + TIME)}
                    if nonce_recv != checking.hexdigest() or EXP < 0:
                        self.wfile.write(bytes('400 BAD REQUEST.\r\n',
                                               'utf-8'))
                        print(' 400 BAD REQUEST.')
                        Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
                                    ': 400 BAD REQUEST.\r\n')
                break

            if METHOD == 'INVITE':
                U2 = info[7].split('o=')[1].split(' ')[0]
                if U1 in self.clientes:
                    if U2 in self.clientes:
                        Logging.log('Sent to' + self.clientes[U1]['IP'] + ':' +
                                    self.clientes[U1]['PORT'] + ':' +
                                    line + '\r\n')
                        rc = self.abrirsocket(line, self.clientes[U1]['IP'],
                                              self.clientes[U1]['PORT'])
                        self.wfile.write(bytes(rc + '\r\n', 'utf-8'))
                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    Logging.log('Sent to:' + CLIENT +
                                ': 404 USER NOT FOUND.\r\n')
            if METHOD == 'ACK':
                Logging.log('Sent to' + self.clientes[U1]['IP'] + ':' +
                            self.clientes[U1]['PORT'] + ':' + line + '\r\n')
                rc = self.abrirsocket(line, self.clientes[U1]['IP'],
                                      self.clientes[U1]['PORT'])

                self.wfile.write(bytes(rc + '\r\n', 'utf-8'))
                break

            if METHOD == 'BYE':
                C_PORT = info[1].split(':')[2].split('SIP')[0]
                self.wfile.write(bytes('SIP/2.0 200 OK. BYE.\r\n', 'utf-8'))
                print('Finishing connection with ' + CLIENT, C_PORT)
                Logging.log('Sent to:' + CLIENT + ':' + C_PORT +
                            ': BYE. FINISHING CONNECTION.\r\n')
                break

            if METHOD not in ['REGISTER', 'INVITE', 'ACK', 'BYE']:
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n")
                Logging.log('Sent to ' + CLIENT + ': 405 METHOD NOT ALLOWED')
                break

        self.register2json()


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
    PORT = opt['server_puerto']
    DATABASE = opt['database_path']
    DATAPASS = opt['database_passwdpath']
    LOGFILE = opt['log_path']

    serv = socketserver.UDPServer((IP, int(PORT)), SIPRegisterHandler)
    print("STARTING SERVER...")
    try:
        """Creamos el servidor"""
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
