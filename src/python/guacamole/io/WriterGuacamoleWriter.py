
from GuacamoleWriter import GuacamoleWriter

class WriterGuacamoleWriter(GuacamoleWriter):
    def __init__(self, socket):
        self.socket = socket

    def write(self, chunk):
        if self.socket.sendall(chunk):
            raise Exception("Send error")

    def writeInstruction(self, instruction):
        self.write(str(instruction))

