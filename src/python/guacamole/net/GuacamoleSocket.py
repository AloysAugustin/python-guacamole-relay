#!/usr/bin/env python

import logging
import socket


class GuacamoleSocket(object):
    def getReader(self):
        raise Exception("Not Implemented")

    def getWriter(self):
        raise Exception("Not Implemented")

    def isOpen(self):
        raise Exception("Not Implemented")

    def close(self):
        raise Exception("Not Implemented")

class InetGuacamoleSocket(GuacamoleSocket):
    SOCKET_TIMEOUT = 15000

    def __init__(self, host, port):
        try:
            logging.debug('Connecting to guacd at %s:%d', host, port)
            self.socket = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
        except socket.timeout:
            raise

    def close(self):
        try:
            logger.debug('Closing connection to guacd.')
            self.socket.close()
        except:
            raise

    def getReader(self):
        return self.socket

    def getWriter(self):
        return self.socket

    def isOpen(self):
        return self.socket.isOpen()

