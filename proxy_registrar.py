#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Proxy-Registrar práctica final María de la Osa."""
import socket
import sys
import time
from xml.sax.handler import ContentHandler


class ProxyHandle(ContentHandler):

    def __init__(self):
        self.dictags = {'server': ['name', 'ip', 'port'], 'database': ['path',
                        'password_path'], 'log': ['path']}

    def startElement(self, tag, attrs):
        if tag in self.dictags.keys():
            print(tag)
            for parameters in self.dictags[tag]:
                self.dataproxy[tag + ' ' + parameters] = attrs.get(parameters, '')

    def get_tags(self):
        return self.dataproxy

if __name__ == '__main__':

#MODIFICAR
    parser = make_parser()
    Handler = DocumentXML()
    parser.setContentHandler(Handler)
    parser.parse(open(sys.argv[1]))
    data = Handler.get_tags()
    print(data)


