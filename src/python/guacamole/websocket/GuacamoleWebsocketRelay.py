from gevent import monkey
monkey.patch_all()

import threading
from geventwebsocket import WebSocketApplication
import logging

from guacamole.net.SimpleGuacamoleTunnel import SimpleGuacamoleTunnel
from guacamole.net.InetGuacamoleSocket import InetGuacamoleSocket
from guacamole.net.GuacamoleTunnel import GuacamoleTunnel
from guacamole.protocol.ConfiguredGuacamoleSocket import ConfiguredGuacamoleSocket
from guacamole.protocol.GuacamoleConfiguration import GuacamoleConfiguration
from guacamole.protocol.GuacamoleInstruction import GuacamoleInstruction

class GuacamoleWebsocketRelay(WebSocketApplication):
    BUFFER_SIZE = 8192

    def __init__(self, ws):
        super(GuacamoleWebsocketRelay, self).__init__(ws)
        logging.info("Created new GuacamoleWebSocketRelay, %s", self)

    def on_open(self):
        logging.info("Connection!")
        current_client = self.ws.handler.active_client
        guacamole_server = InetGuacamoleSocket("54.158.84.184", 4822)
        session_configuration = GuacamoleConfiguration("ssh")
        session_configuration.setParameter("hostname", "localhost")
        session_configuration.setParameter("port", "22")

        current_client.tunnel = SimpleGuacamoleTunnel(
            socket=ConfiguredGuacamoleSocket(guacamole_server, session_configuration)
        )
        readThread = _ReaderThread(self.ws, current_client.tunnel)
        readThread.start()
        logging.info("Reader thread started")

    def on_message(self, message):
        if message is None:
            return

        current_client = self.ws.handler.active_client
        if not current_client.tunnel:
            return

        tunnel = current_client.tunnel
        writer = tunnel.acquireWriter()
        writer.write(message)
        tunnel.releaseWriter()

    def on_close(self, reason):
        logging.info("Connection closed :'(") 
        current_client = self.ws.handler.active_client
        if current_client.tunnel:
            current_client.tunnel.close()


def closeConnection(websocket, status):
    wsStatusCode = status.websocket_status
    guacStatusCode = str(status.guacamole_status)
    websocket.close(wsStatusCode, guacStatusCode)

class _ReaderThread(threading.Thread):
    def __init__(self, websocket, tunnel):
        super(_ReaderThread, self).__init__()
        self.tunnel = tunnel
        self.websocket = websocket
        self.buffer = bytearray(0)

    def run(self):
        reader = self.tunnel.acquireReader()
        self.websocket.send(str(GuacamoleInstruction(GuacamoleTunnel.INTERNAL_DATA_OPCODE, self.tunnel.getUUID())))
        readMessage = reader.read()
        while readMessage:
            self.buffer.extend(readMessage)
            if not reader.available() or len(self.buffer) >= GuacamoleWebsocketRelay.BUFFER_SIZE:
                self.websocket.send(self.buffer, False)
                logging.debug("Sending message, length %d", len(self.buffer))
                del self.buffer[:]
            readMessage = reader.read()
        closeConnection(self.websocket, GuacamoleStatus.SUCCESS)
