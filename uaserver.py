#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Servidor UA práctica final María de la Osa."""

import sys
import socketserver
from xml.sax import make_parser
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
            METHOD = line[0]
            print("THE CLIENT SENT: " + line.decode('utf-8'))
            if METHOD == 'INVITE':
                sip_connection = ('SIP/2.0 100 TRYING...\r\n\r\n' +
                                  'SIP/2.0 180 RINGING...\r\n\r\n' +
                                  'SIP/2.0 200 OK...\r\n')
                msdp = ('Content-Type:application/sdp \r\n\r\n' +
                        'v=0 \r\n o=' + USERNAME + ' ' + SERVER + '\r\n s=misesion' +
                        '\r\n t=0 \r\n m=audio ' + AUDIOPORT + ' RTP \r\n')
                self.wfile.write(bytes(sip_connection) + bytes(msdp))
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            sip_connection + msdp)
                break
            if METHOD == 'ACK':
                aEjecutar = "./mp3rtp -i" + PROXY + " -p " + PROXYPORT + " < " +\
                            AUDIOFILE #Guardar dirección del otro y mandarla aquí
                print('SONG: ', aEjecutar)
                os.system(aEjecutar)
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': '
                            + aEjecutar) #Proxy no, la otra persona
                break
            if METHOD == 'BYE':
                self.wfile.write(b"SIP/2.0 200 OK FINISHING CONNECTION")
                print('FINISHING CONNECTION WITH THE CLIENT')
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                            ': FINISHING CONNECTION')
                break
            if METHOD != ('INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                            ': 405 METHOD NOT ALLOWED')
                break
            else:
                self.wfile.write(b"SIP/2.0 400 BAD REQUEST\r\n\r\n")
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT +
                            ': 400 BAD REQUEST')
                break


if __name__ == '__main__':

    parser = make_parser()
    Handler = DocumentXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    opt = Handler.get_tags()
    print(opt)

    CONFIG = sys.argv[1]  # Fichero XML.
    USERNAME = opt['account_username']
    PASSWORD = opt['account_passwd']
    SERVER = opt['uaserver_ip']
    PORT = opt['uaserver_puerto']
    AUDIOPORT = opt['rtpaudio_puerto']
    PROXY = opt['regproxy_ip']
    PROXYPORT = opt['regproxy_puerto']
    LOGFILE = opt['log_path']
    AUDIOFILE = opt['audio_path']

    serv = socketserver.UDPServer((SERVER, int(PORT)), SIPHandler)
    print("STARTING SERVER...")
    try:
        """Creamos el servidor"""
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")

    '''if (IndexError or ValueError):
        print("Usage: python3 uaserver.py CONFIG")'''
