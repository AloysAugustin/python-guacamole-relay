
import logging
import socket

from GuacamoleSocket import GuacamoleSocket
from guacamole.io import ReaderGuacamoleReader, WriterGuacamoleWriter

class InetGuacamoleSocket(GuacamoleSocket):
    SOCKET_TIMEOUT = 15000

    def __init__(self, host, port):
        try:
            logging.debug('Connecting to guacd at %s:%d', host, port)
            self.socket = socket.create_connection((host, port), timeout=InetGuacamoleSocket.SOCKET_TIMEOUT)
            self.reader = ReaderGuacamoleReader(self.socket)
            self.writer = WriterGuacamoleWriter(self.socket)
        except socket.timeout:
            raise

    def close(self):
        try:
            logger.debug('Closing connection to guacd.')
            self.socket.close()
        except:
            raise

    def getReader(self):
        return self.reader

    def getWriter(self):
        return self.writer

    def isOpen(self):
        # TODO
        return "maybe"
