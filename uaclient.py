#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Cliente UA práctica final María de la Osa."""

import sys
import time
import os


def log(self, fichlog):
    with open(fichlog, 'w') as log:
        fichlog.dump(self.data, log, indent=3)

try:
    config = sys.argv[1]  # Fichero XML.
    method = sys.argv[2]  # Método SIP.
    option = sys.argv[3]  # Parámetro opcional.

    file = open(config, 'r')
    line = file.readlines()

except IndexError:
    print("Usage: python3 uaclient.py config method option")

def datetime():
    time_actual = int(time.time())
    time_actual_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time_actual))

file.close()

if __name__ == "__main__":

