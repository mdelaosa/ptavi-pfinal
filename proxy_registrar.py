#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socket
import sys
import time
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
            for parameters in self.dictags[tag]:
                self.dataproxy[tag + ' ' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.dataproxy


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Clase Proxy"""

    def json2register(self):
        try:
            with open(DATABASE, 'r') as jsonfile:
                self.clientes = json.load(jsonfile)
        except (FileNotFoundError, ValueError):
            self.clientes = {}

    def register2json(self):
        with open('registered.json', 'w') as archivo_json:
            json.dump(self.clientes, archivo_json, sort_keys=True,
                      indent=4)

    def deletinguser(self):
        del_client = []
        time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(int(time.time())))
        '''for client in self.clients:
                if'''

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
