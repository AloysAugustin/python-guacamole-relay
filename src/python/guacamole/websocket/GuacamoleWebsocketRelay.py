from gevent import monkey
monkey.patch_all()

import threading
from geventwebsocket import WebSocketApplication
import logging

from guacamole.net import SimpleGuacamoleTunnel, InetGuacamoleSocket, GuacamoleTunnel
from guacamole.protocol import ConfiguredGuacamoleSocket, GuacamoleConfiguration, GuacamoleInstruction

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
        readThread = _ReaderThread(self.ws, current_client)
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


def closeConnection(client, status):
    wsStatusCode = status.websocket_status
    guacStatusCode = str(status.guacamole_status)
    client.close(wsStatusCode, guacStatusCode)

class _ReaderThread(threading.Thread):
    def __init__(self, websocket, tunnel):
        super(_ReaderThread, self).__init__()
        self.tunnel = tunnel
        self.websocket = websocket
        self.buffer = bytearray(0)

    def run(self):
        reader = self.tunnel.acquireReader()
        self.client.send(str(GuacamoleInstruction(GuacamoleTunnel.INTERNAL_DATA_OPCODE, self.tunnel.getUUID())))
        readMessage = reader.read()
        while readMessage:
            self.buffer.extend(readMessage)
            if not reader.available() or len(self.buffer) >= GuacamoleWebsocketRelay.BUFFER_SIZE:
                self.client.send(self.buffer, False)
                logging.debug("Sending message, length %d", len(self.buffer))
                del self.buffer[:]
            readMessage = reader.read()
        closeConnection(self.client, GuacamoleStatus.SUCCESS)