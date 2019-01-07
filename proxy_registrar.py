#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socket
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import DocumentXML

if __name__ == '__main__':

#MODIFICAR
    parser = make_parser()
    Handler = DocumentXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    data = Handler.get_tags()
    print(data)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((PROXY, int(PROXYPORT)))
        my_socket.send(bytes(USER, 'utf-8'))
        data = my_socket.recv(1024)

