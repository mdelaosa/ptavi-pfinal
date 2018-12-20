#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Servidor UA práctica final María de la Osa."""

import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os

class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read()
            if not line:
                break
            method = line.decode('utf-8').split(" ")[0]
            print("THE CLIENT SENT: " + line.decode('utf-8'))
            if method == 'INVITE':
                self.wfile.write(b"SIP/2.0 100 TRYING...\r\n\r\n" +
                                 b"SIP/2.0 100 RINGING...\r\n\r\n" +
                                 b"SIP/2.0 200 OK...\r\n\r\n")
                break
            if method == 'ACK':
                song = 'mp32rtp -i 127.0.0.1 -p 23032 < ' + sys.argv[3]
                print('SONG', song)
                os.system(song)
                break
            if method == 'BYE':
                self.wfile.write(b"SIP/2.0 200 OK FINISHIN CONNECTION")
                print('FINISHING CONNECTION WITH THE CLIENT')
                break
            if method != ('INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
                break
            else:
                self.wfile.write(b"SIP/2.0 400 BAD REQUEST\r\n\r\n")
                break