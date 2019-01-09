#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Servidor UA práctica final María de la Osa."""

import sys
import socketserver
import time
from xml.sax import make_parser
from uaclient import DocumentXML
import os

class Logging:
    """Creamos la clase del Log."""

    def log(operacion):
        """Función log."""
        time_actual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        logfile = open(LOGFILE, 'a')
        logfile.write(time_actual + ' ' + str(operacion))
        logfile.close()

class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8').split(' ')
            if not line:
                break
            METHOD = line[0]
            print("THE CLIENT SENT: " + ' '.join(line))
            if METHOD == 'INVITE':
                sip_connection = ('SIP/2.0 100 TRYING...\r\n\r\n' +
                                  'SIP/2.0 180 RINGING...\r\n\r\n' +
                                  'SIP/2.0 200 OK...\r\n')
                msdp = ('Content-Type:application/sdp \r\n\r\n' +
                        'v=0 \r\n o=' + USERNAME + ' ' + SERVER + '\r\n s=misesion' +
                        '\r\n t=0 \r\n m=audio ' + AUDIOPORT + ' RTP \r\n')
                mensaje = (sip_connection + msdp)
                self.wfile.write(bytes(mensaje,'utf-8'))
                Logging.log('Sent to ' + PROXY + ':' + PROXYPORT + ': ' +
                            sip_connection + msdp)
                break
            if METHOD == 'ACK':
                aEjecutar = "./mp3rtp -i " + PROXY + " -p " + PROXYPORT + " < " +\
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
            elif METHOD != ('INVITE', 'ACK', 'BYE'):
                self.wfile.write(b"SENT: SIP/2.0 405 METHOD NOT ALLOWED\r\n\r\n")
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
