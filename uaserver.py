#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Servidor UA práctica final María de la Osa."""

import sys
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import DocumentXML
from uaclient import Logging
import os


class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8')
            if not line:
                break
            METHOD = line.split(" ")[0]
            print("THE CLIENT SENT: " + line.decode('utf-8'))
            if METHOD == 'INVITE':
                sip_connection = ('SIP/2.0 100 TRYING...\r\n\r\n' +
                                  'SIP/2.0 100 RINGING...\r\n\r\n' +
                                  'SIP/2.0 200 OK...\r\n\r\n')
                msj_sdp = ('SIP/2.0 \r\n Content-Type:application/sdp \r\n\r\n v=0 \r\n o='
                           + USERNAME + SERVER + '\r\n s=misesion \r\n t=0 \r\n m=audio '
                           + AUDIOPORT + 'RTP \r\n')
                self.wfile.write(bytes(sip_connection) + bytes(msj_sdp))
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' + sip_connection + msj_sdp)
                break
            if METHOD == 'ACK':
                aEjecutar = "./mp3rtp -i" + SERVER + " -p " + PORT + " < " + AUDIOFILE
                print('SONG: ', aEjecutar)
                os.system(aEjecutar)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': AUDIO SENT')
                break
            if METHOD == 'BYE':
                self.wfile.write(b"SIP/2.0 200 OK FINISHING CONNECTION")
                print('FINISHING CONNECTION WITH THE CLIENT')
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': FINISHING CONNECTION')
                break
            if METHOD != ('INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': 405 METHOD NOT ALLOWED')
                break
            else:
                self.wfile.write(b"SIP/2.0 400 BAD REQUEST\r\n\r\n")
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': 400 BAD REQUEST')
                break


if __name__ == '__main__':

    parser = make_parser()
    Handler = DocumentXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    opt = Handler.get_tags()
    print(opt)

    try:
        CONFIG = sys.argv[1]  # Fichero XML.
        USERNAME = opt['account username']
        PASSWORD = opt['account passwd']
        SERVER = opt['uaserver ip']
        PORT = opt['uaserver puerto']
        AUDIOPORT = opt['rtpaudio puerto']
        PROXY = opt['regproxy ip']
        PROXYPORT = opt['regproxy puerto']
        LOGFILE = opt['log path']
        AUDIOFILE = opt['audio path']


    except (IndexError or ValueError):
        print("Usage: python3 uaserver.py CONFIG")